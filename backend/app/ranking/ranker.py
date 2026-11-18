from typing import Dict, Any, Optional
from backend.app.schemas.ranking import RankingWeights
from backend.app.schemas.search import ScoreBreakdown
from backend.app.schemas.assistant import ExtractedConstraints
from backend.app.models.preference import UserPreference

class MultiFactorRanker:
    """
    Transparent, deterministic multi-factor ranking engine.
    Combines: Semantic relevance, Keyword relevance, Specification match,
    Budget compatibility, Preference alignment, and Rating.
    """
    def __init__(self, weights: Optional[RankingWeights] = None):
        self.weights = (weights or RankingWeights()).normalize()

    @staticmethod
    def calculate_budget_score(
        price: float,
        budget_max: Optional[float] = None,
        budget_min: Optional[float] = None,
        strict_budget: bool = True
    ) -> float:
        """
        Calculate budget compatibility score in [0.0, 1.0].
        If strict_budget is True and price > budget_max, score is 0.0 (hard constraint).
        """
        if budget_max is None and budget_min is None:
            return 1.0  # No budget constraint specified

        # Check maximum budget
        if budget_max is not None:
            if price > budget_max:
                if strict_budget:
                    return 0.0  # Hard constraint failure
                overshoot_pct = (price - budget_max) / budget_max
                return max(0.0, 1.0 - overshoot_pct * 3.0)
            else:
                # Within budget: closer to budget_max without exceeding is optimal value
                # e.g., spending 70% - 98% of budget gets 0.95 - 1.0
                ratio = price / budget_max
                if ratio >= 0.65:
                    return 1.0
                return max(0.6, ratio)

        # Check minimum budget
        if budget_min is not None and price < budget_min:
            return max(0.2, price / budget_min)

        return 1.0

    @staticmethod
    def calculate_spec_score(
        product_specs: Dict[str, Any],
        constraints: Optional[ExtractedConstraints] = None
    ) -> float:
        """Calculate specification compatibility score in [0.0, 1.0]."""
        if not constraints:
            return 0.8  # neutral baseline

        score_components = []

        # 1. RAM requirement
        if constraints.ram_gb is not None:
            prod_ram = product_specs.get("ram_gb")
            if prod_ram is not None:
                try:
                    ram_val = float(prod_ram)
                    if ram_val >= constraints.ram_gb:
                        score_components.append(1.0)
                    else:
                        score_components.append(ram_val / constraints.ram_gb)
                except ValueError:
                    score_components.append(0.5)

        # 2. Dedicated GPU requirement (if gaming, machine learning, or 3D requested)
        needs_gpu = False
        if constraints.intended_usage:
            usage_lower = constraints.intended_usage.lower()
            if any(term in usage_lower for term in ["gaming", "machine learning", "ml", "gpu", "deep learning"]):
                needs_gpu = True

        if needs_gpu:
            is_dedicated = product_specs.get("is_dedicated_gpu", False)
            gpu_name = str(product_specs.get("gpu", "")).lower()
            if is_dedicated or any(g in gpu_name for g in ["rtx", "gtx", "radeon rx"]):
                score_components.append(1.0)
            else:
                score_components.append(0.3)  # Significant penalty for lack of GPU

        # 3. Battery requirement
        if constraints.intended_usage and any(b in constraints.intended_usage.lower() for b in ["battery", "travel", "all day"]):
            battery = product_specs.get("battery_hours") or product_specs.get("battery_days")
            if battery:
                try:
                    bat_val = float(battery)
                    score_components.append(1.0 if bat_val >= 10.0 else max(0.5, bat_val / 10.0))
                except ValueError:
                    pass

        if not score_components:
            return 0.85
        return sum(score_components) / len(score_components)

    @staticmethod
    def calculate_preference_score(
        product: Dict[str, Any],
        preference: Optional[UserPreference] = None
    ) -> float:
        """Calculate user historical preference alignment in [0.0, 1.0]."""
        if not preference:
            return 0.5  # neutral baseline

        boosts = []
        
        # Preferred category
        if preference.preferred_categories:
            cats = [c.strip().lower() for c in preference.preferred_categories.split(",")]
            if product.get("category", "").lower() in cats:
                boosts.append(1.0)
            else:
                boosts.append(0.4)

        # Preferred brand
        if preference.preferred_brands:
            brands = [b.strip().lower() for b in preference.preferred_brands.split(",")]
            if product.get("brand", "").lower() in brands:
                boosts.append(1.0)
            else:
                boosts.append(0.5)

        # Intended usage match
        if preference.intended_usage:
            desc = product.get("description", "").lower()
            for usage_term in preference.intended_usage.lower().split(","):
                if usage_term.strip() and usage_term.strip() in desc:
                    boosts.append(0.9)
                    break

        if not boosts:
            return 0.5
        return sum(boosts) / len(boosts)

    @staticmethod
    def calculate_rating_score(rating: float) -> float:
        """Normalize 1..5 star rating to [0..1] range."""
        clamped = max(1.0, min(5.0, rating))
        return (clamped - 1.0) / 4.0

    def compute_composite_score(
        self,
        semantic_score: float,
        keyword_score: float,
        spec_score: float,
        budget_score: float,
        preference_score: float,
        rating_score: float
    ) -> ScoreBreakdown:
        """Compute transparent weighted multi-factor ranking score."""
        w = self.weights
        final = (
            (semantic_score * w.semantic) +
            (keyword_score * w.keyword) +
            (spec_score * w.specification) +
            (budget_score * w.budget) +
            (rating_score * w.rating)
        )
        # Apply preference as soft bonus factor (scaled)
        final = min(1.0, final * (0.85 + 0.15 * preference_score))

        return ScoreBreakdown(
            semantic_score=round(semantic_score, 4),
            keyword_score=round(keyword_score, 4),
            specification_score=round(spec_score, 4),
            budget_score=round(budget_score, 4),
            preference_score=round(preference_score, 4),
            rating_score=round(rating_score, 4),
            final_score=round(final, 4)
        )
