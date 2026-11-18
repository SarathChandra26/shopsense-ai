from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.schemas.assistant import ChatRequest, ChatResponse
from backend.app.assistant.grounded_assistant import GroundedShoppingAssistant

router = APIRouter(prefix="/assistant", tags=["Assistant"])

@router.post("/chat", response_model=ChatResponse)
def assistant_chat(request: ChatRequest, db: Session = Depends(get_db)):
    assistant = GroundedShoppingAssistant(db)
    return assistant.process_chat(request)
