from httpx import AsyncClient
from pytest import mark

from app.models import UserRole
from app.security import create_access_token


async def test_user_read_me(client: AsyncClient, test_user):
    token = create_access_token(data={"id": test_user.id})
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
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
        "/api/v1/users/me", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


async def test_user_read_me_invalid_token_payload(client: AsyncClient):
    invalid_token = create_access_token(data={})
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
    assert False


async def test_user_read_me_not_found(client: AsyncClient):
    token = create_access_token(data={"id": 999})
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


async def test_user_details_success(test_user, admin_token, client: AsyncClient):
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
    assert response.status_code == 400
    assert "999" in response.json()["detail"]


async def test_user_details_forbidden(client: AsyncClient, test_user):
    token = create_access_token(data={"id": test_user.id})
    response = await client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"


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
        "/api/v1/users",
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
        "/api/v1/users?offset=2&limit=50",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["offset"] == 2
    assert data["limit"] == 50


async def test_update_profile_success(client: AsyncClient, user_token):
    update_user = {"username": "new_username", "email": "new_email@test.com"}

    response = await client.patch(
        url="/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json=update_user,
    )
    assert response.status_code == 200
    assert response.json()["username"] == update_user["username"]
    assert response.json()["email"] == update_user["email"]


async def test_update_profile_unauthorized(client: AsyncClient):
    update_user = {"username": "new_username", "email": "new_email@test.com"}

    response = await client.patch(
        url="/api/v1/users/me",
        json=update_user,
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_update_profile_not_found(client: AsyncClient):
    token = create_access_token(data={"id": 999})
    response = await client.patch(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


async def test_update_profile_duplicated_username(
    client: AsyncClient, user_token, test_other_user
):
    response = await client.patch(
        url="/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"username": test_other_user.username},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


async def test_update_profile_duplicated_email(
    client: AsyncClient, user_token, test_other_user
):
    response = await client.patch(
        url="/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"email": test_other_user.email},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


@mark.parametrize("user_status", ["regular", "loyal", "vip"])
async def test_user_update_success(
    client: AsyncClient, test_user, admin_token, user_status
):

    response = await client.patch(
        url=f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": user_status},
    )
    assert response.status_code == 200
    assert response.json()["status"] == user_status


async def test_user_update_unauthorized(client: AsyncClient, test_user):
    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        json={"username": "new_username"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_user_update_not_found(client: AsyncClient, admin_token):
    response = await client.patch(
        "/api/v1/users/999",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "loyal"},
    )
    assert response.status_code == 400
    assert "999" in response.json()["detail"]


@mark.parametrize("user_status", ["123", "not", None])
async def test_update_user_invalid_data(client: AsyncClient, test_user, admin_token, user_status):
    response = await client.patch(
        f"/api/v1/users/{test_user.id}",
        json={"status": user_status},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


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
    assert response.status_code == 400
    assert str(test_user.id) in response.json()["detail"]


async def test_delete_user_not_found(client: AsyncClient, admin_token):
    response = await client.delete(
        "/api/v1/users/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert "999" in response.json()["detail"]
