from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import _bootstrap  # noqa: F401
from _helpers import send_json
from server import _series


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        try:
            minutes = int(qs.get(minutes, [720])[0])
        except (TypeError, ValueError):
            minutes = 720
        try:
            payload = _series(minutes)
            send_json(self, payload)
        except Exception as exc:
            send_json(self, {error: str(exc)}, code=500)
