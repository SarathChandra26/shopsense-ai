from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.product import ProductResponse

class ComparisonRequest(BaseModel):
    product_ids: List[str] = Field(..., min_items=2, max_items=5)

class SpecComparisonRow(BaseModel):
    spec_key: str
    label: str
    values: Dict[str, str] # product_id -> formatted_value
    is_different: bool
    winner_product_id: Optional[str] = None
    winner_reason: Optional[str] = None

class ComparisonResponse(BaseModel):
    products: List[ProductResponse]
    category: str
    specs_table: List[SpecComparisonRow]
    best_for: Dict[str, str] # e.g. "Best for Programming": "Dell XPS 15 (PROD-LAP-001)"
    tradeoffs: List[str]
    summary_verdict: str
