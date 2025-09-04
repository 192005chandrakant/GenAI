@echo off
echo ====================================
echo    GenAI Frontend Development Server
echo ====================================
echo.

cd /d "%~dp0"

echo Installing dependencies...
npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:3001
echo.
npm run dev

pause
