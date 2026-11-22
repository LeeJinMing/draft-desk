"""Serve the local Draft Desk UI and evaluate a draft in memory."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from run import board_for


ROOT = Path(__file__).resolve().parent
PAGES = {
    "/": ("web/index.html", "text/html; charset=utf-8"),
    "/draft.js": ("web/draft.js", "text/javascript; charset=utf-8"),
    "/validator.js": ("web/validator.js", "text/javascript; charset=utf-8"),
    "/site.css": ("web/site.css", "text/css; charset=utf-8"),
    "/demo.json": ("synthetic-series.json", "application/json; charset=utf-8"),
}


class DraftHandler(BaseHTTPRequestHandler):
    def reply(self, code, mime, body):
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path not in PAGES:
            self.send_error(404)
            return
        file, mime = PAGES[self.path]
        self.reply(200, mime, (ROOT / file).read_bytes())

    def do_POST(self):
        if self.path != "/draft":
            self.send_error(404)
            return
        if self.headers.get_content_type() != "application/json":
            self.send_error(415)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 64_000:
                self.send_error(413)
                return
            result = board_for(json.loads(self.rfile.read(size)))
            code = 200
        except (KeyError, ValueError, UnicodeError) as error:
            result, code = {"error": str(error)}, 400
        self.reply(code, "application/json", json.dumps(result).encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5185)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), DraftHandler) as server:
        print(f"Draft Desk: http://127.0.0.1:{server.server_port}/", flush=True)
        server.serve_forever()
