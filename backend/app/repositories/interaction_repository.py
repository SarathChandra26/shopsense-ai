from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.interaction import SearchHistory, SavedProduct, ProductFeedback, RecommendationHistory
from backend.app.models.product import Product

class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def record_search(
        self,
        user_id: str,
        query: str,
        search_type: str = "hybrid",
        filters_json: Optional[str] = None,
        results_count: int = 0,
        latency_ms: float = 0.0
    ) -> SearchHistory:
        rec = SearchHistory(
            user_id=user_id,
            query=query,
            search_type=search_type,
            filters_json=filters_json,
            results_count=results_count,
            latency_ms=latency_ms
        )
        self.db.add(rec)
        self.db.commit()
        return rec

    def get_search_history(self, user_id: str, limit: int = 50) -> List[SearchHistory]:
        return (
            self.db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
            .all()
        )

    def save_product(self, user_id: str, product_id: str, notes: Optional[str] = None) -> SavedProduct:
        existing = (
            self.db.query(SavedProduct)
            .filter(SavedProduct.user_id == user_id, SavedProduct.product_id == product_id)
            .first()
        )
        if existing:
            return existing

        saved = SavedProduct(user_id=user_id, product_id=product_id, notes=notes)
        self.db.add(saved)
        self.db.commit()
        self.db.refresh(saved)
        return saved

    def get_saved_products(self, user_id: str) -> List[Product]:
        saved_items = (
            self.db.query(SavedProduct)
            .filter(SavedProduct.user_id == user_id)
            .order_by(SavedProduct.created_at.desc())
            .all()
        )
        pids = [s.product_id for s in saved_items]
        if not pids:
            return []
        products = self.db.query(Product).filter(Product.id.in_(pids)).all()
        # Maintain saved order
        prod_map = {p.id: p for p in products}
        return [prod_map[pid] for pid in pids if pid in prod_map]

    def remove_saved_product(self, user_id: str, product_id: str) -> bool:
        saved = (
            self.db.query(SavedProduct)
            .filter(SavedProduct.user_id == user_id, SavedProduct.product_id == product_id)
            .first()
        )
        if not saved:
            return False
        self.db.delete(saved)
        self.db.commit()
        return True

    def record_feedback(
        self,
        user_id: str,
        product_id: str,
        feedback_type: str,
        comment: Optional[str] = None
    ) -> ProductFeedback:
        fb = ProductFeedback(
            user_id=user_id,
            product_id=product_id,
            feedback_type=feedback_type,
            comment=comment
        )
        self.db.add(fb)
        self.db.commit()
        self.db.refresh(fb)
        return fb

    def get_user_feedback(self, user_id: str) -> List[ProductFeedback]:
        return (
            self.db.query(ProductFeedback)
            .filter(ProductFeedback.user_id == user_id)
            .order_by(ProductFeedback.created_at.desc())
            .all()
        )

    def get_negative_product_ids(self, user_id: str) -> List[str]:
        """Fetch IDs of products marked 'not_useful', 'too_expensive', 'wrong_specifications', 'not_interested'."""
        negative_types = ["not_useful", "too_expensive", "wrong_specifications", "not_interested"]
        rows = (
            self.db.query(ProductFeedback.product_id)
            .filter(ProductFeedback.user_id == user_id, ProductFeedback.feedback_type.in_(negative_types))
            .all()
        )
        return list(set(r[0] for r in rows))

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Aggregate search and interaction analytics."""
        total_searches = self.db.query(func.count(SearchHistory.id)).scalar() or 0
        avg_latency = self.db.query(func.avg(SearchHistory.latency_ms)).scalar() or 0.0
        
        # Search types count
        search_types_query = (
            self.db.query(SearchHistory.search_type, func.count(SearchHistory.id))
            .group_by(SearchHistory.search_type)
            .all()
        )
        search_types_dist = {st: cnt for st, cnt in search_types_query}

        # Feedback counts
        fb_query = (
            self.db.query(ProductFeedback.feedback_type, func.count(ProductFeedback.id))
            .group_by(ProductFeedback.feedback_type)
            .all()
        )
        feedback_dist = {fb: cnt for fb, cnt in fb_query}

        # Popular categories in catalogue
        cat_counts = (
            self.db.query(Product.category, func.count(Product.id))
            .group_by(Product.category)
            .all()
        )
        category_dist = {cat: cnt for cat, cnt in cat_counts}

        return {
            "total_searches": total_searches,
            "average_latency_ms": round(float(avg_latency), 2),
            "search_types_distribution": search_types_dist,
            "feedback_distribution": feedback_dist,
            "catalogue_category_distribution": category_dist
        }
