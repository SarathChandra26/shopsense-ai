from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.search import SearchRequest, SearchResponse
from backend.app.search.search_service import execute_search

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/semantic", response_model=SearchResponse)
def search_semantic(request: SearchRequest, db: Session = Depends(get_db)):
    request.search_type = "semantic"
    return execute_search(request, db)

@router.post("/keyword", response_model=SearchResponse)
def search_keyword(request: SearchRequest, db: Session = Depends(get_db)):
    request.search_type = "keyword"
    return execute_search(request, db)

@router.post("/hybrid", response_model=SearchResponse)
def search_hybrid(request: SearchRequest, db: Session = Depends(get_db)):
    # Defaults to hybrid_rerank unless hybrid requested explicitly
    if request.search_type not in ["hybrid", "hybrid_rerank"]:
        request.search_type = "hybrid_rerank"
    return execute_search(request, db)
