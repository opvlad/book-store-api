from typing import List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from fastapi_filter.contrib.sqlalchemy import Filter

from app.models import UserRole, UserStatus, Order, OrderStatus, DeliveryType


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginForm(BaseModel):
    username: str
    password: str


# USERS


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime


class UserListPaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[UserResponse]


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    email: EmailStr
    password: str


class UserCreateInDB(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    email: EmailStr
    password_hash: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str | None = None
    email: EmailStr | None = None


class UserUpdateAsAdmin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: UserStatus


# AUTHORS


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bio: str | None = None
    birth_date: date


class AuthorListPaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[AuthorResponse]


class AuthorCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    bio: str | None = None
    birth_date: datetime


class AuthorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    bio: str | None = None
    birth_date: date | None = None


# BOOKS


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    price: float
    stock_quantity: int
    author_id: int


class BookListPaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[BookResponse]


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(default=0, ge=0)
    author_id: int


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    author_id: int | None = Field(default=None)


# ORDERS


class OrderFilter(Filter):
    user_id: int | None = None
    status: OrderStatus | None = None
    delivery_type: DeliveryType | None = None

    total_amount__lt: Decimal | None = None
    total_amount__lte: Decimal | None = None
    total_amount__gt: Decimal | None = None
    total_amount__gte: Decimal | None = None

    priority__lt: float | None = None
    priority__lte: float | None = None
    priority__gt: float | None = None
    priority__gte: float | None = None

    order_by: list[str] = ["+id"]

    class Constants(Filter.Constants):
        model = Order


class OrderItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: int
    quantity: int = Field(..., gt=0)


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    items: List[OrderItems]
    status: OrderStatus
    total_amount: Decimal
    delivery_type: DeliveryType
    note: str | None = None


class OrderAdminResponse(OrderResponse):
    user_id: int
    priority: float
    created_at: datetime


class OrderListPaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[OrderResponse]


class OrderAdminListPaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[OrderAdminResponse]


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[OrderItems] = Field(..., min_length=1)
    delivery_type: DeliveryType = DeliveryType.STANDARD
    note: str | None = None


class OrderCreateInDB(OrderCreate):
    model_config = ConfigDict(extra="forbid")

    user_id: int
    status: OrderStatus
    total_amount: Decimal
    priority: float


class OrderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[OrderItems] | None = None
    status: OrderStatus | None = None
    note: str | None = None


class OrderUpdateInDB(OrderUpdate):
    model_config = ConfigDict(extra="forbid")

    total_amount: Decimal | None = None
    priority: float | None = None
