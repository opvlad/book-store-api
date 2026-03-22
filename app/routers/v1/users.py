from fastapi import APIRouter, HTTPException

from app import services
from app.dependencies import sessionDep
from app.schemas import UserResponse, UserListResponse

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
