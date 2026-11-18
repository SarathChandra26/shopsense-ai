# Run ShopSense AI Pytest Suite
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "         Running Automated Pytest Suite           " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

python -m pytest tests -v --tb=short
