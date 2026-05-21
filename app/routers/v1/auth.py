from fastapi import APIRouter

from app.dependencies import sessionDep
from app.schemas import LoginForm, UserResponse, UserCreate, Token
from app.services import (
    login_user as service_login_user,
    register_user as service_register_user,
)


router = APIRouter()


@router.post("/login")
async def login(db: sessionDep, credentials: LoginForm):
    access_token = await service_login_user(db, credentials)
    return Token(access_token=access_token)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(db: sessionDep, user: UserCreate):
    return await service_register_user(db, user)
