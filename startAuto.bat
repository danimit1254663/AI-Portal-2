@echo off

cd /d %~dp0

if not exist venv (
    echo Creating virtual environment...
    py -3.11 -m venv venv

    echo Activating environment...
    call venv\Scripts\activate.bat

    echo Installing requirements...
    python -m pip install -r requirements.txt
)

call venv\Scripts\activate.bat

echo Starting AI Portal...

python main.py

pause