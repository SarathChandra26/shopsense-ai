# Start ShopSense AI Platform (FastAPI Backend + Streamlit Frontend)
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "            Starting ShopSense AI                " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "FastAPI Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "FastAPI Swagger:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Streamlit Web UI: http://localhost:8501" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan

$py = "python"
if (Test-Path "C:\Users\Sarat\.pyenv\pyenv-win\versions\3.10.11\python.exe") {
    $py = "C:\Users\Sarat\.pyenv\pyenv-win\versions\3.10.11\python.exe"
}

$env:TRANSFORMERS_NO_TF = "1"
$env:TF_ENABLE_ONEDNN_OPTS = "0"
$env:PYTHONPATH = (Get-Location).Path

# Start FastAPI backend in a separate background process
$backendJob = Start-Process -FilePath $py -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000" -PassThru
Write-Host "Started FastAPI server (Process ID: $($backendJob.Id))." -ForegroundColor Yellow

# Wait 5 seconds for backend to bind port
Start-Sleep -Seconds 5

# Launch Streamlit frontend in the current console
Write-Host "Launching Streamlit dashboard..." -ForegroundColor Cyan
& $py -m streamlit run frontend/app.py --server.port 8501
