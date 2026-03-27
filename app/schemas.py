from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginForm(BaseModel):
    username: str
    password: str


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
