#!/usr/bin/env python3
"""Read a <code>_features.csv from the session page and report the sign convention of yaw and pitch.

Runs locally on the numeric head-pose file only. It never touches video.

How to record the test session (open the page with #fast, demo mode is fine):
  1. When recording starts, look straight at the screen and hold still for 3 seconds.
  2. Turn your head to YOUR OWN LEFT, hold 2 seconds, come back to centre, hold 2 seconds.
  3. Same to YOUR OWN RIGHT.
  4. Tilt UP (chin up), hold 2 seconds, back to centre.
  5. Tilt DOWN (chin down), hold 2 seconds, back to centre.
Keep that order: left, right, up, down. Ignore the mirrored preview; use your body's left and right.

Usage
  python scripts/check_signs.py path/to/CODE_features.csv
  python scripts/check_signs.py path/to/CODE_features.csv --plot signs.png
"""
import argparse
import statistics
import sys

EXPECTED = ["left", "right", "up", "down"]


def load(path):
    """Return (rows, n_total). rows = list of (t_s, yaw, pitch, roll) for face=1 samples."""
    rows, n_total, header_seen = [], 0, False
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if not header_seen:
                header_seen = True
                cols = line.split(",")
                want = ["t_ms", "face", "yaw_deg", "pitch_deg", "roll_deg"]
                if cols[:5] != want:
                    sys.exit("Unexpected header: %s\nExpected it to start with: %s" % (line, ",".join(want)))
                continue
            p = line.split(",")
            n_total += 1
            if len(p) < 5 or p[1] != "1" or p[2] == "" or p[3] == "":
                continue
            try:
                rows.append((float(p[0]) / 1000.0, float(p[2]), float(p[3]), float(p[4] or 0)))
            except ValueError:
                continue
    return rows, n_total


def baseline(rows, rest_s):
    t0 = rows[0][0]
    rest = [r for r in rows if r[0] - t0 <= rest_s]
    src = rest if len(rest) >= 5 else rows
    return statistics.median(r[1] for r in src), statistics.median(r[2] for r in src)


def excursions(rows, base_yaw, base_pitch, yaw_thr, pitch_thr, min_s, gap_s):
    """Find stretches where the head is clearly turned (yaw) or tilted (pitch) away from rest."""
    def label(r):
        dy, dp = r[1] - base_yaw, r[2] - base_pitch
        sy, sp = abs(dy) / yaw_thr, abs(dp) / pitch_thr
        if sy < 1 and sp < 1:
            return None
        return ("yaw", 1 if dy > 0 else -1) if sy >= sp else ("pitch", 1 if dp > 0 else -1)

    found, cur = [], None
    for r in rows:
        lab = label(r)
        delta = (r[1] - base_yaw) if lab and lab[0] == "yaw" else (r[2] - base_pitch)
        if cur and lab == cur["lab"] and r[0] - cur["end"] <= gap_s:
            cur["end"] = r[0]
            if abs(delta) > abs(cur["peak"]):
                cur["peak"] = delta
        else:
            if cur:
                found.append(cur)
            cur = {"lab": lab, "start": r[0], "end": r[0], "peak": delta} if lab else None
    if cur:
        found.append(cur)
    return [e for e in found if e["end"] - e["start"] >= min_s]


def conclude(exc):
    """Map the first four excursions to left, right, up, down. Return (lines, ok)."""
    if len(exc) < 4:
        return ["Found %d clear movement(s), need 4 (left, right, up, down). Hold each pose longer or move further." % len(exc)], False
    a, b, c, d = exc[:4]
    shape_ok = (a["lab"][0] == "yaw" and b["lab"][0] == "yaw" and c["lab"][0] == "pitch" and d["lab"][0] == "pitch"
                and a["lab"][1] == -b["lab"][1] and c["lab"][1] == -d["lab"][1])
    if not shape_ok:
        return ["The first four movements are not yaw, opposite yaw, pitch, opposite pitch.",
                "Read the table above against what you actually did, or record again in the order left, right, up, down."], False
    sign = lambda s: "positive" if s > 0 else "negative"
    lines = [
        "Turning to your own LEFT  gives %s yaw." % sign(a["lab"][1]),
        "Turning to your own RIGHT gives %s yaw." % sign(b["lab"][1]),
        "Tilting UP   (chin up)   gives %s pitch." % sign(c["lab"][1]),
        "Tilting DOWN (chin down) gives %s pitch." % sign(d["lab"][1]),
        "",
        "Line to put in README.md and the analysis notes:",
        "  yaw > 0 = head turned to the participant's %s; pitch > 0 = head tilted %s."
        % ("left" if a["lab"][1] > 0 else "right", "up" if c["lab"][1] > 0 else "down"),
    ]
    if len(exc) > 4:
        lines.append("Note: %d extra movement(s) after the first four were ignored." % (len(exc) - 4))
    return lines, True


def plot(rows, base_yaw, base_pitch, exc, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = [r[0] for r in rows]
    fig, ax = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
    ax[0].plot(t, [r[1] - base_yaw for r in rows], lw=1)
    ax[0].set_ylabel("yaw - rest (deg)")
    ax[1].plot(t, [r[2] - base_pitch for r in rows], lw=1, color="tab:orange")
    ax[1].set_ylabel("pitch - rest (deg)")
    ax[1].set_xlabel("time since session_start (s)")
    for i, e in enumerate(exc):
        k = 0 if e["lab"][0] == "yaw" else 1
        ax[k].axvspan(e["start"], e["end"], alpha=0.2, color="gray")
        name = EXPECTED[i] if i < 4 else "?"
        ax[k].text((e["start"] + e["end"]) / 2, e["peak"], "%d %s" % (i + 1, name), ha="center", va="bottom", fontsize=8)
    for a in ax:
        a.axhline(0, color="black", lw=0.5)
        a.grid(alpha=0.3)
    fig.suptitle("Head pose relative to rest (labels assume the order left, right, up, down)")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    print("plot  saved to %s" % out)


def main():
    ap = argparse.ArgumentParser(description="Report the yaw/pitch sign convention from a features CSV.")
    ap.add_argument("csv", help="path to <code>_features.csv")
    ap.add_argument("--plot", metavar="PNG", help="also save a plot (needs matplotlib)")
    ap.add_argument("--rest-s", type=float, default=2.5, help="seconds at the start used as rest pose (default 2.5)")
    ap.add_argument("--yaw-thr", type=float, default=12, help="degrees from rest that count as a turn (default 12)")
    ap.add_argument("--pitch-thr", type=float, default=8, help="degrees from rest that count as a tilt (default 8)")
    ap.add_argument("--min-s", type=float, default=0.6, help="minimum hold time in seconds (default 0.6)")
    a = ap.parse_args()

    rows, n_total = load(a.csv)
    if len(rows) < 20:
        sys.exit("Only %d usable rows with face=1 out of %d. Check lighting and that the face check passed." % (len(rows), n_total))
    dur = rows[-1][0] - rows[0][0]
    print("rows  %d total, %d with a face (%.0f%%), %.1f s, about %.1f Hz"
          % (n_total, len(rows), 100.0 * len(rows) / max(n_total, 1), dur, n_total / max(dur, 1e-6)))
    by, bp = baseline(rows, a.rest_s)
    print("rest  yaw %.1f deg, pitch %.1f deg (median of the first %.1f s)" % (by, bp, a.rest_s))

    exc = excursions(rows, by, bp, a.yaw_thr, a.pitch_thr, a.min_s, gap_s=0.35)
    print("")
    print(" #  start_s  end_s  axis   sign  peak_deg  assumed")
    for i, e in enumerate(exc):
        print("%2d  %7.1f  %5.1f  %-5s  %s     %+7.1f  %s"
              % (i + 1, e["start"], e["end"], e["lab"][0], "+" if e["lab"][1] > 0 else "-", e["peak"],
                 EXPECTED[i] if i < 4 else "(extra)"))
    print("")
    lines, ok = conclude(exc)
    print("\n".join(lines))
    if a.plot:
        plot(rows, by, bp, exc, a.plot)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
