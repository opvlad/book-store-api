from fastapi import APIRouter, Depends

from app.dependencies import sessionDep, get_current_user, get_current_admin
from app.models import User
from app.schemas import OrderResponse, OrderCreate, OrderListPaginatedResponse
from app.services import (
    get_order as service_get_order,
    get_orders as service_get_orders,
    create_order as service_create_order,
)

router = APIRouter()


@router.get("/me/{order_id}", response_model=OrderResponse)
async def get_my_order_details(
    db: sessionDep, order_id: int, user: User = Depends(get_current_user)
):
    return await service_get_order(db, order_id, user)


@router.get("/me", response_model=OrderListPaginatedResponse)
async def get_my_orders(
    db: sessionDep,
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user),
):
    total, items = await service_get_orders(db, limit=limit, offset=offset, user=user)
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("", response_model=OrderListPaginatedResponse)
async def get_orders(
    db: sessionDep,
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_admin),
):
    total, items = await service_get_orders(
        db, limit=limit, offset=offset, user=user, admin_action=True
    )
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.post("/me", response_model=OrderResponse, status_code=201)
async def create_order(
    db: sessionDep, order: OrderCreate, user: User = Depends(get_current_user)
):
    return await service_create_order(db, order, user)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    db: sessionDep, order_id: int, admin: User = Depends(get_current_admin)
):
    return await service_get_order(db, order_id, admin)
