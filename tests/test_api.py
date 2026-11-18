import pytest
from backend.app.schemas.product import ProductCreate

def test_api_health(test_client):
    res = test_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "vector_store" in data

def test_api_product_crud(test_client):
    payload = {
        "id": "API-TEST-001",
        "name": "API Laptop Test",
        "brand": "TestBrand",
        "category": "Laptops",
        "price": 55000.0,
        "description": "Fast laptop for testing",
        "specifications": {"ram_gb": 16, "processor": "Intel i5"}
    }
    # Create
    create_res = test_client.post("/api/products", json=payload)
    assert create_res.status_code == 201
    assert create_res.json()["id"] == "API-TEST-001"

    # Read
    get_res = test_client.get("/api/products/API-TEST-001")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "API Laptop Test"

    # Update
    update_res = test_client.put("/api/products/API-TEST-001", json={"price": 52000.0})
    assert update_res.status_code == 200
    assert update_res.json()["price"] == 52000.0

    # Delete
    del_res = test_client.delete("/api/products/API-TEST-001")
    assert del_res.status_code == 204
    assert test_client.get("/api/products/API-TEST-001").status_code == 404

def test_api_search_endpoints(test_client):
    search_payload = {
        "query": "laptop with 16 GB RAM",
        "limit": 5
    }
    # Semantic
    res_sem = test_client.post("/api/search/semantic", json=search_payload)
    assert res_sem.status_code == 200
    assert "results" in res_sem.json()

    # Keyword
    res_kw = test_client.post("/api/search/keyword", json=search_payload)
    assert res_kw.status_code == 200
    assert "results" in res_kw.json()

    # Hybrid
    res_hyb = test_client.post("/api/search/hybrid", json=search_payload)
    assert res_hyb.status_code == 200
    assert "results" in res_hyb.json()

def test_api_preferences_and_feedback(test_client):
    user_id = "api_user_test"
    # Update preference
    pref_payload = {
        "preferred_categories": ["Laptops"],
        "budget_max": 80000.0,
        "preferred_brands": ["Dell"]
    }
    put_res = test_client.put(f"/api/preferences/{user_id}", json=pref_payload)
    assert put_res.status_code == 200
    assert put_res.json()["budget_max"] == 80000.0

    # Get preference
    get_res = test_client.get(f"/api/preferences/{user_id}")
    assert get_res.status_code == 200
    assert "Dell" in get_res.json()["preferred_brands"]

    # Submit feedback
    fb_payload = {
        "user_id": user_id,
        "product_id": "PROD-LAP-001",
        "feedback_type": "useful",
        "comment": "Great recommendation"
    }
    fb_res = test_client.post("/api/feedback", json=fb_payload)
    assert fb_res.status_code == 201

    # Analytics summary
    an_res = test_client.get("/api/analytics/summary")
    assert an_res.status_code == 200
    assert "total_searches" in an_res.json()

def test_api_invalid_inputs(test_client):
    # Invalid category
    bad_prod = {
        "name": "Bad Product",
        "brand": "BadBrand",
        "category": "NonExistentCategory",
        "price": 100.0,
        "description": "test"
    }
    # FastAPI schema validation error (or 422 Unprocessable Entity)
    r = test_client.post("/api/products", json=bad_prod)
    # Price must be valid and category must be valid
    assert r.status_code in [422, 400]
