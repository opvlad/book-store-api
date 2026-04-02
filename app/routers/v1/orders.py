from fastapi import APIRouter, Depends

from app.dependencies import sessionDep, get_current_user
from app.models import User
from app.schemas import OrderResponse
from app.services import (
    get_order as service_get_order,
)

router = APIRouter()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    db: sessionDep, order_id: int, user: User = Depends(get_current_user)
):
    return await service_get_order(db, order_id, user)
