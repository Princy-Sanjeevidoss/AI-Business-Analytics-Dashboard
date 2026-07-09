from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import crud, models, schemas
from backend.database import Base
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Business Analytics Dashboard" in response.json()["message"]


def test_login_endpoint_for_demo_user():
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add(models.Customer(id=1, name="Test Customer", email="test@example.com"))
        db.add(models.Product(id=1, name="Laptop", category="Electronics", price=1000, stock=10))
        db.add(models.Product(id=2, name="Mouse", category="Accessories", price=25, stock=4))
        db.commit()
        yield db
    finally:
        db.close()


def test_create_sale_reduces_product_stock(db_session):
    sale = schemas.SaleCreate(
        customer_id=1,
        product_id=1,
        quantity=3,
        total_amount=3000,
        sale_date="2026-07-09",
    )

    created = crud.create_sale(db_session, sale)
    product = crud.get_product(db_session, 1)

    assert created.id is not None
    assert product.stock == 7


def test_create_sale_rejects_insufficient_stock(db_session):
    sale = schemas.SaleCreate(
        customer_id=1,
        product_id=2,
        quantity=5,
        total_amount=125,
        sale_date="2026-07-09",
    )

    with pytest.raises(ValueError, match="Insufficient stock"):
        crud.create_sale(db_session, sale)

    assert crud.get_product(db_session, 2).stock == 4


def test_create_customer_rejects_duplicate_email(db_session):
    customer = schemas.CustomerCreate(
        name="Second Customer",
        email="test@example.com",
        phone="555-1111",
        city="Test City",
        join_date="2026-07-09",
    )

    with pytest.raises(ValueError, match="Duplicate customer email"):
        crud.create_customer(db_session, customer)


def test_delete_customer_removes_related_sales_and_payments(db_session):
    sale = crud.create_sale(
        db_session,
        schemas.SaleCreate(
            customer_id=1,
            product_id=1,
            quantity=3,
            total_amount=3000,
            sale_date="2026-07-09",
        ),
    )
    payment = crud.create_payment(
        db_session,
        schemas.PaymentCreate(
            customer_id=1,
            amount=3000,
            payment_method="Card",
            payment_date="2026-07-09",
        ),
    )
    payment_id = payment.id

    deleted = crud.delete_customer(db_session, 1)

    assert deleted is True
    assert crud.get_customer(db_session, 1) is None
    assert crud.get_sale(db_session, sale.id) is None
    assert crud.get_payment(db_session, payment_id) is None
    assert crud.get_product(db_session, 1).stock == 10


def test_update_sale_adjusts_stock_difference(db_session):
    created = crud.create_sale(
        db_session,
        schemas.SaleCreate(
            customer_id=1,
            product_id=1,
            quantity=3,
            total_amount=3000,
            sale_date="2026-07-09",
        ),
    )

    crud.update_sale(
        db_session,
        created.id,
        schemas.SaleCreate(
            customer_id=1,
            product_id=1,
            quantity=6,
            total_amount=6000,
            sale_date="2026-07-10",
        ),
    )

    assert crud.get_product(db_session, 1).stock == 4


def test_update_sale_moves_stock_between_products(db_session):
    created = crud.create_sale(
        db_session,
        schemas.SaleCreate(
            customer_id=1,
            product_id=1,
            quantity=3,
            total_amount=3000,
            sale_date="2026-07-09",
        ),
    )

    crud.update_sale(
        db_session,
        created.id,
        schemas.SaleCreate(
            customer_id=1,
            product_id=2,
            quantity=2,
            total_amount=50,
            sale_date="2026-07-10",
        ),
    )

    assert crud.get_product(db_session, 1).stock == 10
    assert crud.get_product(db_session, 2).stock == 2


def test_delete_sale_restores_product_stock(db_session):
    created = crud.create_sale(
        db_session,
        schemas.SaleCreate(
            customer_id=1,
            product_id=1,
            quantity=3,
            total_amount=3000,
            sale_date="2026-07-09",
        ),
    )

    deleted = crud.delete_sale(db_session, created.id)

    assert deleted is True
    assert crud.get_product(db_session, 1).stock == 10
