from collections import Counter
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy.orm import Session

from backend import models


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self) -> Dict[str, Any]:
        customers = self.db.query(models.Customer).count()
        products = self.db.query(models.Product).count()
        sales = self.db.query(models.Sale).count()
        employees = self.db.query(models.Employee).count()
        payments = self.db.query(models.Payment).count()
        revenue = sum(float(s.total_amount) for s in self.db.query(models.Sale).all())
        return {
            "total_revenue": round(revenue, 2),
            "total_customers": customers,
            "total_sales": sales,
            "total_products": products,
            "total_employees": employees,
            "total_payments": payments,
        }

    def monthly_sales(self) -> List[Dict[str, Any]]:
        sales = self.db.query(models.Sale).all()
        if not sales:
            return []
        df = pd.DataFrame([
            {"sale_date": s.sale_date, "amount": float(s.total_amount)} for s in sales
        ])
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
        df = df.dropna(subset=["sale_date"])
        if df.empty:
            return []
        monthly = df.groupby(df["sale_date"].dt.strftime("%Y-%m"))["amount"].sum().reset_index()
        return [{"month": row[0], "revenue": round(float(row[1]), 2)} for row in monthly.itertuples(index=False)]

    def top_products(self) -> List[Dict[str, Any]]:
        sales = self.db.query(models.Sale).all()
        counts = Counter(s.product_id for s in sales)
        result = []
        for product_id, qty in counts.most_common(5):
            product = self.db.query(models.Product).filter(models.Product.id == product_id).first()
            result.append({"product": product.name if product else f"Product {product_id}", "sales": qty})
        return result

    def payment_methods(self) -> List[Dict[str, Any]]:
        payments = self.db.query(models.Payment).all()
        if not payments:
            return []
        counts = Counter(p.payment_method for p in payments)
        return [{"method": method, "count": count} for method, count in counts.items()]
