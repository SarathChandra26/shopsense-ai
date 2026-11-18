import math
from typing import List, Dict, Any, Set

def precision_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Calculate Precision@K = |Retrieved@K ∩ Relevant| / K"""
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for pid in top_k if pid in relevant_ids)
    return hits / float(k)

def recall_at_k(retrieved_ids: List[str], relevant_ids: Set[str], k: int) -> float:
    """Calculate Recall@K = |Retrieved@K ∩ Relevant| / |Relevant|"""
    if not relevant_ids:
        return 1.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for pid in top_k if pid in relevant_ids)
    return hits / float(len(relevant_ids))

def reciprocal_rank(retrieved_ids: List[str], relevant_ids: Set[str]) -> float:
    """Calculate Reciprocal Rank (RR) = 1 / rank of first relevant item."""
    for rank, pid in enumerate(retrieved_ids, start=1):
        if pid in relevant_ids:
            return 1.0 / float(rank)
    return 0.0

def ndcg_at_k(retrieved_ids: List[str], graded_relevance: Dict[str, int], k: int) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain at K (NDCG@K).
    Formula: DCG@K = sum_{i=1}^K (2^{rel_i} - 1) / log2(i + 1)
    NDCG@K = DCG@K / IDCG@K
    """
    if k <= 0 or not graded_relevance:
        return 0.0

    # Calculate DCG@K
    dcg = 0.0
    top_k = retrieved_ids[:k]
    for i, pid in enumerate(top_k, start=1):
        rel = graded_relevance.get(pid, 0)
        dcg += (2.0 ** rel - 1.0) / math.log2(i + 1.0)

    # Calculate Ideal DCG (IDCG@K)
    sorted_rels = sorted(graded_relevance.values(), reverse=True)[:k]
    idcg = 0.0
    for i, rel in enumerate(sorted_rels, start=1):
        idcg += (2.0 ** rel - 1.0) / math.log2(i + 1.0)

    if idcg <= 0.0:
        return 0.0
    return dcg / idcg

def evaluate_constraint_satisfaction(
    retrieved_items: List[Any],
    constraints: Dict[str, Any]
) -> float:
    """
    Verify what percentage of retrieved items satisfy the specified constraints
    (budget_max, category, ram_gb, brand).
    """
    if not retrieved_items or not constraints:
        return 1.0

    total_checks = 0
    passed_checks = 0

    target_cat = constraints.get("category")
    max_budget = constraints.get("budget_max")
    target_brand = constraints.get("brand")
    min_ram = constraints.get("ram_gb")

    for item in retrieved_items:
        prod = getattr(item, "product", item)
        price = getattr(prod, "price", 0.0)
        cat = getattr(prod, "category", "")
        brand = getattr(prod, "brand", "")
        specs = getattr(prod, "specifications", {})

        if target_cat:
            total_checks += 1
            if cat.lower() == target_cat.lower():
                passed_checks += 1

        if max_budget:
            total_checks += 1
            if price <= max_budget:
                passed_checks += 1

        if target_brand:
            total_checks += 1
            if brand.lower() == target_brand.lower():
                passed_checks += 1

        if min_ram and isinstance(specs, dict):
            ram = specs.get("ram_gb")
            if ram:
                total_checks += 1
                try:
                    if float(ram) >= float(min_ram):
                        passed_checks += 1
                except ValueError:
                    pass

    if total_checks == 0:
        return 1.0
    return passed_checks / float(total_checks)
