from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    city: Optional[str] = None
    join_date: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int


class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    price: float
    stock: int


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int


class SaleBase(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    total_amount: float
    sale_date: str


class SaleCreate(SaleBase):
    pass


class SaleRead(SaleBase):
    id: int


class EmployeeBase(BaseModel):
    name: str
    role: str
    department: Optional[str] = None
    salary: float


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase):
    id: int


class PaymentBase(BaseModel):
    customer_id: int
    amount: float
    payment_method: str
    payment_date: str


class PaymentCreate(PaymentBase):
    pass


class PaymentRead(PaymentBase):
    id: int
