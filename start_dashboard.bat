@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
  set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
) else if exist "venv\Scripts\activate.bat" (
  call "venv\Scripts\activate.bat"
  set "PYTHON_EXE=%CD%\venv\Scripts\python.exe"
) else (
  echo No virtual environment found.
  echo Create one and install dependencies:
  echo python -m venv .venv
  echo .venv\Scripts\activate
  echo pip install -r requirements.txt
  pause
  exit /b 1
)

echo Starting AI Business Analytics Dashboard...
echo.
echo Login page:
echo http://127.0.0.1:8002/app/login.html
echo.
echo Keep this window open while using the dashboard.
echo Press Ctrl+C to stop the server.
echo.

start "" "http://127.0.0.1:8002/app/login.html"
"%PYTHON_EXE%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8002

pause
