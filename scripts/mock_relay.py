#!/usr/bin/env python3
"""Local stand-in for apps-script/Code.gs, for testing test_upload.py and the page offline.

  python scripts/mock_relay.py --port 8787 --invites TEST01
  then use endpoint http://127.0.0.1:8787/exec

It applies the same checks as Code.gs (invite, name, mime, size, uses) and imitates two real
behaviours: the 302 redirect Apps Script sends after a POST, and Drive's rule that a chunk must
start exactly where the stored bytes end. Nothing is written to disk; only size and md5 are kept.
"""
import argparse
import base64
import hashlib
import json
import re
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ALLOWED_MIME = ['text/csv']
NAME_RE = re.compile(r'^[A-Za-z0-9_.-]{1,80}$')
CFG = {'invites': [], 'max_bytes': 3145728, 'max_uses': 12}
USES, SESS, PENDING = {}, {}, {}


def handle(b):
    act = b.get('action')
    if act == 'init':
        invite = str(b.get('invite') or '').strip()
        if invite not in CFG['invites']: return {'ok': False, 'error': 'invite'}
        if not NAME_RE.match(str(b.get('name') or '')): return {'ok': False, 'error': 'name'}
        if b.get('mime') not in ALLOWED_MIME: return {'ok': False, 'error': 'mime'}
        try: size = float(b.get('size'))
        except (TypeError, ValueError): size = 0
        if not size > 0 or size > CFG['max_bytes']: return {'ok': False, 'error': 'size'}
        if USES.get(invite, 0) >= CFG['max_uses']: return {'ok': False, 'error': 'uses'}
        USES[invite] = USES.get(invite, 0) + 1
        sid = str(uuid.uuid4())
        SESS[sid] = {'size': int(size), 'got': 0, 'md5': hashlib.md5(), 'name': b['name']}
        return {'ok': True, 'sid': sid}
    if act in ('chunk', 'status'):
        s = SESS.get(b.get('sid'))
        if not s: return {'ok': False, 'error': 'sid'}
        if act == 'status': return {'ok': True, 'received': s['got']}
        if b.get('total') != s['size']: return {'ok': False, 'error': 'total'}
        data = base64.b64decode(b.get('data') or '')
        if not data: return {'ok': False, 'error': 'empty'}
        if s['got'] == s['size']: return {'ok': True, 'received': s['got']}   # retry after a lost reply
        if b.get('offset') != 0: return {'ok': False, 'error': 'offset'}
        if len(data) != s['size']: return {'ok': False, 'error': 'size'}   # like Code.gs: one chunk per file
        s['md5'].update(data); s['got'] += len(data)
        if s['got'] == s['size']:
            print('DONE %s %d bytes md5 %s' % (s['name'], s['size'], s['md5'].hexdigest()), flush=True)
        return {'ok': True, 'received': s['got']}
    return {'ok': False, 'error': 'action'}


class H(BaseHTTPRequestHandler):
    def _json(self, obj):
        raw = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw)

    def do_POST(self):
        try:
            res = handle(json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0)))))
        except Exception:
            res = {'ok': False, 'error': 'server'}
        token = uuid.uuid4().hex
        PENDING[token] = res
        self.send_response(302)  # like Apps Script: the reply is fetched with a follow-up GET
        self.send_header('Location', '/result?id=' + token)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/result?id='):
            return self._json(PENDING.pop(self.path.split('=', 1)[1], {'ok': False, 'error': 'server'}))
        self._json({'ok': True, 'service': 'desk-robot-upload'})

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8787)
    ap.add_argument('--invites', default='TEST01')
    ap.add_argument('--max-uses', type=int, default=12)
    a = ap.parse_args()
    CFG['invites'] = [s.strip() for s in a.invites.split(',') if s.strip()]
    CFG['max_uses'] = a.max_uses
    print('mock relay on http://127.0.0.1:%d/exec' % a.port, flush=True)
    ThreadingHTTPServer(('127.0.0.1', a.port), H).serve_forever()
