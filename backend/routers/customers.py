from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[schemas.CustomerRead])
def list_customers(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_customers(db)


@router.post("", response_model=schemas.CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_customer(db, customer)


@router.put("/{customer_id}", response_model=schemas.CustomerRead)
def update_customer(customer_id: int, customer: schemas.CustomerCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    updated = crud.update_customer(db, customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = crud.delete_customer(db, customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return None
