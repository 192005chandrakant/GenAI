@echo off
echo ====================================
echo    GenAI Frontend Build & Starter
echo ====================================
echo.

cd /d "%~dp0"

echo Step 1: Installing dependencies...
npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Building the project...
npm run build
if %errorlevel% neq 0 (
    echo Error: Failed to build project
    pause
    exit /b 1
)

echo.
echo Step 3: Starting the production server...
echo Frontend will be available at: http://localhost:3001
echo.
npm start

pause
