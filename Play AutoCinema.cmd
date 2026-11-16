@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Install the Python environment using README.md first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "tools\play_console.py" %*
pause
