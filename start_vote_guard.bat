@echo off
title VOTE-GUARD FastAPI Server
cd /d "%~dp0"
echo =================================================================
echo       VOTE-GUARD: Wireless RFID Verification Platform
echo =================================================================
echo.
echo [INFO] Starting FastAPI server on http://0.0.0.0:8000 ...
echo [INFO] Local Web Terminal: http://localhost:8000/operator.html
echo [INFO] Admin Portal:       http://localhost:8000/admin.html
echo [INFO] ESP32 Target URL:   http://<YOUR_LAN_IP>:8000
echo.
if exist "backend\.venv\Scripts\python.exe" (
    backend\.venv\Scripts\python.exe run_backend.py
) else (
    python run_backend.py
)
pause

