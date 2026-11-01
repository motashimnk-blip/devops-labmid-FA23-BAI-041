@echo off
REM Opens the ngrok tunnel to the receiver. Paste your ngrok token below.
cd /d "%~dp0"
set RECEIVER_PORT=8080
set NGROK_AUTHTOKEN=PASTE_YOUR_NGROK_TOKEN_HERE
REM set NGROK_DOMAIN=your-static-domain.ngrok-free.app
python receiver	unnel.py
pause
