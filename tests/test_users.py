from httpx import AsyncClient
from pytest import mark

from app.models import UserRole
from app.security import create_access_token


async def test_user_read_me(client: AsyncClient, test_user):
    token = create_access_token(data={"id": test_user.id})
    response = await client.get(
        "api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == UserRole.USER
    assert "password" not in data
    assert "password_hash" not in data


async def test_user_read_me_invalid_token(client: AsyncClient):
    response = await client.get(
        "api/v1/users/me", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


async def test_user_read_me_invalid_token_payload(client: AsyncClient):
    invalid_token = create_access_token(data={})
    response = await client.get(
        "api/v1/users/me", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token payload"}


async def test_user_read_me_not_found(client: AsyncClient):
    token = create_access_token(data={"id": 999})
    response = await client.get(
        "api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "User not found"}


async def test_user_details_success(test_user, client: AsyncClient, admin_token):
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == UserRole.USER
    assert "password" not in data
    assert "password_hash" not in data


async def test_user_details_not_found(client: AsyncClient, admin_token):
    response = await client.get(
        "/api/v1/users/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    print(response.status_code)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_user_details_forbidden(test_user, client: AsyncClient):
    token = create_access_token(data={"id": test_user.id})
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Admin permission required"}


async def test_list_users_contains_only_admin(client: AsyncClient, admin_token):
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


async def test_list_users_success(test_user, client: AsyncClient, admin_token):
    response = await client.get(
        "api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 2
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["items"]) == 2


async def test_list_users_pagination(client: AsyncClient, admin_token):
    response = await client.get(
        "api/v1/users?offset=2&limit=50",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["offset"] == 2
    assert data["limit"] == 50


@mark.parametrize("update_type", ["admin_action", "user_action"])
async def test_update_user_success(
    client: AsyncClient, update_type, get_update_context
):
    update_user = {"username": "new_username"}
    context = get_update_context(update_type)

    response = await client.patch(
        url=context["url"], headers=context["headers"], json=update_user
    )
    assert response.status_code == 200
    assert response.json()["username"] == update_user["username"]

    update_user = {"email": "new_email@test.com"}
    response = await client.patch(
        url=context["url"], headers=context["headers"], json=update_user
    )
    assert response.status_code == 200
    assert response.json()["email"] == update_user["email"]


async def test_update_user_not_found(client: AsyncClient, admin_token):
    response = await client.patch(
        "/api/v1/users/999",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


@mark.parametrize("update_type", ["admin_action", "user_action"])
async def test_update_user_duplicated_username(
    test_user, test_other_user, get_update_context, update_type, client: AsyncClient
):
    context = get_update_context(update_type)
    response = await client.patch(
        url=context["url"],
        headers=context["headers"],
        json={"username": test_other_user.username},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


@mark.parametrize("update_type", ["admin_action", "user_action"])
async def test_update_user_duplicated_email(
    test_user, test_other_user, get_update_context, update_type, client: AsyncClient
):
    context = get_update_context(update_type)
    response = await client.patch(
        url=context["url"],
        headers=context["headers"],
        json={"email": test_other_user.email},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


async def test_delete_user_success(test_user, client: AsyncClient, admin_token):
    response = await client.delete(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    response = await client.delete(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_delete_user_not_found(client: AsyncClient, admin_token):
    response = await client.delete(
        "/api/v1/users/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
