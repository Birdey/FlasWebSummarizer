
@echo off
echo Starting Flask Application...
REM Navigate to the project directory

REM Activate the virtual environment (if applicable)
call venv\Scripts\activate

REM Run the Flask app
python app.py

REM Keep the console open
pause
