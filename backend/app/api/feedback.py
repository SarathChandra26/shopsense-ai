from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.preference import FeedbackCreate, FeedbackResponse, SavedProductCreate
from backend.app.schemas.product import ProductResponse
from backend.app.repositories.interaction_repository import InteractionRepository
from backend.app.repositories.product_repository import ProductRepository

router = APIRouter(tags=["Interactions & Feedback"])

@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(fb_in: FeedbackCreate, db: Session = Depends(get_db)):
    repo = InteractionRepository(db)
    return repo.record_feedback(
        user_id=fb_in.user_id,
        product_id=fb_in.product_id,
        feedback_type=fb_in.feedback_type,
        comment=fb_in.comment
    )

@router.get("/feedback/{user_id}", response_model=List[FeedbackResponse])
def get_user_feedback(user_id: str, db: Session = Depends(get_db)):
    repo = InteractionRepository(db)
    return repo.get_user_feedback(user_id)

@router.get("/analytics/summary")
def get_analytics(db: Session = Depends(get_db)):
    repo = InteractionRepository(db)
    return repo.get_analytics_summary()

@router.post("/saved-products", status_code=status.HTTP_201_CREATED)
def save_product(save_in: SavedProductCreate, db: Session = Depends(get_db)):
    repo = InteractionRepository(db)
    saved = repo.save_product(save_in.user_id, save_in.product_id, save_in.notes)
    return {"message": "Product saved successfully", "id": saved.id}

@router.get("/saved-products/{user_id}", response_model=List[ProductResponse])
def list_saved_products(user_id: str, db: Session = Depends(get_db)):
    interaction_repo = InteractionRepository(db)
    product_repo = ProductRepository(db)
    saved_prods = interaction_repo.get_saved_products(user_id)
    return [ProductResponse(**product_repo.format_product_dict(p)) for p in saved_prods]

@router.delete("/saved-products/{user_id}/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_saved_product(user_id: str, product_id: str, db: Session = Depends(get_db)):
    repo = InteractionRepository(db)
    repo.remove_saved_product(user_id, product_id)
    return None

@router.get("/history/{user_id}")
def get_search_history(user_id: str, db: Session = Depends(get_db)):
    repo = InteractionRepository(db)
    history = repo.get_search_history(user_id, limit=30)
    return [
        {
            "id": h.id,
            "query": h.query,
            "search_type": h.search_type,
            "results_count": h.results_count,
            "latency_ms": h.latency_ms,
            "created_at": h.created_at
        }
        for h in history
    ]
