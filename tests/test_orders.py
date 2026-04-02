from decimal import Decimal
from httpx import AsyncClient

from app.security import create_access_token
from app.schemas import OrderResponse


def assert_order_response(response, order):
    response_data = OrderResponse.model_validate(response.json())
    db_data = OrderResponse.model_validate(order)

    assert response_data == db_data


async def test_get_order_details_as_user_success(client: AsyncClient, test_order):
    owner_token = create_access_token(data={"id": test_order.user_id})
    response = await client.get(
        f"/api/v1/orders/{test_order.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 200
    assert_order_response(response, test_order)


async def test_get_order_details_as_admin_success(client: AsyncClient, test_order, admin_token):
    response = await client.get(
        f"/api/v1/orders/{test_order.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert_order_response(response, test_order)


async def test_get_order_details_unauthorized(client: AsyncClient, test_order):
    response = await client.get(
        f"/api/v1/orders/{test_order.id}",
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_get_order_details_forbidden(client: AsyncClient, test_order, test_other_user):
    user_token = create_access_token(data={"id": test_other_user.id})
    response = await client.get(
        f"/api/v1/orders/{test_order.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


async def test_get_order_details_not_found(client: AsyncClient, user_token):
    response = await client.get(
        "/api/v1/orders/999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


