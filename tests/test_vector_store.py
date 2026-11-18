import pytest
from backend.app.vector_store.chroma_client import ChromaVectorStore

def test_vector_store_operations():
    store = ChromaVectorStore()
    
    # Test incremental upsert
    pid = "TEST-VEC-001"
    emb = [0.05] * 384
    doc = "Test document content"
    meta = {"product_id": pid, "category": "Laptops", "price": 50000.0}
    
    store.upsert_product(pid, emb, doc, meta)
    
    # Query
    results = store.query(query_embedding=emb, top_k=5)
    matched_ids = [r[0] for r in results]
    assert pid in matched_ids

    # Delete
    store.delete_product(pid)
    results_after = store.query(query_embedding=emb, top_k=5)
    assert pid not in [r[0] for r in results_after]
