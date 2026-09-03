import json
import os
import sys
import threading
from urllib.request import urlopen
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from server import Handler


def test_health_endpoint():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        url = f"http://{host}:{port}/api/health"
        with urlopen(url, timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        assert "uptime_sec" in payload
        assert "requests" in payload
        assert "quality" in payload
    finally:
        server.shutdown()
