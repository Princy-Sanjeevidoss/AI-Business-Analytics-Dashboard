from io import BytesIO
from typing import Callable

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.dependencies import get_current_user

router = APIRouter(prefix="/import", tags=["import"])


IMPORT_CONFIG: dict[str, tuple[type, Callable]] = {
    "customers": (schemas.CustomerCreate, crud.create_customer),
    "products": (schemas.ProductCreate, crud.create_product),
    "sales": (schemas.SaleCreate, crud.create_sale),
    "employees": (schemas.EmployeeCreate, crud.create_employee),
    "payments": (schemas.PaymentCreate, crud.create_payment),
}

COLUMN_ALIASES = {
    "total_price": "total_amount",
    "amount_paid": "amount",
    "method": "payment_method",
    "payment_method": "payment_method",
    "date_ordered": "sale_date",
    "order_date": "sale_date",
    "payment_date": "payment_date",
    "join_date": "join_date",
    "full_name": "name",
    "product_name": "name",
    "stock_level": "stock",
    "unit_price": "price",
}


def _normalize_column(column: str) -> str:
    normalized = column.strip().lower().replace(" ", "_").replace("-", "_")
    return COLUMN_ALIASES.get(normalized, normalized)


def _normalize_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    return value


async def _read_file(file: UploadFile) -> pd.DataFrame:
    filename = (file.filename or "").lower()
    contents = await file.read()

    if filename.endswith(".csv"):
        return pd.read_csv(BytesIO(contents))

    if filename.endswith((".xlsx", ".xls")):
        try:
            return pd.read_excel(BytesIO(contents))
        except ImportError as exc:
            raise HTTPException(
                status_code=400,
                detail="Excel upload needs openpyxl installed. CSV upload is ready now.",
            ) from exc

    raise HTTPException(status_code=400, detail="Please upload a CSV, XLSX, or XLS file.")


@router.post("/{entity}")
async def import_records(
    entity: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if entity not in IMPORT_CONFIG:
        raise HTTPException(status_code=404, detail="Import type not found")

    schema_class, create_fn = IMPORT_CONFIG[entity]
    frame = await _read_file(file)
    frame = frame.rename(columns={column: _normalize_column(str(column)) for column in frame.columns})

    imported = 0
    errors: list[str] = []

    for index, row in frame.iterrows():
        row_number = index + 2
        payload = {key: _normalize_value(value) for key, value in row.to_dict().items()}
        payload = {key: value for key, value in payload.items() if value is not None}

        try:
            record = schema_class.model_validate(payload)
            create_fn(db, record)
            imported += 1
        except (ValidationError, ValueError, SQLAlchemyError) as exc:
            db.rollback()
            errors.append(f"Row {row_number}: {str(exc).splitlines()[0]}")

    return {
        "imported": imported,
        "skipped": len(errors),
        "errors": errors[:10],
    }
