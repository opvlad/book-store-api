from fastapi import APIRouter, HTTPException

from app.dependencies import sessionDep
from app.schemas import LoginForm, UserResponse, UserCreate
from app.services import (
    login_user as service_login_user,
    register_user as service_register_user,
)
from app.exeptions import UserNotFoundError, UnauthorizedError, DuplicateFieldError

router = APIRouter()


@router.post("/login")
async def login(db: sessionDep, credentials: LoginForm):
    try:
        token = await service_login_user(db, credentials)
        return token
    except (UserNotFoundError, UnauthorizedError):
        raise HTTPException(status_code=401, detail="Incorrect username or password")


@router.post("/register", response_model=UserResponse)
async def register_user(db: sessionDep, user: UserCreate):
    try:
        result = await service_register_user(db, user)
        return result
    except DuplicateFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))
