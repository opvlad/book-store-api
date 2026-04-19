from decimal import Decimal
from httpx import AsyncClient, Response
from pytest import mark

from app.models import Order, OrderStatus, DeliveryType
from app.security import create_access_token
from app.services import calculate_priority
from app.schemas import OrderResponse, OrderAdminResponse


def assert_order_response_data(response: Response, order: Order, response_schema):
    response_data = response_schema.model_validate(response.json())
    db_data = response_schema.model_validate(order)

    assert response_data == db_data


async def test_get_my_order_details_success(client: AsyncClient, test_order):
    owner_token = create_access_token(data={"id": test_order.user_id})
    response = await client.get(
        f"/api/v1/orders/me/{test_order.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200
    assert_order_response_data(response, test_order, OrderResponse)


async def test_get_my_order_details_unauthorized(client: AsyncClient, test_order):
    response = await client.get(
        f"/api/v1/orders/me/{test_order.id}",
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_my_order_details_not_own(
    client: AsyncClient, test_order, test_other_user
):
    not_owner_token = create_access_token(data={"id": test_other_user.id})
    response = await client.get(
        f"/api/v1/orders/me/{test_order.id}",
        headers={"Authorization": f"Bearer {not_owner_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


async def test_get_my_order_details_not_found(client: AsyncClient, user_token):
    response = await client.get(
        "/api/v1/orders/me/999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


async def test_get_order_details_success(client: AsyncClient, test_order, admin_token):
    response = await client.get(
        f"/api/v1/orders/{test_order.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert_order_response_data(response, test_order, OrderAdminResponse)


async def test_get_order_details_unauthorized(client: AsyncClient, test_order):
    response = await client.get(
        f"/api/v1/orders/{test_order.id}",
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_order_details_not_found(client: AsyncClient, admin_token):
    response = await client.get(
        "/api/v1/orders/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


async def test_get_my_orders_empty(client: AsyncClient, user_token):
    response = await client.get(
        "/api/v1/orders/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_get_my_orders_success(client: AsyncClient, test_order):
    owner_token = create_access_token(data={"id": test_order.user_id})
    response = await client.get(
        "/api/v1/orders/me",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["items"]) == 1


async def test_get_my_orders_paginated(client: AsyncClient, user_token):
    response = await client.get(
        "/api/v1/orders/me?limit=50&offset=2",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 50
    assert data["offset"] == 2


async def test_get_my_orders_unauthorized(client: AsyncClient):
    response = await client.get(
        "/api/v1/orders/me",
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_orders_empty(client: AsyncClient, admin_token):
    response = await client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_get_orders_success(client: AsyncClient, test_order, admin_token):
    response = await client.get(
        "/api/v1/orders",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["items"]) == 1


async def test_get_orders_paginated(client: AsyncClient, admin_token):
    response = await client.get(
        "/api/v1/orders?limit=50&offset=2",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 50
    assert data["offset"] == 2


async def test_get_orders_filtered_empty(client: AsyncClient, admin_token):
    response = await client.get(
        "/api/v1/orders?priority__gt=10",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


@mark.parametrize("filter_key", ["user_id", "delivery_type", "status"])
async def test_get_orders_filtered(
    client: AsyncClient, test_order, admin_token, filter_key
):
    response = await client.get(
        f"/api/v1/orders?{filter_key}={getattr(test_order, filter_key)}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_get_orders_unauthorized(client: AsyncClient):
    response = await client.get(
        "/api/v1/orders",
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@mark.parametrize("quantity", [1, 6, 21])
async def test_create_order_success(
    client: AsyncClient, test_book, test_other_book, test_user, quantity
):
    user_token = create_access_token(data={"id": test_user.id})
    items = [
        {"book_id": test_book.id, "quantity": quantity},
        {"book_id": test_other_book.id, "quantity": quantity},
    ]
    order = {"items": items, "note": "very important"}

    response = await client.post(
        "/api/v1/orders",
        json=order,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["items"] == items
    assert data["status"] == OrderStatus.PENDING
    assert data["delivery_type"] == DeliveryType.STANDARD
    assert Decimal(data["total_amount"]) == Decimal(
        test_book.price * items[0]["quantity"]
        + test_other_book.price * items[1]["quantity"]
    )
    assert data["note"] == order["note"]


async def test_create_order_unauthorized(client: AsyncClient, test_book):
    response = await client.post(
        "/api/v1/orders",
        json={"book_id": test_book.id, "quantity": 1, "note": "very important"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_create_order_not_existed_book(client: AsyncClient, user_token):
    order = {
        "items": [
            {"book_id": 999, "quantity": 5},
        ],
        "note": "very important",
    }
    response = await client.post(
        "/api/v1/orders",
        json=order,
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == f"Books with ids [{order['items'][0]['book_id']}] not found"
    )


async def test_order_create_zero_stock_quantity(
    client: AsyncClient, user_token, test_book_zero_stock_qty
):
    response = await client.post(
        "/api/v1/orders",
        json={
            "items": [
                {"book_id": test_book_zero_stock_qty.id, "quantity": 5},
            ]
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == f"Books with ids [{test_book_zero_stock_qty.id}] have insufficient stock quantity"
    )


@mark.parametrize(
    ["field_name", "value"],
    [("quantity", 0), ("quantity", -10), ("delivery_type", "test")],
)
async def test_create_order_invalid_data(
    client: AsyncClient, test_book, user_token, field_name, value
):
    response = await client.post(
        "/api/v1/orders",
        json={"book_id": test_book.id, field_name: value},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 422


async def test_update_order_success(client: AsyncClient, test_order, admin_token):
    order_update = {
        "status": OrderStatus.PAID,
    }

    response = await client.patch(
        f"/api/v1/orders/{test_order.id}",
        json=order_update,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == order_update["status"]


async def test_update_order_unauthorized(client: AsyncClient, test_order):
    response = await client.patch(
        f"/api/v1/orders/{test_order.id}",
        json={"note": "new note"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_update_order_forbidden(client: AsyncClient, test_order, user_token):
    response = await client.patch(
        f"/api/v1/orders/{test_order.id}",
        json={"note": "new note"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


@mark.parametrize("status", ["test", 123])
async def test_update_order_invalid_status(
    client: AsyncClient, test_order, admin_token, status
):
    response = await client.patch(
        f"/api/v1/orders/{test_order.id}",
        json={"status": status},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


async def test_update_order_not_found(client: AsyncClient, admin_token):
    response = await client.patch(
        "/api/v1/orders/999",
        json={"status": OrderStatus.SHIPPED},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


async def test_delete_order_success(client: AsyncClient, test_order, admin_token):
    response = await client.delete(
        f"/api/v1/orders/{test_order.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    response = await client.get(
        f"/api/v1/orders/{test_order.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


async def test_delete_order_unauthorized(client: AsyncClient, test_order):
    response = await client.delete(f"/api/v1/orders/{test_order.id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_delete_order_forbidden(client: AsyncClient, test_order, user_token):
    response = await client.delete(
        f"/api/v1/orders/{test_order.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_delete_order_not_found(client: AsyncClient, admin_token):
    response = await client.delete(
        "/api/v1/orders/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
