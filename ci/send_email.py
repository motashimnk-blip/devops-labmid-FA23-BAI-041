"""Bonus: emails the test report after every run (pass or fail).

Settings come from GitHub secrets / environment variables:
  SMTP_SERVER (default smtp.gmail.com), SMTP_PORT (default 587),
  SMTP_USERNAME, SMTP_PASSWORD (Gmail app password), REPORT_EMAIL_TO
"""
import json
import os
import smtplib
import sys
from email.message import EmailMessage

report_file = sys.argv[1] if len(sys.argv) > 1 else "test-report.json"

server = os.environ.get("SMTP_SERVER") or "smtp.gmail.com"
port = int(os.environ.get("SMTP_PORT") or 587)
username = os.environ.get("SMTP_USERNAME", "")
password = os.environ.get("SMTP_PASSWORD", "")
to_addr = os.environ.get("REPORT_EMAIL_TO", "")

if not (username and password and to_addr):
    print("Email secrets are not set, skipping email.")
    sys.exit(0)

with open(report_file, encoding="utf-8") as f:
    report = json.load(f)

s = report["summary"]
lines = [
    f"Repository : {report['repository']}",
    f"Branch     : {report['branch']}",
    f"Commit     : {report['commit_sha']}",
    f"Run        : #{report['pipeline_run_number']} ({report['pipeline_run_url']})",
    f"Time       : {report['execution_timestamp']}",
    "",
    f"Overall result : {s['overall_status']}",
    f"Total {s['total']} | Passed {s['passed']} | Failed {s['failed']}",
    "",
    "Individual results:",
]
for t in report["tests"]:
    line = f"  [{t['result'].upper()}] {t['name']}"
    if t["failure_message"]:
        line += f"  ->  {t['failure_message']}"
    lines.append(line)

msg = EmailMessage()
msg["Subject"] = f"[{s['overall_status']}] Test report for {report['commit_sha'][:7]}"
msg["From"] = username
msg["To"] = to_addr
msg.set_content("\n".join(lines))
with open(report_file, "rb") as f:
    msg.add_attachment(f.read(), maintype="application", subtype="json",
                       filename="test-report.json")

with smtplib.SMTP(server, port, timeout=30) as smtp:
    smtp.starttls()
    smtp.login(username, password)
    smtp.send_message(msg)

print(f"Report emailed to {to_addr}")
