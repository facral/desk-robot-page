#!/usr/bin/env python3
"""Upload a dummy file through the Apps Script relay with the same protocol as index.html.

No camera and no browser needed. Standard library only.

Examples
  python scripts/test_upload.py --endpoint https://script.google.com/macros/s/XXX/exec --invite AB12CD --size-mb 1
  python scripts/test_upload.py ... --size-mb 1 --fail-at 0          simulated network error before the upload
  python scripts/test_upload.py ... --size-mb 1 --lose-reply-at 0    the file is stored but the reply is "lost"
  python scripts/test_upload.py ... --negative                       bad requests must be rejected (uses no quota)

Endpoint and invite can also come from the environment: DESK_ENDPOINT, DESK_INVITE.
Each upload consumes one of the invite's MAX_USES (default 12), so use a dedicated test invite.
The uploaded file is random bytes named TEST_<id>_laptop_events.csv. Delete it from Drive afterwards.
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

CHUNK = 3 * 1024 * 1024  # same as CONFIG.CHUNK in index.html; must stay a multiple of 262144
MAX_FAILS = 6            # same retry budget as uploadBlob() in index.html
NET_ERRORS = (OSError, RuntimeError, urllib.error.URLError)


class Relay:
    def __init__(self, endpoint, timeout):
        self.endpoint, self.timeout = endpoint, timeout

    def _read(self, req):
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            raw = r.read().decode("utf-8", "replace")
        try:
            return json.loads(raw)
        except ValueError:
            head = " ".join(raw[:100].split())
            raise RuntimeError("reply is not JSON (web app access must be Anyone): " + head)

    def call(self, body):
        # text/plain POST like the page. Apps Script answers 302; urllib follows it with a GET, as browsers do.
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "text/plain;charset=utf-8"},
            method="POST",
        )
        return self._read(req)

    def get(self):
        return self._read(urllib.request.Request(self.endpoint))


def chunk_bytes(block, offset, n):
    """Deterministic bytes for a given offset, so a retried chunk is identical."""
    return (offset.to_bytes(8, "big") + block[8:n]) if n >= 8 else block[:n]


def md5_of_stream(block, size):
    h = hashlib.md5()
    for off in range(0, size, CHUNK):
        h.update(chunk_bytes(block, off, min(CHUNK, size - off)))
    return h.hexdigest()


def upload(relay, invite, size, mime, fail_at, lose_at):
    name = "TEST_%s_laptop_events.csv" % uuid.uuid4().hex[:8]
    block = os.urandom(CHUNK)
    md5 = md5_of_stream(block, size)
    n_chunks = -(-size // CHUNK)
    print("file  %s  %d bytes (%.1f MB)  %d chunks  md5 %s" % (name, size, size / 1e6, n_chunks, md5))

    init = relay.call({"action": "init", "invite": invite, "name": name, "mime": mime, "size": size})
    if not init.get("ok"):
        print("FAIL  init rejected: %s" % json.dumps(init))
        return False
    sid = init["sid"]
    print("init  ok")

    off, fails, injected, resume_ok = 0, 0, False, None
    t0 = time.time()
    while off < size:
        end, i = min(off + CHUNK, size), off // CHUNK
        expect_after_error = None
        try:
            if i == fail_at and not injected:
                injected, expect_after_error = True, off
                raise OSError("simulated network error before chunk %d" % i)
            data = base64.b64encode(chunk_bytes(block, off, end - off)).decode("ascii")
            r = relay.call({"action": "chunk", "sid": sid, "offset": off, "total": size, "data": data})
            if i == lose_at and not injected:
                injected, expect_after_error = True, end
                raise OSError("simulated lost reply after chunk %d" % i)
            if not r.get("ok"):
                raise RuntimeError("chunk rejected: %s" % json.dumps(r))
            off = int(r["received"]) if isinstance(r.get("received"), (int, float)) else end
            fails = 0
            el = time.time() - t0
            print("chunk %3d/%d  %5.1f%%  %.2f MB/s" % (i + 1, n_chunks, 100.0 * off / size, off / 1e6 / max(el, 1e-6)))
        except NET_ERRORS as e:
            fails += 1
            print("retry %d/%d  %s" % (fails, MAX_FAILS, e))
            if fails > MAX_FAILS:
                print("FAIL  gave up at offset %d" % off)
                return False
            time.sleep(min(8, fails))
            try:
                st = relay.call({"action": "status", "sid": sid, "total": size})
                if st.get("ok") and isinstance(st.get("received"), (int, float)):
                    got = int(st["received"])
                    if expect_after_error is not None:
                        resume_ok = got == expect_after_error
                        print("status after injected failure: received=%d expected=%d  %s"
                              % (got, expect_after_error, "ok" if resume_ok else "MISMATCH"))
                    off = got
            except NET_ERRORS as e2:
                print("status call failed: %s" % e2)

    el = time.time() - t0
    final = relay.call({"action": "status", "sid": sid, "total": size})
    done = bool(final.get("ok")) and int(final.get("received", -1)) == size
    print("final status: %s" % json.dumps(final))
    print("time  %.1f s  (%.2f MB/s)" % (el, size / 1e6 / max(el, 1e-6)))
    if (fail_at is not None or lose_at is not None) and resume_ok is None:
        print("WARN  the injected failure never triggered (chunk index beyond the file?)")
    ok = done and resume_ok is not False
    print("%s  upload %s" % ("PASS" if ok else "FAIL", name))
    if ok:
        print("Now check Drive: the file exists, size = %d bytes. Then delete it." % size)
    return ok


def negative(relay, invite):
    """Requests the relay must refuse. None of them reaches the per-invite use counter."""
    good = {"action": "init", "invite": invite, "name": "TEST_neg_laptop_events.csv", "mime": "text/csv", "size": 1000}
    cases = [
        ("wrong invite", dict(good, invite="not-a-real-invite"), "invite"),
        ("bad file name", dict(good, name="../evil name.csv"), "name"),
        ("bad mime", dict(good, mime="application/zip"), "mime"),
        ("size zero", dict(good, size=0), "size"),
        ("size too large", dict(good, size=10 ** 12), "size"),
        ("unknown action", {"action": "nope"}, "action"),
        ("chunk with unknown sid", {"action": "chunk", "sid": "x", "offset": 0, "total": 1, "data": "AA=="}, "sid"),
        ("status with unknown sid", {"action": "status", "sid": "x", "total": 1}, "sid"),
    ]
    all_ok = True
    try:
        g = relay.get()
        ok = g.get("ok") is True
        print("%s  GET health check -> %s" % ("PASS" if ok else "FAIL", json.dumps(g)))
        all_ok &= ok
    except Exception as e:
        print("FAIL  GET health check: %s" % e)
        all_ok = False
    for label, body, want in cases:
        try:
            r = relay.call(body)
            ok = r.get("ok") is False and r.get("error") == want
            print("%s  %-24s -> %s (want error=%s)" % ("PASS" if ok else "FAIL", label, json.dumps(r), want))
        except Exception as e:
            ok = False
            print("FAIL  %-24s -> %s" % (label, e))
        all_ok &= ok
    return all_ok


def main():
    ap = argparse.ArgumentParser(description="Test the desk-robot upload relay without a camera.")
    ap.add_argument("--endpoint", default=os.environ.get("DESK_ENDPOINT", ""), help="web app URL ending in /exec")
    ap.add_argument("--invite", default=os.environ.get("DESK_INVITE", ""), help="a valid invite code (use a test one)")
    ap.add_argument("--size-mb", type=float, default=1, help="dummy file size in MB, at most 3 (default 1)")
    ap.add_argument("--fail-at", type=int, default=None, metavar="N", help="simulate a network error before chunk N (0-based)")
    ap.add_argument("--lose-reply-at", type=int, default=None, metavar="N", help="send chunk N but ignore its reply")
    ap.add_argument("--negative", action="store_true", help="only run the rejection checks")
    ap.add_argument("--timeout", type=float, default=180, help="seconds per request (default 180)")
    a = ap.parse_args()
    if not a.endpoint or not a.invite:
        ap.error("need --endpoint and --invite (or DESK_ENDPOINT and DESK_INVITE)")
    relay = Relay(a.endpoint, a.timeout)
    if a.negative:
        ok = negative(relay, a.invite)
    else:
        size = max(1, int(a.size_mb * 1024 * 1024))
        ok = upload(relay, a.invite, size, "text/csv", a.fail_at, a.lose_reply_at)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
