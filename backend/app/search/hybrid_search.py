from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.schemas.search import SearchFilter
from backend.app.search.semantic_search import perform_semantic_search
from backend.app.search.keyword_search import perform_keyword_search

def reciprocal_rank_fusion(
    semantic_results: List[Tuple[str, float]],
    keyword_results: List[Tuple[str, float]],
    k: int = settings.RRF_K
) -> List[Dict[str, Any]]:
    """
    Fuse dense semantic and sparse keyword results using Reciprocal Rank Fusion (RRF).
    Formula: RRF_score(d) = sum_{m in {semantic, keyword}} (1 / (k + rank_m(d)))
    
    Returns list of dicts with:
    - product_id
    - rrf_score
    - semantic_score
    - keyword_score
    - semantic_rank
    - keyword_rank
    """
    scores: Dict[str, Dict[str, Any]] = {}

    # 1. Process Semantic Ranks (1-based)
    for rank, (pid, sim_score) in enumerate(semantic_results, start=1):
        if pid not in scores:
            scores[pid] = {
                "product_id": pid,
                "rrf_score": 0.0,
                "semantic_score": sim_score,
                "keyword_score": 0.0,
                "semantic_rank": rank,
                "keyword_rank": None
            }
        scores[pid]["rrf_score"] += 1.0 / (k + rank)
        scores[pid]["semantic_score"] = sim_score
        scores[pid]["semantic_rank"] = rank

    # 2. Process Keyword Ranks (1-based)
    for rank, (pid, kw_score) in enumerate(keyword_results, start=1):
        if pid not in scores:
            scores[pid] = {
                "product_id": pid,
                "rrf_score": 0.0,
                "semantic_score": 0.0,
                "keyword_score": kw_score,
                "semantic_rank": None,
                "keyword_rank": rank
            }
        scores[pid]["rrf_score"] += 1.0 / (k + rank)
        scores[pid]["keyword_score"] = kw_score
        scores[pid]["keyword_rank"] = rank

    # Sort descending by RRF score
    sorted_candidates = sorted(scores.values(), key=lambda x: x["rrf_score"], reverse=True)
    return sorted_candidates

def perform_hybrid_search(
    query: str,
    db: Session,
    filters: Optional[SearchFilter] = None,
    candidate_pool_size: int = settings.CANDIDATE_POOL_SIZE
) -> List[Dict[str, Any]]:
    """
    Execute hybrid search by running semantic and keyword search in parallel,
    fusing them via RRF, and returning candidates.
    """
    semantic_res = perform_semantic_search(query=query, filters=filters, top_k=candidate_pool_size)
    keyword_res = perform_keyword_search(query=query, db=db, filters=filters, top_k=candidate_pool_size)

    fused = reciprocal_rank_fusion(
        semantic_results=semantic_res,
        keyword_results=keyword_res,
        k=settings.RRF_K
    )
    return fused
