from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

import _bootstrap  # noqa: F401


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        url = qs.get('url', [None])[0]
        if not url:
            self.send_error(400, 'Missing url')
            return
        if not (url.startswith('http://') or url.startswith('https://')):
            self.send_error(400, 'Invalid url')
            return
        try:
            req = Request(url, headers={'User-Agent': 'space-weather-sentinel/1.0'})
            with urlopen(req, timeout=20) as resp:
                content = resp.read()
                ctype = resp.headers.get('Content-Type', 'image/jpeg')
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as exc:
            self.send_error(502, f'Image proxy failed: {exc}')
