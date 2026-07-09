from collections import Counter
from typing import Any, Dict

import requests
from sqlalchemy.orm import Session

from backend import models
from backend.config import OPENAI_API_KEY


class AIService:
    def __init__(self, db: Session | None = None, api_key: str | None = None):
        self.db = db
        self.api_key = api_key or OPENAI_API_KEY

    def _business_snapshot(self) -> Dict[str, Any]:
        if not self.db:
            return {}

        sales = self.db.query(models.Sale).all()
        products = self.db.query(models.Product).all()
        customers = self.db.query(models.Customer).all()
        employees = self.db.query(models.Employee).all()
        payments = self.db.query(models.Payment).all()

        product_by_id = {product.id: product for product in products}
        customer_by_id = {customer.id: customer for customer in customers}
        product_units = Counter()
        customer_revenue = Counter()
        for sale in sales:
            product_units[sale.product_id] += sale.quantity
            customer_revenue[sale.customer_id] += float(sale.total_amount)

        top_product_id, top_product_units = product_units.most_common(1)[0] if product_units else (None, 0)
        top_customer_id, top_customer_total = customer_revenue.most_common(1)[0] if customer_revenue else (None, 0)
        low_stock = sorted(products, key=lambda product: product.stock)[:5]

        return {
            "sales_count": len(sales),
            "total_revenue": sum(float(sale.total_amount) for sale in sales),
            "customers_count": len(customers),
            "products_count": len(products),
            "total_stock": sum(product.stock for product in products),
            "low_stock": low_stock,
            "employees_count": len(employees),
            "total_payroll": sum(float(employee.salary) for employee in employees),
            "payments_count": len(payments),
            "total_payments": sum(float(payment.amount) for payment in payments),
            "top_product": product_by_id.get(top_product_id),
            "top_product_units": top_product_units,
            "top_customer": customer_by_id.get(top_customer_id),
            "top_customer_total": top_customer_total,
        }

    def _snapshot_prompt(self) -> str:
        snapshot = self._business_snapshot()
        if not snapshot:
            return "No local business database is available."

        top_product = snapshot["top_product"]
        top_customer = snapshot["top_customer"]
        low_stock = ", ".join(f"{product.name}: {product.stock}" for product in snapshot["low_stock"]) or "none"
        return (
            "You are an AI business analytics assistant. Answer using this live dashboard snapshot. "
            f"Revenue: ${snapshot['total_revenue']:,.2f}. Sales: {snapshot['sales_count']}. "
            f"Customers: {snapshot['customers_count']}. Products: {snapshot['products_count']}. "
            f"Total stock: {snapshot['total_stock']}. Low stock: {low_stock}. "
            f"Top product: {top_product.name if top_product else 'none'} "
            f"({snapshot['top_product_units']} units). "
            f"Top customer: {top_customer.name if top_customer else 'none'} "
            f"(${snapshot['top_customer_total']:,.2f}). "
            "Keep replies concise, practical, and tied to the provided data."
        )

    def chat(self, message: str) -> Dict[str, Any]:
        cleaned_msg = message.strip().lower()

        if not cleaned_msg:
            return {"reply": "Ask me about revenue, sales, inventory, customers, payments, payroll, or forecasts."}

        # If an API key is available, enrich the model with local dashboard data.
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
                        "messages": [
                            {"role": "system", "content": self._snapshot_prompt()},
                            {"role": "user", "content": message},
                        ],
                        "temperature": 0.2,
                    },
                    timeout=20,
                )
                if response.status_code == 200:
                    data = response.json()
                    return {"reply": data["choices"][0]["message"]["content"]}
            except Exception:
                # Fall through to offline local analytics on failure.
                pass

        if not self.db:
            return {"reply": "AI is offline. Please initialize with a database session to use local analytics chat."}

        try:
            snapshot = self._business_snapshot()

            if any(k in cleaned_msg for k in ["low stock", "reorder", "running low", "shortage"]):
                low_stock = snapshot["low_stock"]
                if not low_stock:
                    return {"reply": "**Inventory:** There are no products in the database yet."}
                items = "\n".join(f"- **{product.name}**: {product.stock} units left" for product in low_stock)
                return {"reply": f"**Low Stock Watch:** These products need the closest attention:\n{items}"}

            if any(k in cleaned_msg for k in ["top product", "best product", "popular product", "most sold"]):
                product = snapshot["top_product"]
                if not product:
                    return {"reply": "**Top Product:** No sales have been recorded yet."}
                return {
                    "reply": f"**Top Product:** **{product.name}** is currently leading with **{snapshot['top_product_units']} units sold**."
                }

            if any(k in cleaned_msg for k in ["revenue", "sale", "sold", "earn", "transaction"]):
                average_sale = snapshot["total_revenue"] / snapshot["sales_count"] if snapshot["sales_count"] else 0
                return {
                    "reply": (
                        f"**Sales Analytics:** You have **{snapshot['sales_count']}** sales transactions and "
                        f"**${snapshot['total_revenue']:,.2f}** in total revenue. "
                        f"Average transaction value is **${average_sale:,.2f}**."
                    )
                }

            if any(k in cleaned_msg for k in ["customer", "client", "buyer", "user"]):
                customer = snapshot["top_customer"]
                top_text = (
                    f" Top customer by revenue is **{customer.name}** at **${snapshot['top_customer_total']:,.2f}**."
                    if customer
                    else ""
                )
                return {"reply": f"**Customer Directory:** There are **{snapshot['customers_count']}** registered customers.{top_text}"}

            if any(k in cleaned_msg for k in ["product", "item", "inventory", "stock"]):
                return {
                    "reply": (
                        f"**Inventory:** You manage **{snapshot['products_count']}** products with "
                        f"**{snapshot['total_stock']}** total units in stock. Ask for **low stock** to see reorder priorities."
                    )
                }

            if any(k in cleaned_msg for k in ["employee", "staff", "salary", "payroll", "wage"]):
                return {
                    "reply": (
                        f"**Human Resources:** The company has **{snapshot['employees_count']}** employees. "
                        f"Combined payroll is **${snapshot['total_payroll']:,.2f}**."
                    )
                }

            if any(k in cleaned_msg for k in ["payment", "card", "cash", "method"]):
                return {
                    "reply": (
                        f"**Payments:** **{snapshot['payments_count']}** payments are logged, totaling "
                        f"**${snapshot['total_payments']:,.2f}**."
                    )
                }

            if any(k in cleaned_msg for k in ["forecast", "predict", "future", "next month"]):
                from backend.services.prediction_service import PredictionService

                predictor = PredictionService(self.db)
                res = predictor.predict_next_month_revenue()
                pred_val = res.get("prediction", 0.0)
                return {"reply": f"**ML Forecasting:** Projected revenue for next month is **${pred_val:,.2f}**."}

            if any(k in cleaned_msg for k in ["hi", "hello", "hey", "help", "greet"]):
                return {
                    "reply": (
                        "**AI Business Assistant:** I can answer questions about revenue, stock, low-stock products, "
                        "customers, payments, payroll, and forecasts."
                    )
                }

            return {
                "reply": (
                    "**Data Assistant:** Try asking:\n"
                    "- *'How much revenue have we made?'*\n"
                    "- *'Which products are low stock?'*\n"
                    "- *'What is our top product?'*\n"
                    "- *'Show me employee payroll statistics.'*\n"
                    "- *'What is our sales forecast for next month?'*"
                )
            }
        except Exception as e:
            return {"reply": f"Error running local query: {str(e)}"}

    def business_insights(self, prompt: str) -> Dict[str, Any]:
        return self.chat(prompt)
