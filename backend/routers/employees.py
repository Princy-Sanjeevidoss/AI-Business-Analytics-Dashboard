from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[schemas.EmployeeRead])
def list_employees(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.get_employees(db)


@router.post("", response_model=schemas.EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return crud.create_employee(db, employee)


@router.put("/{employee_id}", response_model=schemas.EmployeeRead)
def update_employee(employee_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    updated = crud.update_employee(db, employee_id, employee)
    if not updated:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = crud.delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    return None
