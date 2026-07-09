from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("", response_model=list[schemas.SaleRead])
def list_sales(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_sales(db)


@router.post("", response_model=schemas.SaleRead, status_code=status.HTTP_201_CREATED)
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        return crud.create_sale(db, sale)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{sale_id}", response_model=schemas.SaleRead)
def update_sale(sale_id: int, sale: schemas.SaleCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        updated = crud.update_sale(db, sale_id, sale)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not updated:
        raise HTTPException(status_code=404, detail="Sale not found")
    return updated


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = crud.delete_sale(db, sale_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sale not found")
    return None
