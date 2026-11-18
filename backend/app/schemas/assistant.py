from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.search import SearchResultItem

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str = "default_user"
    session_id: Optional[str] = "default_session"
    history: Optional[List[ChatMessage]] = []

class ExtractedConstraints(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None
    budget_max: Optional[float] = None
    budget_min: Optional[float] = None
    ram_gb: Optional[float] = None
    intended_usage: Optional[str] = None
    raw_keywords: List[str] = []

class ChatResponse(BaseModel):
    reply: str
    intent: str
    constraints: ExtractedConstraints
    retrieved_products: List[SearchResultItem] = []
    tradeoffs: List[str] = []
    grounded_in_catalogue: bool = True
    llm_source: str # "ollama" or "rule_grounded_engine"
