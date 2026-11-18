from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from backend.app.recommendations.engine import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.post("", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    engine = RecommendationEngine(db)
    return engine.generate_recommendations(request)

@router.get("/{user_id}", response_model=RecommendationResponse)
def get_user_recommendations(
    user_id: str,
    rec_type: str = Query("best_overall"),
    limit: int = Query(6, ge=1, le=50),
    db: Session = Depends(get_db)
):
    engine = RecommendationEngine(db)
    req = RecommendationRequest(
        user_id=user_id,
        rec_type=rec_type,
        limit=limit
    )
    return engine.generate_recommendations(req)
