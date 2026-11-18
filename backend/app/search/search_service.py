import time
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.schemas.search import SearchRequest, SearchResponse, SearchResultItem, ScoreBreakdown
from backend.app.schemas.product import ProductResponse
from backend.app.search.query_parser import QueryParser
from backend.app.search.semantic_search import perform_semantic_search
from backend.app.search.keyword_search import perform_keyword_search
from backend.app.search.hybrid_search import perform_hybrid_search
from backend.app.ranking.reranker import ProductReranker
from backend.app.repositories.product_repository import ProductRepository
from backend.app.repositories.preference_repository import PreferenceRepository
from backend.app.repositories.interaction_repository import InteractionRepository

def execute_search(
    request: SearchRequest,
    db: Session
) -> SearchResponse:
    """
    Unified search entry point supporting:
    - semantic: Pure vector dense retrieval
    - keyword: Pure SQLite FTS5 BM25 retrieval
    - hybrid: Reciprocal Rank Fusion of semantic + keyword
    - hybrid_rerank: Hybrid retrieval followed by second-stage multi-factor reranker
    """
    start_time = time.perf_counter()
    query = request.query
    search_type = request.search_type
    filters = request.filters
    limit = request.limit
    offset = request.offset
    user_id = request.user_id

    # 1. Parse natural language query
    constraints = QueryParser.parse(query)

    # 2. Fetch user preferences if user_id is provided
    pref_repo = PreferenceRepository(db)
    user_pref = pref_repo.get_by_user_id(user_id) if user_id else None

    # 3. Retrieve candidates according to search_type
    repo = ProductRepository(db)
    reranker = ProductReranker()
    candidate_pool_size = max(50, limit * 3)

    results: List[SearchResultItem] = []

    if search_type == "semantic":
        raw_sem = perform_semantic_search(query=query, filters=filters, top_k=candidate_pool_size)
        candidates = [{"product_id": pid, "semantic_score": score, "keyword_score": 0.0} for pid, score in raw_sem]
        results = reranker.rerank_candidates(
            candidates=candidates,
            db=db,
            query=query,
            constraints=constraints,
            filters=filters,
            user_preference=user_pref,
            top_k=limit,
            enforce_hard_budget=False
        )

    elif search_type == "keyword":
        raw_kw = perform_keyword_search(query=query, db=db, filters=filters, top_k=candidate_pool_size)
        candidates = [{"product_id": pid, "semantic_score": 0.0, "keyword_score": score} for pid, score in raw_kw]
        results = reranker.rerank_candidates(
            candidates=candidates,
            db=db,
            query=query,
            constraints=constraints,
            filters=filters,
            user_preference=user_pref,
            top_k=limit,
            enforce_hard_budget=False
        )

    elif search_type == "hybrid":
        fused = perform_hybrid_search(query=query, db=db, filters=filters, candidate_pool_size=candidate_pool_size)
        # In hybrid without full rerank, use RRF score directly
        pids = [f["product_id"] for f in fused[:limit]]
        products = {p.id: p for p in repo.get_by_ids(pids)}
        for f in fused[:limit]:
            p = products.get(f["product_id"])
            if p:
                p_dict = repo.format_product_dict(p)
                reasons, limits = ProductReranker.extract_reasons_and_limitations(p_dict, constraints)
                results.append(SearchResultItem(
                    product=ProductResponse(**p_dict),
                    score=round(f["rrf_score"] * 30, 4), # scaled for display
                    score_breakdown=ScoreBreakdown(
                        semantic_score=round(f["semantic_score"], 4),
                        keyword_score=round(f["keyword_score"], 4),
                        final_score=round(f["rrf_score"] * 30, 4)
                    ),
                    match_reasons=reasons,
                    limitations=limits
                ))

    elif search_type == "hybrid_rerank":
        fused = perform_hybrid_search(query=query, db=db, filters=filters, candidate_pool_size=candidate_pool_size)
        results = reranker.rerank_candidates(
            candidates=fused,
            db=db,
            query=query,
            constraints=constraints,
            filters=filters,
            user_preference=user_pref,
            top_k=limit,
            enforce_hard_budget=True
        )

    # 4. Measure latency and record search history
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    if user_id:
        try:
            interaction_repo = InteractionRepository(db)
            filter_str = str(filters.dict()) if filters else None
            interaction_repo.record_search(
                user_id=user_id,
                query=query,
                search_type=search_type,
                filters_json=filter_str,
                results_count=len(results),
                latency_ms=elapsed_ms
            )
        except Exception:
            pass

    explanation = (
        f"Search executed in {elapsed_ms:.1f}ms using {search_type} retrieval. "
        f"Retrieved {len(results)} relevant product(s) matching your criteria."
    )

    return SearchResponse(
        query=query,
        search_type=search_type,
        total_found=len(results),
        results=results,
        latency_ms=round(elapsed_ms, 2),
        explanation=explanation
    )
