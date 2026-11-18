import pytest
from backend.app.ranking.ranker import MultiFactorRanker
from backend.app.schemas.ranking import RankingWeights
from backend.app.schemas.assistant import ExtractedConstraints
from backend.app.ranking.reranker import ProductReranker

def test_ranker_budget_scoring():
    # In budget: price <= budget_max
    assert MultiFactorRanker.calculate_budget_score(price=65000.0, budget_max=70000.0, strict_budget=True) == 1.0

    # Hard constraint: price > budget_max with strict_budget=True
    assert MultiFactorRanker.calculate_budget_score(price=75000.0, budget_max=70000.0, strict_budget=True) == 0.0

    # Soft constraint: price > budget_max with strict_budget=False
    soft_score = MultiFactorRanker.calculate_budget_score(price=75000.0, budget_max=70000.0, strict_budget=False)
    assert 0.0 <= soft_score < 1.0

def test_ranker_spec_scoring():
    constraints = ExtractedConstraints(ram_gb=16.0, intended_usage="machine learning, gaming")
    
    # Matching specs
    matching_specs = {"ram_gb": 16.0, "gpu": "NVIDIA GeForce RTX 4050", "is_dedicated_gpu": True}
    score_match = MultiFactorRanker.calculate_spec_score(matching_specs, constraints)
    assert score_match == 1.0

    # Low specs: 8GB RAM, integrated GPU
    low_specs = {"ram_gb": 8.0, "gpu": "Intel Iris Xe", "is_dedicated_gpu": False}
    score_low = MultiFactorRanker.calculate_spec_score(low_specs, constraints)
    assert score_low < score_match

def test_ranker_composite_formula():
    weights = RankingWeights(semantic=0.35, keyword=0.20, specification=0.20, budget=0.15, rating=0.10)
    ranker = MultiFactorRanker(weights)

    breakdown = ranker.compute_composite_score(
        semantic_score=1.0,
        keyword_score=1.0,
        spec_score=1.0,
        budget_score=1.0,
        preference_score=1.0,
        rating_score=1.0
    )
    assert breakdown.final_score == 1.0

def test_reranker_reasons_and_limits():
    prod = {
        "price": 68990.0,
        "category": "Laptops",
        "rating": 4.6,
        "review_count": 800,
        "specifications": {
            "ram_gb": 16.0,
            "gpu": "NVIDIA RTX 4050",
            "is_dedicated_gpu": True,
            "battery_hours": 6.5,
            "weight_kg": 2.3
        }
    }
    constraints = ExtractedConstraints(ram_gb=16.0, budget_max=70000.0)
    reasons, limits = ProductReranker.extract_reasons_and_limitations(prod, constraints, budget_max=70000.0)

    # Reasons should mention budget savings and 16 GB RAM
    assert any("budget" in r.lower() for r in reasons)
    assert any("16 gb" in r.lower() for r in reasons)

    # Limitations should honestly mention heavy weight and modest battery
    assert any("weight" in l.lower() for l in limits)
    assert any("battery" in l.lower() for l in limits)
