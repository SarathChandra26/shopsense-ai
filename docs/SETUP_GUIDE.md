# ShopSense AI — Setup & Installation Guide

This guide details how to install, configure, verify, and run ShopSense AI on Windows 10/11 using PowerShell and Python 3.10+.

---

## 1. System Requirements
- **OS**: Windows 10 or 11 (64-bit)
- **Python**: Python 3.10 or 3.11
- **RAM**: Minimum 8 GB (16 GB recommended)
- **Disk Space**: ~2 GB (including dependencies, dataset, vector database, and cached embeddings)
- **CPU**: Modern Intel i5/i7 or AMD Ryzen processor (CPU-only execution fully supported)

---

## 2. Quick Setup (Automated PowerShell Script)

Open a PowerShell terminal in the project directory (`e:\New folder (4)`):

```powershell
# 1. Run environment check
.\scripts\check_environment.ps1

# 2. Run one-click setup (installs deps, builds DB, generates 1,100 products, builds ChromaDB vector store)
.\scripts\setup.ps1

# 3. Run automated tests to verify everything passes
.\scripts\run_tests.ps1

# 4. Start both FastAPI and Streamlit
.\scripts\start.ps1
```

Once running:
- **Streamlit Web Dashboard**: `http://localhost:8501`
- **FastAPI REST API**: `http://localhost:8000`
- **FastAPI Interactive Docs (Swagger)**: `http://localhost:8000/docs`

---

## 3. Manual Step-by-Step Setup

If you prefer running commands manually:

```powershell
# Step 1: Install Python Dependencies
python -m pip install -r requirements.txt

# Step 2: Initialize SQLite Schema and FTS5 Virtual Table
python -m backend.app.database.init_db

# Step 3: Generate 1,100 Demonstration Products
python -m backend.app.ingestion.sample_generator

# Step 4: Build Ground Truth Benchmark Dataset
python -m backend.app.evaluation.eval_dataset_builder

# Step 5: Index Products into ChromaDB & SQLite FTS5
python -m backend.app.ingestion.importer

# Step 6: Run Tests
python -m pytest tests -v
```

---

## 4. (Optional) Enabling Ollama Local LLM

ShopSense AI includes a **built-in deterministic rule-grounded response engine** that functions completely offline without Ollama.

If you wish to enable the local LLM generation layer:
1. Open PowerShell and install Ollama:
   ```powershell
   winget install Ollama.Ollama
   ```
   *(Or download the installer from https://ollama.com/download/windows)*
2. Start Ollama and download Llama 3.2 (3B parameters, ~2.0 GB):
   ```powershell
   ollama run llama3.2
   ```
3. ShopSense AI will automatically detect Ollama at `http://localhost:11434` and route shopping explanations through it!

---

## 5. Docker Deployment

```bash
docker-compose up --build
```
Access the application at `http://localhost:8501`.
