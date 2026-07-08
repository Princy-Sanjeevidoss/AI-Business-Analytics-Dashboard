from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat")
def chat(payload: dict, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return AIService(db=db).chat(payload.get("message", ""))


@router.post("/business-insights")
def business_insights(payload: dict, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return AIService(db=db).business_insights(payload.get("prompt", ""))
