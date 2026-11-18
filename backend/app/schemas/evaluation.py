from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EvaluationRunRequest(BaseModel):
    search_type: str = Field("hybrid_rerank", pattern="^(keyword|semantic|hybrid|hybrid_rerank|all)$")
    k: int = Field(5, ge=1, le=20)

class EvaluationMetricResult(BaseModel):
    search_type: str
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg: float
    constraint_satisfaction_rate: float
    avg_latency_ms: float
    total_queries: int

class EvaluationReportResponse(BaseModel):
    metrics: List[EvaluationMetricResult]
    comparison_summary: str
    run_timestamp: datetime
