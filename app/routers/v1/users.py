from fastapi import APIRouter, HTTPException

from app import services
from app.dependencies import sessionDep
from app.schemas import UserResponse, UserListResponse, UserCreate, UserUpdate
from app.exeptions import UserNotFoundError, DuplicateFieldError


router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_details(db: sessionDep, user_id: int):
    result = await services.get_user_details(user_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.get("", response_model=UserListResponse)
async def list_users(db: sessionDep, offset: int = 0, limit: int = 100):
    result = await services.get_users(db, offset, limit)
    return result


@router.post("", response_model=UserResponse)
async def register_user(db: sessionDep, user: UserCreate):
    try:
        result = await services.create_user(db, user)
        return result
    except ValueError as e:
        print(user.model_dump())
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}", response_model=UserResponse)
async def modify_user(db: sessionDep, user_id: int, user: UserUpdate):
    try:
        result = await services.update_user(db, user_id, user)
        return result
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DuplicateFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def remove_user(db: sessionDep, user_id: int):
    try:
        await services.delete_user(db, user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
