from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.app.database.session import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_name = Column(String(100), nullable=False)
    search_type = Column(String(50), nullable=False)  # keyword, semantic, hybrid, hybrid_rerank
    precision_at_k = Column(Float, nullable=False)
    recall_at_k = Column(Float, nullable=False)
    mrr = Column(Float, nullable=False)
    ndcg = Column(Float, nullable=False)
    constraint_satisfaction_rate = Column(Float, nullable=False)
    avg_latency_ms = Column(Float, nullable=False)
    total_test_queries = Column(Integer, nullable=False)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
