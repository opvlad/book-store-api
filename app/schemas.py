from typing import List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models import UserRole, OrderStatus


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


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    book_id: int
    status: OrderStatus
    quantity: int = Field(..., gt=0)
    total_amount: float
    note: str | None = None
    created_at: datetime


class OrderListPaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[OrderResponse]


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_id: int
    quantity: int = Field(..., gt=0)
    note: str | None = None


class OrderCreateInDB(OrderCreate):
    model_config = ConfigDict(extra="forbid")

    user_id: int
    status: OrderStatus
    total_amount: Decimal


class OrderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_id: int
    quantity: int = Field(..., gt=0)
    status: OrderStatus
    note: str | None = None
