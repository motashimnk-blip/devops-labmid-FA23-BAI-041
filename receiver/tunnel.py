"""Opens an ngrok tunnel to the local receiver so the GitHub runner can reach it.

Run:  python receiver/tunnel.py
Env:  NGROK_AUTHTOKEN (from dashboard.ngrok.com), RECEIVER_PORT (default 8080),
      NGROK_DOMAIN (optional, your free static domain so the URL never changes)
"""
import os
import time

import ngrok

port = int(os.environ.get("RECEIVER_PORT", 8080))
domain = os.environ.get("NGROK_DOMAIN") or None

options = {"authtoken_from_env": True}
if domain:
    options["domain"] = domain

listener = ngrok.forward(port, **options)
print(f"Tunnel is open: {listener.url()}  ->  http://localhost:{port}")
print(f"Put this in the GitHub secret RECEIVER_URL:  {listener.url()}/report")
print("Keep this window open. Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ngrok.disconnect()
