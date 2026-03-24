from fastapi import APIRouter, HTTPException, Depends
from cashews import cache

from app.dependencies import sessionDep, get_current_user, get_current_admin
from app.schemas import UserResponse, UserListResponse, UserUpdate
from app.models import User
from app.exeptions import UserNotFoundError, DuplicateFieldError
from app.services import (
    get_user as service_get_user,
    get_users as service_get_users,
    update_user as service_update_user,
    delete_user as service_delete_user,
)


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_profile(user: User = Depends(get_current_user)):
    return user


@router.patch("/me/update", response_model=UserResponse)
async def update_profile(
    db: sessionDep, user_update: UserUpdate, user: User = Depends(get_current_user)
):
    try:
        result = await service_update_user(db, user.id, user_update)
        await cache.delete_tags("list_users")
        return result
    except DuplicateFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=UserListResponse)
@cache(ttl="60s", key="list_users:{offset}:{limit}", tags=["list_users"])
async def list_users(
    db: sessionDep,
    offset: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_admin),
):
    result = await service_get_users(db, offset, limit)
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def read_user_details(
    db: sessionDep, user_id: int, _: User = Depends(get_current_admin)
):
    result = await service_get_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


@router.patch("/{user_id}", response_model=UserResponse)
async def modify_user(
    db: sessionDep,
    user_id: int,
    user_update: UserUpdate,
    _: User = Depends(get_current_admin),
):
    try:
        result = await service_update_user(db, user_id, user_update)
        await cache.delete_tags("list_users")
        return result
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except DuplicateFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def remove_user(
    db: sessionDep, user_id: int, _: User = Depends(get_current_admin)
):
    try:
        await service_delete_user(db, user_id)
        await cache.delete_tags("list_users")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
