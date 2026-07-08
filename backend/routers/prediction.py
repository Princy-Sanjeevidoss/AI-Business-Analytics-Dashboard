from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.services.prediction_service import PredictionService

router = APIRouter(prefix="/prediction", tags=["prediction"])


@router.post("/train")
def train_model(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return PredictionService(db).train_sales_model()


@router.get("/next-month-revenue")
def next_month_revenue(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return PredictionService(db).predict_next_month_revenue()
