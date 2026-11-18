from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.preference import UserPreferenceUpdate, UserPreferenceResponse
from backend.app.repositories.preference_repository import PreferenceRepository

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.get("/{user_id}", response_model=UserPreferenceResponse)
def get_preferences(user_id: str, db: Session = Depends(get_db)):
    repo = PreferenceRepository(db)
    pref = repo.get_by_user_id(user_id)
    return UserPreferenceResponse(**repo.format_preference_dict(pref))

@router.put("/{user_id}", response_model=UserPreferenceResponse)
def update_preferences(user_id: str, updates: UserPreferenceUpdate, db: Session = Depends(get_db)):
    repo = PreferenceRepository(db)
    pref = repo.create_or_update(user_id, updates)
    return UserPreferenceResponse(**repo.format_preference_dict(pref))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preferences(user_id: str, db: Session = Depends(get_db)):
    repo = PreferenceRepository(db)
    repo.delete(user_id)
    return None
