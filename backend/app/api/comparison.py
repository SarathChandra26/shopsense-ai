from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.comparison import ComparisonRequest, ComparisonResponse
from backend.app.comparison.comparator import ProductComparator

router = APIRouter(prefix="/compare", tags=["Comparison"])

@router.post("", response_model=ComparisonResponse)
def compare_products(request: ComparisonRequest, db: Session = Depends(get_db)):
    comparator = ProductComparator(db)
    try:
        return comparator.compare_products(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
