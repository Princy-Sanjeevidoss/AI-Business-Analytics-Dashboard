import os
from typing import Any, Dict

import requests
from sqlalchemy.orm import Session

from backend import models
from backend.config import OPENAI_API_KEY


class AIService:
    def __init__(self, db: Session | None = None, api_key: str | None = None):
        self.db = db
        self.api_key = api_key or OPENAI_API_KEY

    def chat(self, message: str) -> Dict[str, Any]:
        cleaned_msg = message.strip().lower()

        # If API key is available, attempt to use OpenAI
        if self.api_key:
            try:
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": message}],
                        "temperature": 0.2,
                    },
                    timeout=20,
                )
                if response.status_code == 200:
                    data = response.json()
                    return {"reply": data["choices"][0]["message"]["content"]}
            except Exception:
                # Fall through to offline mock analysis on failure
                pass

        # Database-aware offline query handler (Fallback)
        if not self.db:
            return {"reply": "AI is offline. Please initialize with a database session to use local analytics chat."}

        try:
            if any(k in cleaned_msg for k in ["revenue", "sale", "sold", "earn", "transaction"]):
                sales_count = self.db.query(models.Sale).count()
                total_rev = sum(float(s.total_amount) for s in self.db.query(models.Sale).all())
                return {
                    "reply": f"📊 **Sales Analytics:** Currently, there are **{sales_count}** sales transactions in the system. The total accumulated revenue is **${total_rev:,.2f}**."
                }

            elif any(k in cleaned_msg for k in ["customer", "client", "buyer", "user"]):
                cust_count = self.db.query(models.Customer).count()
                cities = [c.city for c in self.db.query(models.Customer).all() if c.city]
                city_summary = f" spanning cities like {', '.join(set(cities[:3]))}" if cities else ""
                return {
                    "reply": f"👥 **Customer Directory:** There are **{cust_count}** registered customers in the database{city_summary}."
                }

            elif any(k in cleaned_msg for k in ["product", "item", "inventory", "stock"]):
                prod_count = self.db.query(models.Product).count()
                total_stock = sum(p.stock for p in self.db.query(models.Product).all())
                return {
                    "reply": f"📦 **Inventory:** We manage **{prod_count}** unique products. Total inventory stock level across all items is **{total_stock}** units."
                }

            elif any(k in cleaned_msg for k in ["employee", "staff", "salary", "payroll", "wage"]):
                emp_count = self.db.query(models.Employee).count()
                total_payroll = sum(float(e.salary) for e in self.db.query(models.Employee).all())
                return {
                    "reply": f"💼 **Human Resources:** The company has **{emp_count}** employees on staff. The combined monthly payroll is **${total_payroll:,.2f}**."
                }

            elif any(k in cleaned_msg for k in ["payment", "card", "cash", "method"]):
                pay_count = self.db.query(models.Payment).count()
                total_payments = sum(float(p.amount) for p in self.db.query(models.Payment).all())
                return {
                    "reply": f"💳 **Transactions:** A total of **{pay_count}** payments have been logged, amounting to **${total_payments:,.2f}**."
                }

            elif any(k in cleaned_msg for k in ["forecast", "predict", "future", "next month"]):
                from backend.services.prediction_service import PredictionService
                predictor = PredictionService(self.db)
                res = predictor.predict_next_month_revenue()
                pred_val = res.get("prediction", 0.0)
                return {
                    "reply": f"🔮 **ML Forecasting:** Based on our regression models, the projected revenue for next month is **${pred_val:,.2f}**."
                }

            elif any(k in cleaned_msg for k in ["hi", "hello", "hey", "greet"]):
                return {
                    "reply": "👋 Hello! I am your AI Business Assistant. Ask me questions about your revenue, sales, customers, products, employees, or future forecasts."
                }

            else:
                return {
                    "reply": "🔍 **Data Assistant:** I can help you analyze your business database. Try asking:\n"
                             "- *'How much revenue have we made?'*\n"
                             "- *'How many customers do we have?'*\n"
                             "- *'What is our current product stock level?'*\n"
                             "- *'Show me employee payroll statistics.'*\n"
                             "- *'What is our sales forecast for next month?'*"
                }
        except Exception as e:
            return {"reply": f"Error running local query: {str(e)}"}

    def business_insights(self, prompt: str) -> Dict[str, Any]:
        return self.chat(prompt)
