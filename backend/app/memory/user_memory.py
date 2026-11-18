from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.repositories.preference_repository import PreferenceRepository
from backend.app.repositories.interaction_repository import InteractionRepository
from backend.app.schemas.preference import UserPreferenceUpdate, UserPreferenceResponse

class UserMemoryManager:
    def __init__(self, db: Session):
        self.db = db
        self.pref_repo = PreferenceRepository(db)
        self.interaction_repo = InteractionRepository(db)

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Aggregate full persistent profile: preferences, saved items, negative feedback, and recent searches."""
        pref = self.pref_repo.get_by_user_id(user_id)
        pref_dict = self.pref_repo.format_preference_dict(pref)
        saved = self.interaction_repo.get_saved_products(user_id)
        history = self.interaction_repo.get_search_history(user_id, limit=10)
        feedback = self.interaction_repo.get_user_feedback(user_id)

        return {
            "user_id": user_id,
            "preferences": pref_dict,
            "saved_products_count": len(saved),
            "recent_searches_count": len(history),
            "feedback_given_count": len(feedback),
            "rejected_products": self.interaction_repo.get_negative_product_ids(user_id)
        }

    def update_preferences(self, user_id: str, updates: UserPreferenceUpdate) -> UserPreferenceResponse:
        pref = self.pref_repo.create_or_update(user_id, updates)
        pref_dict = self.pref_repo.format_preference_dict(pref)
        return UserPreferenceResponse(**pref_dict)

    def clear_preferences(self, user_id: str) -> bool:
        return self.pref_repo.delete(user_id)
