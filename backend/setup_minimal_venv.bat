@echo off
echo Creating new virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo Installing minimal required packages in virtual environment...
pip install -r minimal_requirements.txt

echo Setup complete! Virtual environment is activated.
