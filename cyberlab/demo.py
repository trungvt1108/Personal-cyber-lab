"""Harmless HTTP telemetry service; no credential store or executable payloads."""

from __future__ import annotations

import json
import logging
import signal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import FrameType
from urllib.parse import urlsplit

LOGGER = logging.getLogger("cyberlab.demo")
MARKER_PATHS = {"/admin-test", "/security-test", "/scanner-test"}


def response_for(method: str, path: str, body_size: int = 0) -> tuple[int, dict[str, object]]:
    """Return fixed lab responses; never authenticate, execute or echo user input."""
    if body_size < 0 or len(path) > 2048:
        return 400, {"error": "invalid request"}
    if body_size > 1024:
        return 413, {"error": "demo body limit is 1024 bytes"}
    try:
        route = urlsplit(path).path
    except ValueError:
        return 400, {"error": "invalid request"}
    if method == "POST" and route == "/login-demo":
        return 401, {"authenticated": False, "demo": True, "message": "No real accounts exist"}
    if method != "GET":
        return 405, {"error": "method not allowed"}
    if route == "/":
        return 200, {"service": "Personal Cyber Lab", "purpose": "educational HTTP telemetry"}
    if route == "/health":
        return 200, {"status": "ok"}
    if route == "/api/status":
        return 200, {"service": "demo", "mode": "isolated-lab", "credentials_stored": False}
    if route == "/login-demo":
        return 200, {
            "demo": True,
            "message": "POST creates a rejected demo login; send no credentials",
        }
    if route in MARKER_PATHS:
        return 200, {"demo": True, "event": "educational security marker"}
    return 404, {"error": "not found"}


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "CyberLabDemo/1.0"
    sys_version = ""

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(5)

    def _respond(self, method: str) -> None:
        try:
            body_size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            body_size = -1
        if self.headers.get("Transfer-Encoding"):
            status, data = 400, {"error": "transfer encoding is not supported"}
        else:
            status, data = response_for(method, self.path, body_size)
        # HTTP/1.0 closes the request; no input body is stored or interpreted.
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._respond("GET")

    def do_POST(self) -> None:
        self._respond("POST")

    def log_message(self, _format: str, *args: object) -> None:
        LOGGER.info(
            json.dumps(
                {
                    "event": "http_request",
                    "method": self.command,
                    "path": self.path.split("?", 1)[0][:2048],
                }
            )
        )


def _stop(_signal_number: int, _frame: FrameType | None) -> None:
    raise SystemExit(0)


def main() -> None:
    """Start only inside the target guest container, behind lab Nginx."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    server = ThreadingHTTPServer(("0.0.0.0", 8080), DemoHandler)  # noqa: S104
    server.daemon_threads = True
    signal.signal(signal.SIGTERM, _stop)
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
