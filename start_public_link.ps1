Set-Location -Path $PSScriptRoot

$healthUrl = "http://127.0.0.1:8002/health"
$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
}

function Test-Backend {
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (-not (Test-Backend)) {
    if (-not (Test-Path $pythonExe)) {
        Write-Host "No virtual environment found. Install dependencies first."
        exit 1
    }

    Start-Process `
        -FilePath $pythonExe `
        -ArgumentList @("-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8002") `
        -WorkingDirectory $PSScriptRoot `
        -WindowStyle Hidden

    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Backend) {
            break
        }
    }
}

if (-not (Test-Backend)) {
    Write-Host "Backend did not start on http://127.0.0.1:8002."
    exit 1
}

$cloudflared = Join-Path $PSScriptRoot "cloudflared.exe"
if (-not (Test-Path $cloudflared)) {
    Write-Host "cloudflared.exe was not found."
    Write-Host "Download it from:"
    Write-Host "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    exit 1
}

$outLog = Join-Path $PSScriptRoot "cloudflared.out.log"
$errLog = Join-Path $PSScriptRoot "cloudflared.err.log"
Clear-Content $outLog, $errLog -ErrorAction SilentlyContinue

Start-Process `
    -FilePath $cloudflared `
    -ArgumentList @("tunnel", "--url", "http://127.0.0.1:8002") `
    -WorkingDirectory $PSScriptRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $outLog `
    -RedirectStandardError $errLog

Write-Host "Creating public link..."
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    $logText = ""
    if (Test-Path $errLog) {
        $logText = Get-Content $errLog -Raw
    }

    $match = [regex]::Match($logText, "https://[a-z0-9-]+\.trycloudflare\.com")
    if ($match.Success) {
        Write-Host ""
        Write-Host "Public website link:"
        Write-Host "$($match.Value)/app/login.html"
        Write-Host ""
        Write-Host "Keep this computer and the backend running while sharing the link."
        exit 0
    }
}

Write-Host "Tunnel started, but no URL was found yet. Check:"
Write-Host $errLog
