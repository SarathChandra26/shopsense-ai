import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Disable TensorFlow backend in transformers for CPU efficiency and stability
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Workspace base directory (e:\New folder (4))
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ShopSense AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Storage and database paths
    STORAGE_DIR: Path = BASE_DIR / "storage"
    SQLITE_PATH: Path = BASE_DIR / "storage" / "sqlite" / "shopsense.db"
    CHROMA_PATH: Path = BASE_DIR / "storage" / "chroma"
    DATA_DIR: Path = BASE_DIR / "data"
    PRODUCTS_CSV_PATH: Path = BASE_DIR / "data" / "products.csv"
    EVALUATION_TESTSET_PATH: Path = BASE_DIR / "data" / "evaluation" / "ground_truth_testset.json"
    
    # SQLAlchemy DB URL
    DATABASE_URL: str = f"sqlite:///{SQLITE_PATH.as_posix()}"
    
    # Embedding Configuration
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    CHROMA_COLLECTION_NAME: str = "shopsense_products"
    
    # Hybrid Search & RRF Parameters
    RRF_K: int = 60
    DEFAULT_TOP_K: int = 10
    CANDIDATE_POOL_SIZE: int = 40
    
    # Default Multi-Factor Ranking Weights (Sum to 1.0)
    WEIGHT_SEMANTIC: float = 0.35
    WEIGHT_KEYWORD: float = 0.20
    WEIGHT_SPECIFICATION: float = 0.20
    WEIGHT_BUDGET: float = 0.15
    WEIGHT_RATING: float = 0.10
    
    # LLM & Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    OLLAMA_TIMEOUT_SECONDS: int = 15
    
    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
(settings.STORAGE_DIR / "sqlite").mkdir(parents=True, exist_ok=True)
(settings.STORAGE_DIR / "chroma").mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "evaluation").mkdir(parents=True, exist_ok=True)
