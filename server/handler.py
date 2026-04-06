"""JARVIS HTTP request handler."""
import http.server, json, time
from urllib.parse import parse_qs
from ..brain import agent
from ..ui.dashboard import HTML_PAGE


class JarvisHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  [{time.strftime('%H:%M:%S')}] {fmt % args}")

    def _respond(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        if content_type == "application/json":
            self.send_header("Access-Control-Allow-Origin", "*")
        if content_type.startswith("text/html"):
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else body.encode())

    def do_GET(self):
        if self.path == "/":
            self._respond(200, "text/html;charset=utf-8", HTML_PAGE)

        elif self.path == "/jobs":
            jobs = agent.get_jobs()
            self._respond(200, "application/json", json.dumps([
                {"id": j["id"], "prompt": j["prompt"][:300], "status": j["status"],
                 "result": j.get("result", ""), "started": j["started"],
                 "elapsed": j.get("elapsed", ""), "stage": j.get("stage", ""),
                 "stage_tool": j.get("stage_tool", "")}
                for j in jobs
            ]).encode())

        elif self.path == "/perms":
            self._respond(200, "application/json", b"[]")

        elif self.path == "/health":
            self._respond(200, "application/json", json.dumps({
                "status": "ok", "version": "5.1", "name": "J.A.R.V.I.S."
            }).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()

        if self.path == "/send":
            params = parse_qs(body)
            prompt = params.get("prompt", [""])[0].strip()
            if prompt:
                jid = agent.new_job(prompt)
                self._respond(200, "application/json", json.dumps({"id": jid}).encode())
                print(f"  [{time.strftime('%H:%M:%S')}] >> #{jid}: {prompt[:80]}")
            else:
                self.send_response(400)
                self.end_headers()

        elif self.path == "/stop":
            params = parse_qs(body)
            jid = int(params.get("id", ["0"])[0])
            agent.stop_job(jid)
            self._respond(200, "application/json", b'{"ok":true}')
            print(f"  [{time.strftime('%H:%M:%S')}] XX #{jid} STOPPED")

        elif self.path == "/perm":
            self._respond(200, "application/json", b'{"ok":true}')

        else:
            self.send_response(404)
            self.end_headers()
