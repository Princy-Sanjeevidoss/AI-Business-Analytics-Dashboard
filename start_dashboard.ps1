Set-Location -Path $PSScriptRoot

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
}

if (-not (Test-Path $pythonExe)) {
    Write-Host "No virtual environment found."
    Write-Host "Run these commands first:"
    Write-Host "python -m venv .venv"
    Write-Host ".\.venv\Scripts\Activate.ps1"
    Write-Host "pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting AI Business Analytics Dashboard..."
Write-Host ""
Write-Host "Login page:"
Write-Host "http://127.0.0.1:8002/app/login.html"
Write-Host ""
Write-Host "Keep this terminal open while using the dashboard."
Write-Host "Press Ctrl+C to stop the server."
Write-Host ""

Start-Process "http://127.0.0.1:8002/app/login.html"
& $pythonExe -m uvicorn backend.main:app --host 127.0.0.1 --port 8002
