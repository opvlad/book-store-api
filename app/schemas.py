from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr

from app.models import UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime


class UserListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[UserResponse]


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
