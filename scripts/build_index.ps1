# Ingest and Index Catalogue into SQLite, FTS5, and ChromaDB
Write-Host "Building SQLite, FTS5, and ChromaDB Vector Indices..." -ForegroundColor Cyan
python -m backend.app.ingestion.importer
Write-Host "Index build complete." -ForegroundColor Green
