from fastapi import APIRouter, HTTPException
from cashews import cache

from app import services
from app.dependencies import sessionDep
from app.schemas import UserResponse, UserListResponse, UserUpdate
from app.exeptions import UserNotFoundError, DuplicateFieldError


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_me(db: sessionDep):
    pass


@router.post("/me/update", response_model=UserResponse)
async def update_me(db: sessionDep):
    pass


@router.get("", response_model=UserListResponse)
@cache(ttl="60s", key="list_users:{offset}:{limit}", tags=["list_users"])
async def list_users(db: sessionDep, offset: int = 0, limit: int = 100):
    result = await services.get_users(db, offset, limit)
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_details(db: sessionDep, user_id: int):
    result = await services.get_user_details(user_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.patch("/{user_id}", response_model=UserResponse)
async def modify_user(db: sessionDep, user_id: int, user: UserUpdate):
    try:
        result = await services.update_user(db, user_id, user)
        await cache.delete_tags("list_users")
        return result
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DuplicateFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def remove_user(db: sessionDep, user_id: int):
    try:
        await services.delete_user(db, user_id)
        await cache.delete_tags("list_users")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
