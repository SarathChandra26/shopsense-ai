from typing import List, Tuple, Dict, Any, Optional
from backend.app.embeddings.embedder import get_embedder
from backend.app.vector_store.chroma_client import get_vector_store
from backend.app.schemas.search import SearchFilter

def perform_semantic_search(
    query: str,
    filters: Optional[SearchFilter] = None,
    top_k: int = 50
) -> List[Tuple[str, float]]:
    """
    Perform dense vector similarity search using all-MiniLM-L6-v2 and ChromaDB.
    Returns: List of tuples (product_id, cosine_similarity_score [0..1])
    """
    if not query or not query.strip():
        return []

    embedder = get_embedder()
    query_emb = embedder.encode_text(query)

    vector_store = get_vector_store()
    
    where_filter = None
    if filters and filters.category:
        where_filter = {"category": filters.category}

    raw_results = vector_store.query(
        query_embedding=query_emb,
        top_k=top_k,
        where_filter=where_filter
    )
    
    # Return (product_id, score)
    return [(pid, score) for pid, score, _ in raw_results]
