from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.models import Customer, Employee, Payment, Product, Sale, User  # noqa: F401
from backend.routers import ai, analytics, auth, customers, employees, payments, prediction, products, sales

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Business Analytics Dashboard")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(employees.router)
app.include_router(payments.router)
app.include_router(analytics.router)
app.include_router(prediction.router)
app.include_router(ai.router)


@app.get("/")
def home():
    return {"message": "Welcome to AI Business Analytics Dashboard"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
