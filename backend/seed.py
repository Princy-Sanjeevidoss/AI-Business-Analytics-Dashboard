import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Customer, Employee, Payment, Product, Sale, User
from backend.security import get_password_hash


def _read_csv_rows(filename: str):
    path = Path(__file__).resolve().parent.parent / "data" / filename
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def seed_data():
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(username="admin", email="admin@example.com", hashed_password=get_password_hash("admin123"), full_name="Admin User"))
        if db.query(Customer).count() == 0:
            for row in _read_csv_rows("customers.csv"):
                db.add(Customer(name=row["name"], email=row["email"], phone=row["phone"], city=row["city"], join_date=row["join_date"]))
        if db.query(Product).count() == 0:
            for row in _read_csv_rows("products.csv"):
                db.add(Product(name=row["product_name"], category=row["category"], price=float(row["price"]), stock=int(row["stock"])))
        if db.query(Sale).count() == 0:
            for row in _read_csv_rows("sales.csv"):
                db.add(Sale(customer_id=int(row["customer_id"]), product_id=int(row["product_id"]), quantity=int(row["quantity"]), total_amount=float(row["total_amount"]), sale_date=str(row["sale_date"])))
        if db.query(Employee).count() == 0:
            db.add_all([
                Employee(name="Asha", role="Manager", department="Sales", salary=75000),
                Employee(name="Bharath", role="Analyst", department="Analytics", salary=65000),
            ])
        if db.query(Payment).count() == 0:
            db.add_all([
                Payment(customer_id=1, amount=65000, payment_method="Card", payment_date="2025-06-01"),
                Payment(customer_id=2, amount=4000, payment_method="Cash", payment_date="2025-06-02"),
            ])
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
