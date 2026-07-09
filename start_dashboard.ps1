Set-Location -Path $PSScriptRoot

$appUrl = "http://127.0.0.1:8002/app/login.html"
$healthUrl = "http://127.0.0.1:8002/health"
$pidFile = Join-Path $PSScriptRoot "uvicorn.pid"
$outLog = Join-Path $PSScriptRoot "uvicorn.out.log"
$errLog = Join-Path $PSScriptRoot "uvicorn.err.log"

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

function Test-Backend {
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Get-BackendPid {
    try {
        $connection = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8002 -State Listen -ErrorAction Stop | Select-Object -First 1
        return $connection.OwningProcess
    } catch {
        return $null
    }
}

Write-Host "Starting AI Business Analytics Dashboard..."
Write-Host ""

if (-not (Test-Backend)) {
    $server = Start-Process `
        -FilePath $pythonExe `
        -ArgumentList @("-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8002") `
        -WorkingDirectory $PSScriptRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $outLog `
        -RedirectStandardError $errLog `
        -PassThru

    Set-Content -Path $pidFile -Value $server.Id

    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if (Test-Backend) {
            $ready = $true
            break
        }
    }

    if (-not $ready) {
        Write-Host "Backend did not start. Check these logs:"
        Write-Host $outLog
        Write-Host $errLog
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Backend is already running."
    $existingPid = Get-BackendPid
    if ($existingPid) {
        Set-Content -Path $pidFile -Value $existingPid
    }
}

Write-Host "Opening website:"
Write-Host $appUrl
Write-Host ""
if (Test-Path $pidFile) {
    Write-Host "To stop the backend later:"
    Write-Host "Stop-Process -Id (Get-Content `"$pidFile`")"
} else {
    Write-Host "To stop the backend later, close the Python/Uvicorn process listening on port 8002."
}
Write-Host ""

Start-Process $appUrl
