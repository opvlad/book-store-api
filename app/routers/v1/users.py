from fastapi import APIRouter, Depends

from app.dependencies import sessionDep, get_current_user, get_current_admin
from app.schemas import UserResponse, UserListPaginatedResponse, UserUpdate, UserUpdateAsAdmin
from app.models import User
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


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    db: sessionDep, user_update: UserUpdate, user: User = Depends(get_current_user)
):
    return await service_update_user(db, user.id, user_update, requester=user)


@router.get("", response_model=UserListPaginatedResponse)
async def list_users(
    db: sessionDep,
    offset: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_admin),
):
    total, items = await service_get_users(db, offset=offset, limit=limit)
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/{user_id}", response_model=UserResponse)
async def read_user_details(
    db: sessionDep, user_id: int, admin: User = Depends(get_current_admin)
):
    return await service_get_user(db, user_id, requester=admin)


@router.patch("/{user_id}", response_model=UserResponse)
async def modify_user(
    db: sessionDep,
    user_id: int,
    user_update: UserUpdateAsAdmin,
    admin: User = Depends(get_current_admin),
):
    return await service_update_user(db, user_id, user_update, requester=admin)


@router.delete("/{user_id}", status_code=204)
async def remove_user(
    db: sessionDep, user_id: int, admin: User = Depends(get_current_admin)
):
    await service_delete_user(db, user_id, requester=admin)
