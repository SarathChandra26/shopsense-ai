from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class UserPreferenceUpdate(BaseModel):
    preferred_categories: Optional[List[str]] = None
    budget_min: Optional[float] = Field(None, ge=0)
    budget_max: Optional[float] = Field(None, ge=0)
    preferred_brands: Optional[List[str]] = None
    intended_usage: Optional[str] = None
    preferred_specs: Optional[Dict[str, Any]] = None

class UserPreferenceResponse(BaseModel):
    user_id: str
    preferred_categories: List[str] = []
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    preferred_brands: List[str] = []
    intended_usage: Optional[str] = None
    preferred_specs: Dict[str, Any] = {}
    updated_at: Optional[datetime] = None

class FeedbackCreate(BaseModel):
    user_id: str = "default_user"
    product_id: str
    feedback_type: str = Field(
        ...,
        pattern="^(useful|not_useful|too_expensive|wrong_specifications|already_purchased|not_interested)$"
    )
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    user_id: str
    product_id: str
    feedback_type: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SavedProductCreate(BaseModel):
    user_id: str = "default_user"
    product_id: str
    notes: Optional[str] = None
