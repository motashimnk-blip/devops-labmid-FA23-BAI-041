@echo off
REM Starts the local report receiver on port 8080
cd /d "%~dp0"
set RECEIVER_PORT=8080
REM set RECEIVER_TOKEN=put-the-same-token-as-github-secret
python receivereceiver.py
pause
