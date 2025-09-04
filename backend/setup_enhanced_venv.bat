@echo off
echo Setting up Python virtual environment for GenAI Backend

REM Set error handling
setlocal EnableDelayedExpansion

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo Installing required packages...
echo Installing core dependencies first...
pip install fastapi uvicorn python-dotenv pydantic pydantic-settings

echo Installing from minimal requirements file...
pip install -r minimal_requirements.txt

echo Virtual environment setup complete!
echo.
echo To activate this environment in the future, run:
echo     venv\Scripts\activate.bat
echo.
echo To run the FastAPI application:
echo     uvicorn main:app --reload
echo.
