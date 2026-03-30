import json
import time

from config import CORS_ALLOW_ORIGIN
from http.server import BaseHTTPRequestHandler

latest_usage = {
    "five_hour_utilization": 0,
    "seven_day_utilization": 0,
}

last_update_time = 0.0


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": CORS_ALLOW_ORIGIN,
        "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "86400",
    }


def _path_only(path):
    return path.split("?", 1)[0]


class LightpuckHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.address_string(), fmt % args))

    def do_OPTIONS(self):
        if _path_only(self.path) != "/update":
            self.send_error(404)
            return
        self.send_response(204)
        for key, val in _cors_headers().items():
            self.send_header(key, val)
        self.end_headers()

    def do_POST(self):
        if _path_only(self.path) != "/update":
            self.send_error(404)
            return
        cl = self.headers.get("Content-Length")
        if cl is None:
            self.send_response(411)
            for key, val in _cors_headers().items():
                self.send_header(key, val)
            self.end_headers()
            return
        try:
            n = int(cl)
        except ValueError:
            self.send_error(400, "Bad Content-Length")
            return
        if n > 8192:
            self.send_error(413)
            return
        raw = self.rfile.read(n) if n else b""
        try:
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("not an object")
            latest_usage.update(data)
            global last_update_time
            last_update_time = time.monotonic()
            print("Updated usage:", latest_usage)
            body = b"OK"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            for key, val in _cors_headers().items():
                self.send_header(key, val)
            self.end_headers()
            self.wfile.write(body)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            print("POST /update JSON error:", e)
            body = b"Invalid JSON"
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            for key, val in _cors_headers().items():
                self.send_header(key, val)
            self.end_headers()
            self.wfile.write(body)

    def do_GET(self):
        path = _path_only(self.path)
        if path in ("/", "/health"):
            body = b"lightpuck ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)
