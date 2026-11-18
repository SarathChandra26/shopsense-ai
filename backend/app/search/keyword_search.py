from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from backend.app.database.fts_index import search_fts
from backend.app.schemas.search import SearchFilter

def perform_keyword_search(
    query: str,
    db: Session,
    filters: Optional[SearchFilter] = None,
    top_k: int = 50
) -> List[Tuple[str, float]]:
    """
    Perform sparse keyword search using SQLite FTS5 (BM25).
    Returns: List of tuples (product_id, normalized_bm25_score [0..1])
    """
    if not query or not query.strip():
        return []

    results = search_fts(db=db, query=query, limit=top_k)
    return results
