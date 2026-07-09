from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.security import get_password_hash


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    return db.query(models.Customer).offset(skip).limit(limit).all()


def _duplicate_error(name: str) -> ValueError:
    return ValueError(f"Duplicate {name} already exists")


def _ensure_unique_customer_email(db: Session, email: str, customer_id: Optional[int] = None) -> None:
    query = db.query(models.Customer).filter(models.Customer.email == email)
    if customer_id is not None:
        query = query.filter(models.Customer.id != customer_id)
    if query.first():
        raise _duplicate_error("customer email")


def _ensure_unique_product(db: Session, product: schemas.ProductCreate, product_id: Optional[int] = None) -> None:
    query = db.query(models.Product).filter(
        and_(
            models.Product.name == product.name,
            models.Product.category == product.category,
        )
    )
    if product_id is not None:
        query = query.filter(models.Product.id != product_id)
    if query.first():
        raise _duplicate_error("product")


def _ensure_unique_employee(db: Session, employee: schemas.EmployeeCreate, employee_id: Optional[int] = None) -> None:
    query = db.query(models.Employee).filter(
        and_(
            models.Employee.name == employee.name,
            models.Employee.role == employee.role,
            models.Employee.department == employee.department,
        )
    )
    if employee_id is not None:
        query = query.filter(models.Employee.id != employee_id)
    if query.first():
        raise _duplicate_error("employee")


def _ensure_unique_sale(db: Session, sale: schemas.SaleCreate, sale_id: Optional[int] = None) -> None:
    query = db.query(models.Sale).filter(
        and_(
            models.Sale.customer_id == sale.customer_id,
            models.Sale.product_id == sale.product_id,
            models.Sale.quantity == sale.quantity,
            models.Sale.total_amount == sale.total_amount,
            models.Sale.sale_date == sale.sale_date,
        )
    )
    if sale_id is not None:
        query = query.filter(models.Sale.id != sale_id)
    if query.first():
        raise _duplicate_error("sale")


def _ensure_unique_payment(db: Session, payment: schemas.PaymentCreate, payment_id: Optional[int] = None) -> None:
    query = db.query(models.Payment).filter(
        and_(
            models.Payment.customer_id == payment.customer_id,
            models.Payment.amount == payment.amount,
            models.Payment.payment_method == payment.payment_method,
            models.Payment.payment_date == payment.payment_date,
        )
    )
    if payment_id is not None:
        query = query.filter(models.Payment.id != payment_id)
    if query.first():
        raise _duplicate_error("payment")


def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    _ensure_unique_customer_email(db, customer.email)
    db_customer = models.Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer: schemas.CustomerCreate) -> Optional[models.Customer]:
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    _ensure_unique_customer_email(db, customer.email, customer_id)
    for key, value in customer.model_dump().items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> bool:
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False
    for sale in db.query(models.Sale).filter(models.Sale.customer_id == customer_id).all():
        product = get_product(db, sale.product_id)
        if product:
            product.stock += sale.quantity
        db.delete(sale)
    db.query(models.Payment).filter(models.Payment.customer_id == customer_id).delete(synchronize_session=False)
    db.delete(db_customer)
    db.commit()
    return True


def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    _ensure_unique_product(db, product)
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductCreate) -> Optional[models.Product]:
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    _ensure_unique_product(db, product, product_id)
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    db.query(models.Sale).filter(models.Sale.product_id == product_id).delete(synchronize_session=False)
    db.delete(db_product)
    db.commit()
    return True


def get_sale(db: Session, sale_id: int) -> Optional[models.Sale]:
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()


def get_sales(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sale]:
    return db.query(models.Sale).offset(skip).limit(limit).all()


def _get_sale_product(db: Session, product_id: int) -> models.Product:
    product = get_product(db, product_id)
    if not product:
        raise ValueError("Product not found")
    return product


def _validate_sale_customer(db: Session, customer_id: int) -> None:
    if not get_customer(db, customer_id):
        raise ValueError("Customer not found")


def _require_available_stock(product: models.Product, quantity: int) -> None:
    if quantity <= 0:
        raise ValueError("Sale quantity must be greater than zero")
    if product.stock < quantity:
        raise ValueError(f"Insufficient stock for {product.name}. Available: {product.stock}, requested: {quantity}")


def create_sale(db: Session, sale: schemas.SaleCreate) -> models.Sale:
    _validate_sale_customer(db, sale.customer_id)
    product = _get_sale_product(db, sale.product_id)
    _require_available_stock(product, sale.quantity)
    _ensure_unique_sale(db, sale)

    product.stock -= sale.quantity
    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def update_sale(db: Session, sale_id: int, sale: schemas.SaleCreate) -> Optional[models.Sale]:
    db_sale = get_sale(db, sale_id)
    if not db_sale:
        return None

    _validate_sale_customer(db, sale.customer_id)
    _ensure_unique_sale(db, sale, sale_id)
    old_product = _get_sale_product(db, db_sale.product_id)
    new_product = _get_sale_product(db, sale.product_id)

    if old_product.id == new_product.id:
        available_stock = old_product.stock + db_sale.quantity
        if sale.quantity <= 0:
            raise ValueError("Sale quantity must be greater than zero")
        if available_stock < sale.quantity:
            raise ValueError(
                f"Insufficient stock for {old_product.name}. Available: {available_stock}, requested: {sale.quantity}"
        )
        old_product.stock = available_stock - sale.quantity
    else:
        _require_available_stock(new_product, sale.quantity)
        old_product.stock += db_sale.quantity
        new_product.stock -= sale.quantity

    for key, value in sale.model_dump().items():
        setattr(db_sale, key, value)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def delete_sale(db: Session, sale_id: int) -> bool:
    db_sale = get_sale(db, sale_id)
    if not db_sale:
        return False
    product = get_product(db, db_sale.product_id)
    if product:
        product.stock += db_sale.quantity
    db.delete(db_sale)
    db.commit()
    return True


def get_employee(db: Session, employee_id: int) -> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[models.Employee]:
    return db.query(models.Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
    _ensure_unique_employee(db, employee)
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeCreate) -> Optional[models.Employee]:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return None
    _ensure_unique_employee(db, employee, employee_id)
    for key, value in employee.model_dump().items():
        setattr(db_employee, key, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, employee_id: int) -> bool:
    db_employee = get_employee(db, employee_id)
    if not db_employee:
        return False
    db.delete(db_employee)
    db.commit()
    return True


def get_payment(db: Session, payment_id: int) -> Optional[models.Payment]:
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()


def get_payments(db: Session, skip: int = 0, limit: int = 100) -> List[models.Payment]:
    return db.query(models.Payment).offset(skip).limit(limit).all()


def create_payment(db: Session, payment: schemas.PaymentCreate) -> models.Payment:
    if not get_customer(db, payment.customer_id):
        raise ValueError("Customer not found")
    _ensure_unique_payment(db, payment)
    db_payment = models.Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def update_payment(db: Session, payment_id: int, payment: schemas.PaymentCreate) -> Optional[models.Payment]:
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return None
    if not get_customer(db, payment.customer_id):
        raise ValueError("Customer not found")
    _ensure_unique_payment(db, payment, payment_id)
    for key, value in payment.model_dump().items():
        setattr(db_payment, key, value)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def delete_payment(db: Session, payment_id: int) -> bool:
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        return False
    db.delete(db_payment)
    db.commit()
    return True
