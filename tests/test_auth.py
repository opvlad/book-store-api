from httpx import AsyncClient

from app.models import UserRole


async def test_login_success(client: AsyncClient, test_user):
    response = await client.post(
        "/api/v1/auth/login", json={"username": "test_username", "password": "secret"}
    )
    assert response.status_code == 200


async def test_login_not_existed_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login", json={"username": "not_exist", "password": "secret"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


async def test_login_wrong_password(client: AsyncClient, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "test_username", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


async def test_register_success(client: AsyncClient):
    user = {"username": "test", "email": "example@test.com", "password": "secret"}
    response = await client.post("/api/v1/auth/register", json=user)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert data["role"] == UserRole.USER


async def test_register_duplicated_username(test_user, client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_username",
            "email": "example@test.com",
            "password": "secret",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


async def test_register_duplicated_email(test_user, client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"username": "test", "email": "test@test.com", "password": "secret"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"
