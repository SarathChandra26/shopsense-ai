# Download Embedding Model & Optional Ollama Model
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "         Downloading Models for ShopSense AI      " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Download & verify SentenceTransformer model
Write-Host "1. Downloading all-MiniLM-L6-v2 embedding weights..." -ForegroundColor Yellow
python -c "import os; os.environ['TRANSFORMERS_NO_TF']='1'; from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); print('Embedding model cached successfully.')"

# 2. Check Ollama
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "2. Ollama detected. Pulling llama3.2 (3B parameter model)..." -ForegroundColor Yellow
    ollama pull llama3.2
    Write-Host "Ollama model ready." -ForegroundColor Green
} else {
    Write-Host "2. Ollama is not installed on PATH." -ForegroundColor Gray
    Write-Host "   To install Ollama on Windows, run: winget install Ollama.Ollama" -ForegroundColor Cyan
    Write-Host "   Then run: ollama run llama3.2" -ForegroundColor Cyan
}

Write-Host "Model download verification complete." -ForegroundColor Green
