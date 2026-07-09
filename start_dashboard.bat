@echo off
setlocal

cd /d "%~dp0"

echo Starting AI Business Analytics Dashboard...
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_dashboard.ps1"

pause
