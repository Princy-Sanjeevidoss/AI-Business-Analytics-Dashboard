import os
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend import models

MODEL_DIR = Path(__file__).resolve().parent.parent / "ml" / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


class PredictionService:
    def __init__(self, db: Session):
        self.db = db

    def train_sales_model(self) -> Dict[str, Any]:
        sales = self.db.query(models.Sale).all()
        if not sales:
            return {"message": "Not enough data to train model"}
        df = pd.DataFrame([
            {
                "customer_id": s.customer_id,
                "product_id": s.product_id,
                "quantity": s.quantity,
                "amount": float(s.total_amount),
            }
            for s in sales
        ])
        X = df[["customer_id", "product_id", "quantity"]]
        y = df["amount"]
        from sklearn.linear_model import LinearRegression

        model = LinearRegression()
        model.fit(X, y)
        joblib.dump(model, MODEL_DIR / "sales_model.joblib")
        return {"message": "Sales model trained", "model_path": str(MODEL_DIR / "sales_model.joblib")}

    def predict_next_month_revenue(self) -> Dict[str, Any]:
        model_path = MODEL_DIR / "sales_model.joblib"
        if not model_path.exists():
            self.train_sales_model()
        model = joblib.load(model_path)
        latest = self.db.query(models.Sale).order_by(models.Sale.id.desc()).first()
        if not latest:
            return {"prediction": 0.0}
        features = np.array([[latest.customer_id, latest.product_id, latest.quantity]], dtype=float)
        prediction = float(model.predict(features)[0])
        return {"prediction": round(prediction, 2)}
