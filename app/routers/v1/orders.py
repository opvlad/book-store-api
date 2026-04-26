from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi_filter import FilterDepends

from app.dependencies import sessionDep, get_current_user, get_current_admin
from app.utils import remove_temp_file
from app.models import User
from app.schemas import (
    OrderFilter,
    OrderResponse,
    OrderAdminResponse,
    OrderCreate,
    OrderListPaginatedResponse,
    OrderAdminListPaginatedResponse,
    OrderUpdate,
)
from app.services import (
    get_order as service_get_order,
    get_orders as service_get_orders,
    create_order as service_create_order,
    update_order as service_update_order,
    delete_order as service_delete_order,
    export_orders as service_export_orders,
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


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    db: sessionDep, order: OrderCreate, user: User = Depends(get_current_user)
):
    return await service_create_order(db, order, user)


@router.get("", response_model=OrderAdminListPaginatedResponse)
async def get_orders(
    db: sessionDep,
    filters: OrderFilter = FilterDepends(OrderFilter),
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_admin),
):
    total, items = await service_get_orders(
        db, limit=limit, offset=offset, user=user, admin_action=True, filters=filters
    )
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.get("/{order_id}", response_model=OrderAdminResponse)
async def get_order_details(
    db: sessionDep, order_id: int, admin: User = Depends(get_current_admin)
):
    return await service_get_order(db, order_id, admin)


@router.patch("/{order_id}", response_model=OrderResponse)
async def modify_order(
    db: sessionDep,
    order_id: int,
    order_update: OrderUpdate,
    admin: User = Depends(get_current_admin),
):
    return await service_update_order(db, order_id, order_update, requester=admin)


@router.delete("/{order_id}", status_code=204)
async def delete_order(
    db: sessionDep, order_id: int, admin: User = Depends(get_current_admin)
):
    await service_delete_order(db, order_id, requester=admin)


@router.get("/export/xlsx")
async def export_orders(
    db: sessionDep,
    background_tasks: BackgroundTasks,
    limit: int = 100,
    offset: int = 0,
    _: User = Depends(get_current_admin),
):
    file_path, file_name = await service_export_orders(db, limit=limit, offset=offset)

    background_tasks.add_task(remove_temp_file, file_path)

    return FileResponse(
        file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
