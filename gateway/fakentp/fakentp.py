#!/usr/bin/env python3
"""
EchoSmart FakeNTP — HTTP-based time server for IoT devices.

Provides NTP-like time synchronization over HTTP/HTTPS for devices
that cannot reach standard NTP servers (port 123/UDP) or operate
behind restrictive firewalls.

Endpoints:
    GET  /            — HTML status page with current time
    GET  /time        — JSON time response (ISO 8601 + Unix timestamp)
    GET  /time?fmt=unix   — Plain-text Unix timestamp
    GET  /time?fmt=iso    — Plain-text ISO 8601
    GET  /health      — Health check

Usage:
    python fakentp.py                     # default: 0.0.0.0:8123
    python fakentp.py --host 0.0.0.0 --port 8123

IoT device example (ESP32 / MicroPython):
    import urequests, ujson, time
    r = urequests.get("https://ntp.echosmart.me/time")
    data = ujson.loads(r.text)
    epoch = data["unix"]

@package EchoSmart
"""

import argparse
import json
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

__version__ = "1.0.0"

# ─── Request handler ─────────────────────────────────────────────────


class FakeNTPHandler(BaseHTTPRequestHandler):
    """Serves current time over HTTP in multiple formats."""

    server_version = f"EchoSmart-FakeNTP/{__version__}"

    def do_GET(self):
        path = self.path.split("?")[0]
        query = self._parse_query()

        if path == "/time":
            self._handle_time(query)
        elif path == "/health":
            self._handle_health()
        elif path == "/":
            self._handle_index()
        else:
            self._send_error(404, "Not Found")

    def do_HEAD(self):
        """Support HEAD requests for monitoring."""
        self.do_GET()

    # ── /time ──

    def _handle_time(self, query: dict):
        now = datetime.now(timezone.utc)
        unix_ts = now.timestamp()
        iso_str = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        fmt = query.get("fmt", "json")

        if fmt == "unix":
            self._send_text(f"{unix_ts:.6f}")
        elif fmt == "iso":
            self._send_text(iso_str)
        else:
            data = {
                "unix": unix_ts,
                "iso": iso_str,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S.%f"),
                "timezone": "UTC",
                "server": "EchoSmart FakeNTP",
                "version": __version__,
            }
            self._send_json(data)

    # ── /health ──

    def _handle_health(self):
        self._send_json({"status": "ok", "service": "fakentp", "version": __version__})

    # ── / (index) ──

    def _handle_index(self):
        now = datetime.now(timezone.utc)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EchoSmart FakeNTP</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#000; color:#E0E0E0; font-family:-apple-system,BlinkMacSystemFont,
         'Segoe UI',Roboto,sans-serif; display:flex; justify-content:center;
         align-items:center; min-height:100vh; }}
  .card {{ background:#111; border-radius:16px; padding:48px; max-width:520px;
           width:90%; box-shadow:0 4px 24px rgba(0,230,118,0.08); text-align:center; }}
  h1 {{ color:#00E676; font-size:28px; margin-bottom:8px; }}
  .subtitle {{ color:#888; font-size:14px; margin-bottom:32px; }}
  .time {{ font-size:48px; font-weight:700; color:#00E676;
           font-variant-numeric:tabular-nums; margin:24px 0; }}
  .date {{ font-size:18px; color:#bbb; margin-bottom:24px; }}
  .unix {{ font-size:14px; color:#666; font-family:monospace; }}
  .api {{ margin-top:32px; text-align:left; background:#0a0a0a;
          border-radius:8px; padding:20px; }}
  .api h3 {{ color:#00E676; font-size:14px; margin-bottom:12px; }}
  .api code {{ display:block; color:#888; font-size:12px; margin:4px 0;
               font-family:monospace; }}
  .api a {{ color:#00BCD4; text-decoration:none; }}
  .badge {{ display:inline-block; background:#00E676; color:#000;
            font-size:11px; font-weight:600; padding:2px 8px;
            border-radius:4px; margin-left:8px; }}
</style>
</head>
<body>
<div class="card">
  <h1>EchoSmart FakeNTP</h1>
  <p class="subtitle">HTTP-based Time Server for IoT Devices</p>
  <div class="time" id="clock">{now.strftime('%H:%M:%S')}</div>
  <div class="date" id="date">{now.strftime('%A, %B %d, %Y')}</div>
  <div class="unix">Unix: <span id="unix">{now.timestamp():.6f}</span></div>
  <div class="api">
    <h3>API Endpoints <span class="badge">v{__version__}</span></h3>
    <code>GET <a href="/time">/time</a> — JSON (unix + iso + date)</code>
    <code>GET <a href="/time?fmt=unix">/time?fmt=unix</a> — Plain Unix timestamp</code>
    <code>GET <a href="/time?fmt=iso">/time?fmt=iso</a> — Plain ISO 8601</code>
    <code>GET <a href="/health">/health</a> — Health check</code>
  </div>
</div>
<script>
function tick() {{
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toISOString().slice(11,19);
  document.getElementById('date').textContent =
    now.toLocaleDateString('en-US',{{weekday:'long',year:'numeric',month:'long',day:'numeric'}});
  document.getElementById('unix').textContent =
    (now.getTime()/1000).toFixed(6);
}}
setInterval(tick, 200);
</script>
</body>
</html>"""
        self._send_html(html)

    # ── Helpers ──

    def _parse_query(self) -> dict:
        query = {}
        if "?" in self.path:
            qs = self.path.split("?", 1)[1]
            for pair in qs.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    query[k] = v
                else:
                    query[pair] = ""
        return query

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status: int = 200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str):
        self._send_json({"error": message}, status)

    def log_message(self, format, *args):
        """Override to use ISO timestamps in log."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"[{ts}] {self.address_string()} {format % args}")


# ─── Server entry point ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="EchoSmart FakeNTP — HTTP-based time server for IoT devices"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8123, help="Listen port (default: 8123)"
    )
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), FakeNTPHandler)
    print(f"EchoSmart FakeNTP v{__version__} listening on {args.host}:{args.port}")
    print(f"  Web UI:    http://{args.host}:{args.port}/")
    print(f"  Time API:  http://{args.host}:{args.port}/time")
    print(f"  Health:    http://{args.host}:{args.port}/health")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down FakeNTP server.")
        server.shutdown()


if __name__ == "__main__":
    main()
