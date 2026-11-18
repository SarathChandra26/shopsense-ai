from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.evaluation import EvaluationRunRequest, EvaluationMetricResult, EvaluationReportResponse
from backend.app.evaluation.evaluator import run_evaluation, evaluate_all_methods
from backend.app.models.evaluation import EvaluationRun

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.post("/run", response_model=EvaluationReportResponse)
def trigger_evaluation_run(request: EvaluationRunRequest, db: Session = Depends(get_db)):
    if request.search_type == "all":
        return evaluate_all_methods(db, k=request.k)
    else:
        metric = run_evaluation(request.search_type, db, k=request.k)
        return EvaluationReportResponse(
            metrics=[metric],
            comparison_summary=f"Evaluation executed for {request.search_type} (k={request.k}).",
            run_timestamp=metric.created_at if hasattr(metric, "created_at") else None
        )

@router.get("/results", response_model=List[Dict[str, Any]])
def get_evaluation_history(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "run_name": r.run_name,
            "search_type": r.search_type,
            "precision_at_k": r.precision_at_k,
            "recall_at_k": r.recall_at_k,
            "mrr": r.mrr,
            "ndcg": r.ndcg,
            "constraint_satisfaction_rate": r.constraint_satisfaction_rate,
            "avg_latency_ms": r.avg_latency_ms,
            "total_test_queries": r.total_test_queries,
            "created_at": r.created_at
        }
        for r in runs
    ]
