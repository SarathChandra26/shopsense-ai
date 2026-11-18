import pytest
from backend.app.schemas.product import ProductCreate
from backend.app.schemas.comparison import ComparisonRequest
from backend.app.repositories.product_repository import ProductRepository
from backend.app.comparison.comparator import ProductComparator

def test_comparison_logic(db_session):
    repo = ProductRepository(db_session)
    p1 = repo.create(ProductCreate(
        id="COMP-P1",
        name="Laptop Alpha",
        brand="BrandA",
        category="Laptops",
        price=60000.0,
        description="First laptop",
        specifications={"ram_gb": 16, "battery_hours": 8.0, "weight_kg": 1.5, "is_dedicated_gpu": False}
    ))
    p2 = repo.create(ProductCreate(
        id="COMP-P2",
        name="Laptop Beta",
        brand="BrandB",
        category="Laptops",
        price=85000.0,
        description="Second laptop",
        specifications={"ram_gb": 32, "battery_hours": 6.0, "weight_kg": 2.2, "is_dedicated_gpu": True}
    ))

    comparator = ProductComparator(db_session)
    req = ComparisonRequest(product_ids=["COMP-P1", "COMP-P2"])
    res = comparator.compare_products(req)

    assert len(res.products) == 2
    assert res.category == "Laptops"
    
    # Winners check
    assert "Best Value / Budget" in res.best_for
    assert "Laptop Alpha" in res.best_for["Best Value / Budget"]

    # Check specs matrix
    price_row = next(r for r in res.specs_table if r.spec_key == "price")
    assert price_row.winner_product_id == "COMP-P1"

    ram_row = next(r for r in res.specs_table if r.spec_key == "ram_gb")
    assert ram_row.winner_product_id == "COMP-P2"
