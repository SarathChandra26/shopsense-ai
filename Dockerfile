FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    TRANSFORMERS_NO_TF=1 \
    TF_ENABLE_ONEDNN_OPTS=0

# Install system dependencies (build-essential, curl, sqlite3)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Initialize DB, generate demonstration catalogue, and build vector index
RUN python -m backend.app.database.init_db && \
    python -m backend.app.ingestion.sample_generator && \
    python -m backend.app.ingestion.importer && \
    python -m backend.app.evaluation.eval_dataset_builder

EXPOSE 8000 8501

# Default entrypoint launches both FastAPI and Streamlit
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]
