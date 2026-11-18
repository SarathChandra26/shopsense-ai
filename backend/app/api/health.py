from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database.session import get_db
from backend.app.vector_store.chroma_client import get_vector_store
from backend.app.assistant.ollama_client import OllamaClient
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    # 1. Check SQLite
    sql_ok = False
    product_count = 0
    try:
        res = db.execute(text("SELECT count(*) FROM products")).scalar()
        product_count = int(res or 0)
        sql_ok = True
    except Exception as e:
        sql_error = str(e)

    # 2. Check ChromaDB
    chroma_ok = False
    chroma_count = 0
    try:
        store = get_vector_store()
        chroma_count = store.get_count()
        chroma_ok = True
    except Exception:
        pass

    # 3. Check Ollama
    ollama = OllamaClient()
    ollama_ok = ollama.is_available()

    return {
        "status": "healthy" if sql_ok and chroma_ok else "degraded",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "status": "connected" if sql_ok else "error",
            "total_products": product_count,
        },
        "vector_store": {
            "engine": "ChromaDB",
            "collection": settings.CHROMA_COLLECTION_NAME,
            "indexed_vectors": chroma_count,
            "status": "connected" if chroma_ok else "error"
        },
        "llm_assistant": {
            "provider": "Ollama",
            "model": settings.OLLAMA_MODEL,
            "status": "connected" if ollama_ok else "offline (rule-based grounded engine active)",
            "endpoint": settings.OLLAMA_BASE_URL
        }
    }
