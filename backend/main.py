from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.database import Base, engine
from backend.models import Customer, Employee, Payment, Product, Sale, User  # noqa: F401
from backend.routers import ai, analytics, auth, customers, employees, import_data, payments, prediction, products, sales
from backend.seed import seed_data

Base.metadata.create_all(bind=engine)
seed_data()

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
app.include_router(import_data.router)
app.include_router(analytics.router)
app.include_router(prediction.router)
app.include_router(ai.router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/")
def home():
    return {"message": "Welcome to AI Business Analytics Dashboard"}


@app.get("/login")
def login_page():
    return RedirectResponse(url="/app/login.html")


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
