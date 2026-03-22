from httpx import AsyncClient

from app.models import UserRole


async def test_user_details(test_user, client: AsyncClient) -> None:
    response = await client.get(f"api/v1/users/{test_user.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == UserRole.USER


async def test_user_details_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/999")
    print(response.status_code)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_list_users_is_empty(client: AsyncClient):
    response = await client.get("/api/v1/users")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


async def test_list_users(test_user, client: AsyncClient):
    response = await client.get("api/v1/users")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["items"]) == 1


async def test_list_users_pagination(client: AsyncClient):
    response = await client.get("api/v1/users?offset=2&limit=50")
    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 50
    assert data["offset"] == 2
