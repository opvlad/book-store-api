from fastapi import APIRouter, HTTPException

from app.dependencies import sessionDep
from app.schemas import LoginForm, UserResponse, UserCreate, Token
from app.services import (
    login_user as service_login_user,
    register_user as service_register_user,
)
from app.exceptions import UserNotFoundError, UnauthorizedError, DuplicateFieldError


router = APIRouter()


@router.post("/login")
async def login(db: sessionDep, credentials: LoginForm):
    try:
        access_token = await service_login_user(db, credentials)
        return Token(access_token=access_token)
    except (UserNotFoundError, UnauthorizedError):
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@router.post("/register", response_model=UserResponse)
async def register_user(db: sessionDep, user: UserCreate):
    try:
        return await service_register_user(db, user)
    except DuplicateFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))
