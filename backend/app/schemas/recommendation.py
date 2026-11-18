from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.search import SearchResultItem

class RecommendationRequest(BaseModel):
    user_id: str = "default_user"
    rec_type: str = Field(
        "best_overall",
        pattern="^(best_overall|within_budget|best_specs|budget_alternatives|similar_products|alternative_brands|best_value)$"
    )
    context_product_id: Optional[str] = None
    limit: int = Field(6, ge=1, le=50)

class RecommendationResponse(BaseModel):
    user_id: str
    rec_type: str
    items: List[SearchResultItem]
    rationale: str
