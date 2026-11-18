from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.schemas.search import SearchResultItem, SearchFilter, ScoreBreakdown
from backend.app.schemas.ranking import RankingWeights
from backend.app.schemas.product import ProductResponse
from backend.app.schemas.assistant import ExtractedConstraints
from backend.app.models.preference import UserPreference
from backend.app.repositories.product_repository import ProductRepository
from backend.app.ranking.ranker import MultiFactorRanker

class ProductReranker:
    def __init__(self, weights: Optional[RankingWeights] = None):
        self.ranker = MultiFactorRanker(weights)

    @staticmethod
    def extract_reasons_and_limitations(
        prod_dict: Dict[str, Any],
        constraints: Optional[ExtractedConstraints] = None,
        budget_max: Optional[float] = None
    ) -> (List[str], List[str]):
        """Generate deterministic, grounded match reasons and honest limitations."""
        reasons = []
        limitations = []
        price = prod_dict.get("price", 0.0)
        specs = prod_dict.get("specifications", {})
        category = prod_dict.get("category", "")

        # 1. Budget analysis
        if budget_max:
            if price <= budget_max:
                savings = budget_max - price
                reasons.append(f"Comfortably within budget: ₹{price:,.0f} (₹{savings:,.0f} under your limit).")
            else:
                over = price - budget_max
                limitations.append(f"Exceeds specified budget by ₹{over:,.0f} (Price: ₹{price:,.0f}).")

        # 2. Category-specific spec checks
        if category == "Laptops":
            ram = specs.get("ram_gb")
            if ram:
                ram_str = f"{int(ram)}" if isinstance(ram, (int, float)) and float(ram).is_integer() else f"{ram}"
                if constraints and constraints.ram_gb and ram >= constraints.ram_gb:
                    reasons.append(f"Meets requested RAM: {ram_str} GB memory provides smooth multitasking.")
                elif ram >= 16:
                    reasons.append(f"Generous {ram_str} GB RAM suitable for software development, VMs, and data processing.")
                elif ram <= 8:
                    limitations.append(f"{ram_str} GB RAM may become a bottleneck for heavy development or multi-container workloads.")

            gpu = str(specs.get("gpu", ""))
            is_dedicated = specs.get("is_dedicated_gpu", False)
            if is_dedicated:
                reasons.append(f"Dedicated GPU: {gpu} provides hardware acceleration for ML models and 1080p/1440p gaming.")
            else:
                limitations.append("Integrated graphics: Not suitable for heavy 3D rendering or local deep learning training.")

            battery = specs.get("battery_hours")
            if battery:
                if battery >= 12.0:
                    reasons.append(f"Exceptional battery endurance: up to {battery} hours of runtime.")
                elif battery < 7.0:
                    limitations.append(f"Modest battery life ({battery} hours); will require a charger during extended university days.")

            weight = specs.get("weight_kg")
            if weight and weight > 2.1:
                limitations.append(f"Weight is {weight} kg; slightly heavy for daily campus commuting.")
            elif weight and weight <= 1.4:
                reasons.append(f"Ultra-portable chassis at {weight} kg, ideal for travel.")

        elif category == "Headphones":
            anc = specs.get("active_noise_cancellation", False)
            if anc:
                reasons.append("Active Noise Cancellation (ANC) effectively isolates ambient background distractions.")
            else:
                limitations.append("Lacks Active Noise Cancellation (passive isolation only).")
            bat = specs.get("battery_hours")
            if bat and bat >= 30:
                reasons.append(f"Long-lasting battery life of up to {bat} hours.")

        elif category == "Monitors":
            hz = specs.get("refresh_rate_hz")
            panel = specs.get("panel_type")
            if hz and hz >= 144:
                reasons.append(f"High {hz}Hz refresh rate for blur-free gaming and silky smooth window motion.")
            if panel == "OLED":
                reasons.append("Self-lit OLED panel delivers infinite contrast and true inky blacks.")

        # General rating mention
        rating = prod_dict.get("rating", 4.0)
        review_count = prod_dict.get("review_count", 0)
        if rating >= 4.5 and review_count >= 500:
            reasons.append(f"Highly rated by users ({rating}★ from {review_count:,} reviews).")

        return reasons, limitations

    def rerank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        db: Session,
        query: str,
        constraints: Optional[ExtractedConstraints] = None,
        filters: Optional[SearchFilter] = None,
        user_preference: Optional[UserPreference] = None,
        top_k: int = 10,
        enforce_hard_budget: bool = True
    ) -> List[SearchResultItem]:
        """
        Rerank candidate products using multi-factor deterministic scoring,
        enforcing budget/category constraints and attaching grounded rationale.
        """
        if not candidates:
            return []

        repo = ProductRepository(db)
        pids = [c["product_id"] for c in candidates]
        product_models = {p.id: p for p in repo.get_by_ids(pids)}

        budget_max = None
        if filters and filters.max_price is not None:
            budget_max = filters.max_price
        elif constraints and constraints.budget_max is not None:
            budget_max = constraints.budget_max

        budget_min = None
        if filters and filters.min_price is not None:
            budget_min = filters.min_price
        elif constraints and constraints.budget_min is not None:
            budget_min = constraints.budget_min

        target_category = None
        if filters and filters.category:
            target_category = filters.category
        elif constraints and constraints.category:
            target_category = constraints.category

        ranked_items = []
        for cand in candidates:
            pid = cand["product_id"]
            p_model = product_models.get(pid)
            if not p_model:
                continue

            prod_dict = repo.format_product_dict(p_model)
            price = float(prod_dict["price"])
            category = prod_dict["category"]

            # Hard Constraint 1: Category Filter
            if target_category and category.lower() != target_category.lower():
                continue  # Exclude non-matching categories

            # Hard Constraint 2: Budget Filter
            if enforce_hard_budget and budget_max is not None and price > budget_max:
                continue  # Out-of-budget products strictly excluded

            # Compute individual scores
            sem_score = float(cand.get("semantic_score", 0.0))
            kw_score = float(cand.get("keyword_score", 0.0))
            spec_score = self.ranker.calculate_spec_score(prod_dict.get("specifications", {}), constraints)
            bud_score = self.ranker.calculate_budget_score(price, budget_max, budget_min, strict_budget=enforce_hard_budget)
            pref_score = self.ranker.calculate_preference_score(prod_dict, user_preference)
            rat_score = self.ranker.calculate_rating_score(float(prod_dict.get("rating", 4.0)))

            score_breakdown = self.ranker.compute_composite_score(
                semantic_score=sem_score,
                keyword_score=kw_score,
                spec_score=spec_score,
                budget_score=bud_score,
                preference_score=pref_score,
                rating_score=rat_score
            )

            # Generate match reasons and limitations
            reasons, limits = self.extract_reasons_and_limitations(
                prod_dict=prod_dict,
                constraints=constraints,
                budget_max=budget_max
            )

            item = SearchResultItem(
                product=ProductResponse(**prod_dict),
                score=score_breakdown.final_score,
                score_breakdown=score_breakdown,
                match_reasons=reasons,
                limitations=limits
            )
            ranked_items.append(item)

        # Sort descending by final score
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        return ranked_items[:top_k]
