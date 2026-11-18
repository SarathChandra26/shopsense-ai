from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.schemas.search import SearchResultItem, ScoreBreakdown
from backend.app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from backend.app.schemas.product import ProductResponse
from backend.app.repositories.product_repository import ProductRepository
from backend.app.repositories.preference_repository import PreferenceRepository
from backend.app.repositories.interaction_repository import InteractionRepository
from backend.app.ranking.reranker import ProductReranker
from backend.app.embeddings.embedder import get_embedder, ProductEmbedder
from backend.app.vector_store.chroma_client import get_vector_store
from backend.app.core.logging import logger

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)
        self.pref_repo = PreferenceRepository(db)
        self.interaction_repo = InteractionRepository(db)
        self.reranker = ProductReranker()
        self.vector_store = get_vector_store()
        self.embedder = get_embedder()

    def generate_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        user_id = request.user_id
        rec_type = request.rec_type
        limit = request.limit
        context_pid = request.context_product_id

        # 1. Fetch user preferences & rejected/negative feedback IDs
        pref = self.pref_repo.get_by_user_id(user_id)
        pref_dict = self.pref_repo.format_preference_dict(pref)
        negative_ids = set(self.interaction_repo.get_negative_product_ids(user_id))

        # 2. Fetch context product if provided
        context_product = self.repo.get_by_id(context_pid) if context_pid else None

        items: List[SearchResultItem] = []
        rationale = ""

        # Strategy 1: Similar Products (Content-based vector nearest neighbors)
        if rec_type == "similar_products" and context_product:
            ctx_dict = self.repo.format_product_dict(context_product)
            ctx_text = ProductEmbedder.build_searchable_text(ctx_dict)
            ctx_emb = self.embedder.encode_text(ctx_text)

            where_clause = {"category": context_product.category}
            nearest = self.vector_store.query(ctx_emb, top_k=limit + len(negative_ids) + 5, where_filter=where_clause)
            
            pids = [pid for pid, _, _ in nearest if pid != context_pid and pid not in negative_ids][:limit]
            products = {p.id: p for p in self.repo.get_by_ids(pids)}

            for pid, sim_score, _ in nearest:
                if pid in products and len(items) < limit:
                    p = products[pid]
                    p_dict = self.repo.format_product_dict(p)
                    reasons, limits = ProductReranker.extract_reasons_and_limitations(p_dict)
                    reasons.insert(0, f"Similar to {context_product.name} ({int(sim_score*100)}% match).")
                    items.append(SearchResultItem(
                        product=ProductResponse(**p_dict),
                        score=round(sim_score, 4),
                        score_breakdown=ScoreBreakdown(semantic_score=round(sim_score, 4), final_score=round(sim_score, 4)),
                        match_reasons=reasons,
                        limitations=limits
                    ))
            rationale = f"Recommending products with similar technical profile and usage characteristics to {context_product.name}."

        # Strategy 2: Budget Alternatives (Similar capabilities, but priced lower)
        elif rec_type == "budget_alternatives" and context_product:
            target_price = context_product.price * 0.80  # 20% cheaper
            ctx_dict = self.repo.format_product_dict(context_product)
            ctx_text = ProductEmbedder.build_searchable_text(ctx_dict)
            ctx_emb = self.embedder.encode_text(ctx_text)

            where_clause = {"category": context_product.category}
            nearest = self.vector_store.query(ctx_emb, top_k=40, where_filter=where_clause)

            for pid, sim_score, meta in nearest:
                if pid == context_pid or pid in negative_ids:
                    continue
                p = self.repo.get_by_id(pid)
                if p and p.price <= target_price:
                    p_dict = self.repo.format_product_dict(p)
                    savings = context_product.price - p.price
                    reasons, limits = ProductReranker.extract_reasons_and_limitations(p_dict)
                    reasons.insert(0, f"Budget alternative: Saves ₹{savings:,.0f} compared to {context_product.name}.")
                    items.append(SearchResultItem(
                        product=ProductResponse(**p_dict),
                        score=round(sim_score * 0.9, 4),
                        score_breakdown=ScoreBreakdown(semantic_score=round(sim_score, 4), budget_score=1.0, final_score=round(sim_score * 0.9, 4)),
                        match_reasons=reasons,
                        limitations=limits
                    ))
                    if len(items) >= limit:
                        break
            rationale = f"Lower-cost alternatives offering similar features to {context_product.name} while saving money."

        # Strategy 3: Alternative Brands (Same category, competing brands)
        elif rec_type == "alternative_brands" and context_product:
            ctx_dict = self.repo.format_product_dict(context_product)
            ctx_text = ProductEmbedder.build_searchable_text(ctx_dict)
            ctx_emb = self.embedder.encode_text(ctx_text)

            where_clause = {"category": context_product.category}
            nearest = self.vector_store.query(ctx_emb, top_k=40, where_filter=where_clause)

            for pid, sim_score, meta in nearest:
                if pid == context_pid or pid in negative_ids:
                    continue
                p = self.repo.get_by_id(pid)
                if p and p.brand.lower() != context_product.brand.lower():
                    p_dict = self.repo.format_product_dict(p)
                    reasons, limits = ProductReranker.extract_reasons_and_limitations(p_dict)
                    reasons.insert(0, f"Alternative brand ({p.brand}) with comparable class.")
                    items.append(SearchResultItem(
                        product=ProductResponse(**p_dict),
                        score=round(sim_score, 4),
                        score_breakdown=ScoreBreakdown(semantic_score=round(sim_score, 4), final_score=round(sim_score, 4)),
                        match_reasons=reasons,
                        limitations=limits
                    ))
                    if len(items) >= limit:
                        break
            rationale = f"Top-rated alternative brand choices competing in the {context_product.category} segment."

        # Strategy 4: Best Value (High rating, high specs relative to price)
        elif rec_type == "best_value":
            cat = pref_dict.get("preferred_categories")[0] if pref_dict.get("preferred_categories") else "Laptops"
            total, prods = self.repo.list_products(category=cat, limit=60)
            
            scored_candidates = []
            for p in prods:
                if p.id in negative_ids:
                    continue
                # Value formula: (rating * 1000) / (price / 1000)
                p_dict = self.repo.format_product_dict(p)
                val_metric = (p.rating * 10000.0) / max(1000.0, p.price)
                scored_candidates.append((p_dict, val_metric))
                
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            for p_dict, val in scored_candidates[:limit]:
                reasons, limits = ProductReranker.extract_reasons_and_limitations(p_dict)
                reasons.insert(0, f"High value-for-money index with {p_dict['rating']}★ rating at ₹{p_dict['price']:,.0f}.")
                items.append(SearchResultItem(
                    product=ProductResponse(**p_dict),
                    score=0.88,
                    score_breakdown=ScoreBreakdown(rating_score=round(p_dict["rating"]/5.0, 4), budget_score=0.9, final_score=0.88),
                    match_reasons=reasons,
                    limitations=limits
                ))
            rationale = "Products delivering the highest specifications and customer ratings per rupee spent."

        # Strategy 5, 6, 7: Best Overall / Within Budget / Best Specs (Default personalized)
        else:
            cat = pref_dict.get("preferred_categories")[0] if pref_dict.get("preferred_categories") else (context_product.category if context_product else "Laptops")
            budget_max = pref_dict.get("budget_max")
            
            total, prods = self.repo.list_products(
                category=cat,
                max_price=budget_max if rec_type == "within_budget" else None,
                limit=50
            )

            for p in prods:
                if p.id in negative_ids:
                    continue
                p_dict = self.repo.format_product_dict(p)
                reasons, limits = ProductReranker.extract_reasons_and_limitations(p_dict, budget_max=budget_max)
                if pref_dict.get("preferred_brands") and p.brand in pref_dict.get("preferred_brands"):
                    reasons.insert(0, f"Matches your preferred brand: {p.brand}.")
                
                score = round(p.rating / 5.0, 4)
                items.append(SearchResultItem(
                    product=ProductResponse(**p_dict),
                    score=score,
                    score_breakdown=ScoreBreakdown(rating_score=score, budget_score=1.0 if not budget_max or p.price <= budget_max else 0.5, final_score=score),
                    match_reasons=reasons,
                    limitations=limits
                ))
                if len(items) >= limit:
                    break
            rationale = f"Personalized recommendations based on your saved preferences, category interest in {cat}, and budget."

        return RecommendationResponse(
            user_id=user_id,
            rec_type=rec_type,
            items=items,
            rationale=rationale
        )
