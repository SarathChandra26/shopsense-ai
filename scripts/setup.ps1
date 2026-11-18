# ShopSense AI One-Click Setup Script
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "       Setting up ShopSense AI Platform           " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Install dependencies
Write-Host "Step 1: Installing Python dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

# 2. Initialize Database & FTS5
Write-Host "Step 2: Initializing SQLite database and FTS5 full-text tables..." -ForegroundColor Yellow
python -m backend.app.database.init_db

# 3. Generate Demonstration Catalogue (1,100 products)
Write-Host "Step 3: Generating 1,100 demonstration products across 10 categories..." -ForegroundColor Yellow
python -m backend.app.ingestion.sample_generator

# 4. Generate Ground-Truth Evaluation Testset
Write-Host "Step 4: Building ground-truth evaluation benchmark queries..." -ForegroundColor Yellow
python -m backend.app.evaluation.eval_dataset_builder

# 5. Ingest into ChromaDB & FTS5
Write-Host "Step 5: Embedding and indexing products into ChromaDB and SQLite FTS5..." -ForegroundColor Yellow
python -m backend.app.ingestion.importer

Write-Host "=================================================" -ForegroundColor Green
Write-Host "  Setup successfully completed! Run .\scripts\start.ps1 " -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
