import json
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.preference import UserPreference
from backend.app.schemas.preference import UserPreferenceUpdate

class PreferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> Optional[UserPreference]:
        return self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

    def create_or_update(self, user_id: str, pref_in: UserPreferenceUpdate) -> UserPreference:
        pref = self.get_by_user_id(user_id)
        if not pref:
            pref = UserPreference(user_id=user_id)
            self.db.add(pref)
            self.db.flush()

        if pref_in.preferred_categories is not None:
            pref.preferred_categories = ", ".join(pref_in.preferred_categories)
        if pref_in.budget_min is not None:
            pref.budget_min = pref_in.budget_min
        if pref_in.budget_max is not None:
            pref.budget_max = pref_in.budget_max
        if pref_in.preferred_brands is not None:
            pref.preferred_brands = ", ".join(pref_in.preferred_brands)
        if pref_in.intended_usage is not None:
            pref.intended_usage = pref_in.intended_usage
        if pref_in.preferred_specs is not None:
            pref.preferred_specs = json.dumps(pref_in.preferred_specs)

        self.db.commit()
        self.db.refresh(pref)
        return pref

    def delete(self, user_id: str) -> bool:
        pref = self.get_by_user_id(user_id)
        if not pref:
            return False
        self.db.delete(pref)
        self.db.commit()
        return True

    def format_preference_dict(self, pref: Optional[UserPreference]) -> Dict[str, Any]:
        if not pref:
            return {
                "preferred_categories": [],
                "budget_min": None,
                "budget_max": None,
                "preferred_brands": [],
                "intended_usage": None,
                "preferred_specs": {},
                "updated_at": None
            }
        
        cats = [c.strip() for c in pref.preferred_categories.split(",") if c.strip()] if pref.preferred_categories else []
        brands = [b.strip() for b in pref.preferred_brands.split(",") if b.strip()] if pref.preferred_brands else []
        
        specs = {}
        if pref.preferred_specs:
            try:
                specs = json.loads(pref.preferred_specs)
            except Exception:
                specs = {}

        return {
            "user_id": pref.user_id,
            "preferred_categories": cats,
            "budget_min": pref.budget_min,
            "budget_max": pref.budget_max,
            "preferred_brands": brands,
            "intended_usage": pref.intended_usage,
            "preferred_specs": specs,
            "updated_at": pref.updated_at
        }
