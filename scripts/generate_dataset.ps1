# Generate 1,100 demonstration products
Write-Host "Generating synthetic demonstration catalogue..." -ForegroundColor Cyan
python -m backend.app.ingestion.sample_generator
python -m backend.app.evaluation.eval_dataset_builder
Write-Host "Dataset generation complete." -ForegroundColor Green
