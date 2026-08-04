@echo off
cd /d "C:\Users\Admin\Desktop\AI-Portal-2-main"

echo Creating virtual environment...

if not exist venv (
    py -3.11 -m venv venv
)

echo Activating environment...

call venv\Scripts\activate.bat

echo Installing requirements...

python -m pip install -r requirements.txt

echo Starting AI Portal...

python main.py

pause