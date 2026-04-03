from fastapi import APIRouter, Depends

from app.dependencies import sessionDep, get_current_user, get_current_admin
from app.models import User
from app.schemas import OrderResponse, OrderCreate
from app.services import (
    get_order as service_get_order,
    create_order as service_create_order,
)

router = APIRouter()


@router.get("/me/{order_id}", response_model=OrderResponse)
async def get_my_order_details(
    db: sessionDep, order_id: int, user: User = Depends(get_current_user)
):
    return await service_get_order(db, order_id, user)


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



