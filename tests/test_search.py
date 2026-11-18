import pytest
from backend.app.search.query_parser import QueryParser
from backend.app.search.hybrid_search import reciprocal_rank_fusion
from backend.app.database.fts_index import index_product_fts, search_fts

def test_query_parser():
    q = "I want a Lenovo laptop under 70000 for Python development with 16 GB RAM and gaming"
    constraints = QueryParser.parse(q)
    assert constraints.category == "Laptops"
    assert constraints.brand == "Lenovo"
    assert constraints.budget_max == 70000.0
    assert constraints.ram_gb == 16.0
    assert "gaming" in constraints.intended_usage
    assert "python" in constraints.intended_usage

def test_query_parser_k_units():
    q = "budget of 50k for headphones"
    c = QueryParser.parse(q)
    assert c.budget_max == 50000.0
    assert c.category == "Headphones"

def test_reciprocal_rank_fusion_math():
    semantic_results = [("PROD-1", 0.95), ("PROD-2", 0.85), ("PROD-3", 0.75)]
    keyword_results = [("PROD-2", 0.90), ("PROD-1", 0.80), ("PROD-4", 0.70)]

    # Formula: 1 / (60 + rank)
    fused = reciprocal_rank_fusion(semantic_results, keyword_results, k=60)
    
    # PROD-1: sem rank 1 (1/61) + kw rank 2 (1/62) = 0.01639 + 0.01613 = 0.03252
    # PROD-2: sem rank 2 (1/62) + kw rank 1 (1/61) = 0.01613 + 0.01639 = 0.03252 (tie)
    # PROD-3: sem rank 3 (1/63) = 0.01587
    # PROD-4: kw rank 3 (1/63) = 0.01587
    fused_pids = [f["product_id"] for f in fused]
    assert set(fused_pids[:2]) == {"PROD-1", "PROD-2"}
    assert set(fused_pids[2:]) == {"PROD-3", "PROD-4"}

def test_sqlite_fts5_search(db_session):
    index_product_fts(
        db=db_session,
        product_id="TEST-LAP-RTX",
        name="Acer Nitro V 15",
        brand="Acer",
        category="Laptops",
        description="High performance gaming laptop",
        specifications_text="GPU: NVIDIA RTX 4050 6GB; RAM: 16 GB"
    )
    
    # Search for specific model keyword
    res = search_fts(db=db_session, query="RTX 4050")
    assert len(res) > 0
    assert res[0][0] == "TEST-LAP-RTX"
