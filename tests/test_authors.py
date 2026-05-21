from datetime import datetime
from httpx import Response

from app.schemas import AuthorResponse
import app.routers.v1.authors as authors_router
from tests.utils import assert_response_data


async def test_list_authors_cache_success(client, mocker):
    mock_get_list_authors = mocker.spy(authors_router, "service_get_authors")

    response_1 = await client.get("/api/v1/authors")
    assert response_1.status_code == 200
    assert mock_get_list_authors.call_count == 1

    response_2 = await client.get("/api/v1/authors")
    assert response_2.status_code == 200
    assert mock_get_list_authors.call_count == 1


async def test_list_authors_cache_invalidation(client, mocker, admin_token):
    mock_get_list_authors = mocker.spy(authors_router, "service_get_authors")

    async def _get_response(call_count: int) -> Response:
        get_response = await client.get("/api/v1/authors")
        assert get_response.status_code == 200
        assert mock_get_list_authors.call_count == call_count
        return get_response

    await _get_response(call_count=1)
    mock_get_list_authors.reset_mock()

    # --- POST invalidates cache ---

    post_response = await client.post(
        "/api/v1/authors",
        json={"name": "test", "birth_date": "1999-01-01"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert post_response.status_code == 201
    response = await _get_response(call_count=1)
    await _get_response(call_count=1)

    assert response.json()["total"] == 1
    author = post_response.json()
    assert_response_data(response.json()["items"][0], author, AuthorResponse)
    mock_get_list_authors.reset_mock()

    # --- PATCH invalidates cache ---

    patch_response = await client.patch(
        f"/api/v1/authors/{author['id']}",
        json={"name": "new name"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_response.status_code == 200
    response = await _get_response(call_count=1)
    await _get_response(call_count=1)

    author_updated = patch_response.json()
    assert_response_data(response.json()["items"][0], author_updated, AuthorResponse)
    mock_get_list_authors.reset_mock()

    # --- DELETE invalidates cache ---

    delete_response = await client.delete(
        f"/api/v1/authors/{author['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_response.status_code == 204
    response = await _get_response(call_count=1)
    await _get_response(call_count=1)
    assert response.json()["total"] == 0


async def test_author_details_success(client, test_author):
    response = await client.get(f"/api/v1/authors/{test_author.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == test_author.name
    assert data["bio"] == test_author.bio
    assert data["birth_date"] == test_author.birth_date.isoformat()


async def test_author_details_not_found(client):
    response = await client.get("/api/v1/authors/999")
    assert response.status_code == 400
    assert "999" in response.json()["detail"]


async def test_authors_list_empty(client):
    response = await client.get("/api/v1/authors")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


async def test_authors_list_success(client, test_author):
    response = await client.get("/api/v1/authors")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["items"]) == 1


async def test_authors_list_paginated(client):
    response = await client.get("/api/v1/authors?limit=50&offset=2")
    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 50
    assert data["offset"] == 2


async def test_create_author_success(client, admin_token):
    author = {"name": "John Doe", "bio": "test info", "birth_date": "1999-01-01"}
    response = await client.post(
        "/api/v1/authors",
        json=author,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == author["name"]
    assert data["bio"] == author["bio"]
    assert data["birth_date"] == author["birth_date"]


async def test_create_author_unauthorized(client):
    response = await client.post(
        "/api/v1/authors",
        json={"name": "John Doe", "bio": "test info", "birth_date": "1999-01-01"},
    )
    assert response.status_code == 401


async def test_create_author_as_user_forbidden(client, user_token):
    response = await client.post(
        "/api/v1/authors",
        json={"name": "John Doe", "bio": "test info", "birth_date": "1999-01-01"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


async def test_create_author_is_not_adult(client, admin_token):
    response = await client.post(
        "/api/v1/authors",
        json={
            "name": "John Doe",
            "bio": "test info",
            "birth_date": datetime.now().date().isoformat(),
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Author is not adult"


async def test_update_author_success(client, test_author, admin_token):
    author_update = {
        "name": "updated name",
        "bio": "updated bio",
        "birth_date": "2000-09-09",
    }
    response = await client.patch(
        f"/api/v1/authors/{test_author.id}",
        json=author_update,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == author_update["name"]
    assert data["bio"] == author_update["bio"]
    assert data["birth_date"] == author_update["birth_date"]


async def test_update_author_not_found(client, admin_token):
    response = await client.patch(
        "/api/v1/authors/999",
        json={
            "name": "updated name",
            "bio": "updated bio",
            "birth_date": "2000-09-09",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert "999" in response.json()["detail"]


async def test_update_author_is_not_adult(client, test_author, admin_token):
    response = await client.patch(
        f"/api/v1/authors/{test_author.id}",
        json={"birth_date": datetime.now().date().isoformat()},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Author is not adult"


async def test_update_author_unauthorized(client, test_author):
    response = await client.patch(
        f"/api/v1/authors/{test_author.id}",
        json={
            "name": "updated name",
            "bio": "updated bio",
            "birth_date": "2000-09-09",
        },
    )
    assert response.status_code == 401


async def test_update_author_as_user_forbidden(client, test_author, user_token):
    response = await client.patch(
        f"/api/v1/authors/{test_author.id}",
        json={
            "name": "updated name",
            "bio": "updated bio",
            "birth_date": "2000-09-09",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403


async def test_delete_author_success(client, test_author, admin_token):
    response = await client.delete(
        f"/api/v1/authors/{test_author.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    response = await client.get(
        f"/api/v1/authors/{test_author.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert str(test_author.id) in response.json()["detail"]


async def test_delete_author_not_found(client, test_author, admin_token):
    response = await client.delete(
        "/api/v1/authors/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400
    assert "999" in response.json()["detail"]


async def test_delete_author_unauthorized(client, test_author):
    response = await client.delete(
        f"/api/v1/authors/{test_author.id}",
    )
    assert response.status_code == 401


async def test_delete_author_as_user_forbidden(client, test_author, user_token):
    response = await client.delete(
        f"/api/v1/authors/{test_author.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
