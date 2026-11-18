from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.product import ProductResponse

class SearchFilter(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    availability: Optional[str] = None
    spec_filters: Optional[Dict[str, Any]] = None  # e.g. {"ram_gb": 16, "gpu": "RTX"}

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[SearchFilter] = None
    search_type: str = Field("hybrid", pattern="^(semantic|keyword|hybrid|hybrid_rerank)$")
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)
    user_id: Optional[str] = "default_user"

class ScoreBreakdown(BaseModel):
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    specification_score: float = 0.0
    budget_score: float = 0.0
    preference_score: float = 0.0
    rating_score: float = 0.0
    final_score: float = 0.0

class SearchResultItem(BaseModel):
    product: ProductResponse
    score: float
    score_breakdown: ScoreBreakdown
    match_reasons: List[str] = []
    limitations: List[str] = []

class SearchResponse(BaseModel):
    query: str
    search_type: str
    total_found: int
    results: List[SearchResultItem]
    latency_ms: float
    explanation: Optional[str] = None
