# ShopSense AI Launcher Script
$ErrorActionPreference = "Continue"
$projectRoot = "e:\New folder (4)"
$storageLogs = "$projectRoot\storage\logs"

if (-not (Test-Path $storageLogs)) {
    New-Item -ItemType Directory -Force -Path $storageLogs | Out-Null
}

$py = "C:\Users\Sarat\.pyenv\pyenv-win\versions\3.10.11\python.exe"

# Stop existing processes on 8000 or 8501 if any
$conns = Get-NetTCPConnection -LocalPort 8000, 8501 -ErrorAction SilentlyContinue
foreach ($c in $conns) {
    try {
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
        Write-Host "Killed stale process on port $($c.LocalPort): PID $($c.OwningProcess)"
    } catch {}
}

Start-Sleep -Seconds 1

# Environment settings for children
$env:TRANSFORMERS_NO_TF = "1"
$env:TF_ENABLE_ONEDNN_OPTS = "0"
$env:PYTHONPATH = $projectRoot

# Launch FastAPI Backend
$backendLog = "$storageLogs\backend.log"
$backendErr = "$storageLogs\backend_err.log"

$backendProc = Start-Process -FilePath $py `
    -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $projectRoot `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErr `
    -PassThru

Write-Host "Started FastAPI (PID $($backendProc.Id))"

# Launch Streamlit Frontend
$frontendLog = "$storageLogs\frontend.log"
$frontendErr = "$storageLogs\frontend_err.log"

$frontendProc = Start-Process -FilePath $py `
    -ArgumentList "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true" `
    -WorkingDirectory $projectRoot `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendErr `
    -PassThru

Write-Host "Started Streamlit (PID $($frontendProc.Id))"

# Wait for startup
Start-Sleep -Seconds 8

# Check open ports
$activeConns = Get-NetTCPConnection -LocalPort 8000, 8501 -ErrorAction SilentlyContinue | Select-Object LocalAddress, LocalPort, State, OwningProcess
$activeConns | Format-Table -AutoSize
