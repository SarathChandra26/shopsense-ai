import pytest
from backend.app.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
    evaluate_constraint_satisfaction
)

def test_metrics_calculations():
    retrieved = ["p1", "p2", "p3", "p4", "p5"]
    relevant = {"p2", "p4", "p6"}
    graded = {"p2": 2, "p4": 1, "p6": 2}

    # Precision@5: hits = 2 (p2, p4) / 5 = 0.4
    assert precision_at_k(retrieved, relevant, k=5) == 0.4

    # Recall@5: hits = 2 / 3 = 0.6667
    assert round(recall_at_k(retrieved, relevant, k=5), 4) == 0.6667

    # Reciprocal Rank: first hit is p2 at rank 2 -> 1/2 = 0.5
    assert reciprocal_rank(retrieved, relevant) == 0.5

    # NDCG@5 should be > 0 and <= 1.0
    ndcg = ndcg_at_k(retrieved, graded, k=5)
    assert 0.0 < ndcg <= 1.0

def test_constraint_satisfaction():
    class MockProduct:
        def __init__(self, price, category, brand, specs):
            self.price = price
            self.category = category
            self.brand = brand
            self.specifications = specs

    items = [
        MockProduct(65000.0, "Laptops", "Lenovo", {"ram_gb": 16}),
        MockProduct(68000.0, "Laptops", "Dell", {"ram_gb": 16}),
    ]
    constraints = {"category": "Laptops", "budget_max": 70000.0, "ram_gb": 16.0}
    score = evaluate_constraint_satisfaction(items, constraints)
    assert score == 1.0
