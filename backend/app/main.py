from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.init_db import init_db
from backend.app.api.health import router as health_router
from backend.app.api.products import router as products_router
from backend.app.api.search import router as search_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.comparison import router as comparison_router
from backend.app.api.assistant import router as assistant_router
from backend.app.api.preferences import router as preferences_router
from backend.app.api.feedback import router as feedback_router
from backend.app.api.evaluation import router as evaluation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database, tables, FTS5, and default categories are ready
    logger.info("Initializing ShopSense AI Backend application...")
    init_db()
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} ready.")
    yield
    # Shutdown:
    logger.info("ShopSense AI Backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "ShopSense AI — An AI-Powered Product Discovery & Shopping Recommendation Engine.\n\n"
        "Features:\n"
        "- Dense Semantic Search (SentenceTransformers all-MiniLM-L6-v2 + ChromaDB)\n"
        "- Sparse Keyword Search (SQLite FTS5 BM25)\n"
        "- Hybrid Search via Reciprocal Rank Fusion (RRF)\n"
        "- Multi-Factor Deterministic Ranking & Reranking\n"
        "- Content-Based Personalization & Negative Feedback Avoidance\n"
        "- Category-Specific Product Comparison Engine\n"
        "- Grounded AI Shopping Assistant (Ollama Llama 3.2 / Fallback Synthesizer)\n"
        "- Precision/Recall/MRR/NDCG Evaluation Framework"
    ),
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Health router
app.include_router(health_router)
app.include_router(health_router, prefix=settings.API_V1_STR)

# Mount API Routers under /api
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(comparison_router, prefix=settings.API_V1_STR)
app.include_router(assistant_router, prefix=settings.API_V1_STR)
app.include_router(preferences_router, prefix=settings.API_V1_STR)
app.include_router(feedback_router, prefix=settings.API_V1_STR)
app.include_router(evaluation_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
