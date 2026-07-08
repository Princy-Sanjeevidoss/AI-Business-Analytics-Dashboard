from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=list[schemas.PaymentRead])
def list_payments(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_payments(db)


@router.post("", response_model=schemas.PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_payment(db, payment)


@router.put("/{payment_id}", response_model=schemas.PaymentRead)
def update_payment(payment_id: int, payment: schemas.PaymentCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    updated = crud.update_payment(db, payment_id, payment)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = crud.delete_payment(db, payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return None
