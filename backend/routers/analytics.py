from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return AnalyticsService(db).summary()


@router.get("/monthly-sales")
def get_monthly_sales(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return AnalyticsService(db).monthly_sales()


@router.get("/top-products")
def get_top_products(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return AnalyticsService(db).top_products()


@router.get("/payment-methods")
def get_payment_methods(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return AnalyticsService(db).payment_methods()
