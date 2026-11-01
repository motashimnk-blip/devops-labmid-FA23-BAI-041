"""Local HTTP receiver. It waits for the CI pipeline to POST the test report
and saves it as test-report.json on this computer.

Run:  python receiver/receiver.py
Env:  RECEIVER_PORT (default 8080), RECEIVER_TOKEN (optional shared secret)
"""
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("RECEIVER_PORT", 8080))
TOKEN = os.environ.get("RECEIVER_TOKEN", "")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_FILE = os.path.join(BASE_DIR, "test-report.json")
HISTORY_DIR = os.path.join(BASE_DIR, "reports")


class ReportHandler(BaseHTTPRequestHandler):

    def _reply(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # simple health check so you can test the tunnel in a browser
        self._reply(200, {"status": "receiver is running", "save_to": REPORT_FILE})

    def do_POST(self):
        if self.path != "/report":
            return self._reply(404, {"error": "use POST /report"})
        if TOKEN and self.headers.get("X-Report-Token") != TOKEN:
            return self._reply(401, {"error": "wrong or missing token"})

        length = int(self.headers.get("Content-Length", 0))
        try:
            report = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self._reply(400, {"error": "body is not valid JSON"})

        if "summary" not in report or "tests" not in report:
            return self._reply(400, {"error": "not a test report"})

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # also keep a copy of every run
        os.makedirs(HISTORY_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run = report.get("pipeline_run_number", "x")
        with open(os.path.join(HISTORY_DIR, f"run-{run}-{stamp}.json"), "w",
                  encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        s = report["summary"]
        print(f"[{stamp}] Report received: run #{run}, commit "
              f"{report.get('commit_sha', '')[:7]}, {s['overall_status']} "
              f"({s['passed']}/{s['total']} passed) -> saved to {REPORT_FILE}", flush=True)
        self._reply(200, {"saved": "test-report.json", "status": s["overall_status"]})


if __name__ == "__main__":
    print(f"Receiver listening on http://localhost:{PORT}  (POST /report)")
    print(f"Reports will be saved to {REPORT_FILE}", flush=True)
    HTTPServer(("0.0.0.0", PORT), ReportHandler).serve_forever()
