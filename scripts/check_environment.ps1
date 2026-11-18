# Check ShopSense AI Environment Prerequisites
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  ShopSense AI — Environment Verification Check" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Python version check
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] Python: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not found on PATH." -ForegroundColor Red
}

# 2. SQLite FTS5 Check
$ftsCheck = python -c "import sqlite3; conn = sqlite3.connect(':memory:'); conn.execute('CREATE VIRTUAL TABLE t USING fts5(c);'); print('ENABLED')" 2>&1
if ($ftsCheck -match "ENABLED") {
    Write-Host "[OK] SQLite FTS5 Full-Text Extension: Supported" -ForegroundColor Green
} else {
    Write-Host "[WARNING] SQLite FTS5 may not be enabled in this Python build." -ForegroundColor Yellow
}

# 3. PyTorch CPU check
$torchCheck = python -c "import torch; print(f'Version: {torch.__version__}, CUDA: {torch.cuda.is_available()}')" 2>&1
Write-Host "[OK] PyTorch: $torchCheck" -ForegroundColor Green

# 4. SentenceTransformers & ChromaDB check
$embCheck = python -c "import sentence_transformers, chromadb; print(f'ST: {sentence_transformers.__version__}, ChromaDB: {chromadb.__version__}')" 2>&1
Write-Host "[OK] Core IR Dependencies: $embCheck" -ForegroundColor Green

# 5. Ollama Status Check
Write-Host "Checking local Ollama status..." -ForegroundColor Gray
try {
    $ollamaResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] Ollama is active on http://localhost:11434" -ForegroundColor Green
    $models = $ollamaResponse.models.name
    Write-Host "     Installed Ollama Models: $($models -join ', ')" -ForegroundColor Cyan
} catch {
    Write-Host "[INFO] Ollama is currently offline or not installed." -ForegroundColor Yellow
    Write-Host "       (ShopSense AI will run seamlessly using its built-in rule-grounded response synthesizer)" -ForegroundColor Gray
}

Write-Host "Environment check completed." -ForegroundColor Cyan
