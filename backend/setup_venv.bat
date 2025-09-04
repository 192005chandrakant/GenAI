@echo off
echo Cleaning up global packages...
pip freeze > packages.txt
pip uninstall -y -r packages.txt
del packages.txt
echo Done cleaning global packages.

echo Creating new virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo Installing required packages in virtual environment...
pip install -r requirements.txt

echo Setup complete! Virtual environment is activated.
