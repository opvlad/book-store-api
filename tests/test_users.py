from httpx import AsyncClient

from app.models import UserRole


async def test_user_details(test_user, client: AsyncClient):
    response = await client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == UserRole.USER


async def test_user_details_not_found(client: AsyncClient):
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
    assert data["offset"] == 2
    assert data["limit"] == 50


async def test_create_user(client: AsyncClient):
    user = {"username": "test", "email": "example@test.com", "password": "secret"}
    response = await client.post("/api/v1/users", json=user)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert data["role"] == UserRole.USER


async def test_create_user_duplicated_username(test_user, client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "test_username",
            "email": "example@test.com",
            "password": "secret",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


async def test_create_user_duplicated_email(test_user, client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={"username": "test", "email": "test@test.com", "password": "secret"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


async def test_update_user(test_user, client: AsyncClient):
    user = {"username": "new_username"}
    response = await client.patch(f"/api/v1/users/{test_user.id}", json=user)
    assert response.status_code == 200
    assert response.json()["username"] == user["username"]

    user = {"email": "new_email@test.com"}
    response = await client.patch(f"/api/v1/users/{test_user.id}", json=user)
    assert response.status_code == 200
    assert response.json()["email"] == user["email"]


async def test_update_user_not_found(test_user, client: AsyncClient):
    response = await client.patch("/api/v1/users/999", json={})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_update_user_duplicated_username(
    test_user, test_other_user, client: AsyncClient
):
    response = await client.patch(
        f"/api/v1/users/{test_user.id}", json={"username": test_other_user.username}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


async def test_update_user_duplicated_email(
    test_user, test_other_user, client: AsyncClient
):
    response = await client.patch(
        f"/api/v1/users/{test_user.id}", json={"email": test_other_user.email}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


async def test_delete_user(test_user, client: AsyncClient):
    response = await client.delete(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 204


async def test_delete_user_not_found(test_user, client: AsyncClient):
    response = await client.delete("/api/v1/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
