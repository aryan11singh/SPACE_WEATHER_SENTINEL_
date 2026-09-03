from http.server import BaseHTTPRequestHandler

import _bootstrap  # noqa: F401
from _helpers import send_json
from server import _fetch_aurora


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            payload = _fetch_aurora()
            send_json(self, payload)
        except Exception as exc:
            send_json(self, {error: str(exc)}, code=500)
