"""Sends test-report.json to the local receiver (through the ngrok tunnel).

Needs these environment variables (set as GitHub secrets):
  RECEIVER_URL    e.g. https://xxxx.ngrok-free.app/report
  RECEIVER_TOKEN  same secret token the receiver was started with
"""
import json
import os
import sys
import urllib.request

report_file = sys.argv[1] if len(sys.argv) > 1 else "test-report.json"
url = os.environ.get("RECEIVER_URL", "").strip()
token = os.environ.get("RECEIVER_TOKEN", "")

if not url:
    print("RECEIVER_URL is not set, cannot send the report.")
    sys.exit(1)

with open(report_file, "rb") as f:
    body = f.read()
json.loads(body)  # make sure it is valid JSON before sending

req = urllib.request.Request(
    url,
    data=body,
    method="POST",
    headers={
        "Content-Type": "application/json",
        "X-Report-Token": token,
        "ngrok-skip-browser-warning": "true",
        "User-Agent": "github-actions-report-sender",
    },
)

for attempt in range(1, 4):
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"Receiver answered {resp.status}: {resp.read().decode()}")
            sys.exit(0)
    except Exception as e:
        print(f"Attempt {attempt} failed: {e}")

print("Could not deliver the report to the receiver.")
sys.exit(1)
