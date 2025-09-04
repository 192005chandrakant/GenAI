@echo off
echo Starting GenAI Backend Server with Dashboard...
echo.

cd /d %~dp0

echo Backend Server starting on http://127.0.0.1:8006
echo Dashboard available at: http://127.0.0.1:8006
echo API Documentation at: http://127.0.0.1:8006/docs
echo.

python main.py

pause
