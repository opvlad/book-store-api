from pytest import mark
from httpx import AsyncClient, Response

from app.models import Book
from app.schemas import BookResponse
import app.routers.v1.books as books_router
from tests.utils import assert_response_data


async def test_list_books_cache_success(client: AsyncClient, mocker):
    mock_get_list_books = mocker.spy(books_router, "service_get_books")

    response_1 = await client.get("/api/v1/books")
    assert response_1.status_code == 200
    assert mock_get_list_books.call_count == 1

    response_2 = await client.get("/api/v1/books")
    assert response_2.status_code == 200
    assert mock_get_list_books.call_count == 1


async def test_list_books_cache_invalidation(
    client: AsyncClient, test_author, mocker, admin_token
):
    mock_get_list_books = mocker.spy(books_router, "service_get_books")

    async def _get_response(call_count: int) -> Response:
        get_response = await client.get("/api/v1/books")
        assert get_response.status_code == 200
        assert mock_get_list_books.call_count == call_count
        return get_response

    response = await _get_response(call_count=1)
    mock_get_list_books.reset_mock()

    # --- POST invalidates cache ---

    post_response = await client.post(
        "/api/v1/books",
        json={"title": "test title", "author_id": test_author.id, "price": 10},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert post_response.status_code == 201
    response = await _get_response(call_count=1)
    await _get_response(call_count=1)

    assert response.json()["total"] == 1
    book = post_response.json()
    assert_response_data(response.json()["items"][0], book, BookResponse)
    mock_get_list_books.reset_mock()

    # --- PATCH invalidates cache ---

    patch_response = await client.patch(
        f"/api/v1/books/{book['id']}",
        json={"title": "new title"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert patch_response.status_code == 200
    response = await _get_response(call_count=1)
    await _get_response(call_count=1)

    book_updated = patch_response.json()
    assert_response_data(response.json()["items"][0], book_updated, BookResponse)
    mock_get_list_books.reset_mock()

    # --- DELETE invalidates cache ---

    delete_response = await client.delete(
        f"/api/v1/books/{book['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_response.status_code == 204
    response = await _get_response(call_count=1)
    await _get_response(call_count=1)
    assert response.json()["total"] == 0


async def test_get_book_details_success(client: AsyncClient, test_book: Book):
    response = await client.get(f"/api/v1/books/{test_book.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == test_book.title
    assert data["description"] == test_book.description
    assert data["price"] == float(test_book.price)
    assert data["stock_quantity"] == test_book.stock_quantity
    assert data["author_id"] == test_book.author_id


async def test_get_book_details_not_found(client: AsyncClient):
    response = await client.get("/api/v1/books/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


async def test_get_list_books_empty(client: AsyncClient):
    response = await client.get("/api/v1/books")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


async def test_get_list_books_success(client: AsyncClient, test_book):
    response = await client.get("/api/v1/books")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert len(data["items"]) == 1


async def test_get_list_books_paginated(client: AsyncClient):
    response = await client.get("/api/v1/books?limit=50&offset=2")
    assert response.status_code == 200

    data = response.json()
    assert data["limit"] == 50
    assert data["offset"] == 2


async def test_create_book_success(client: AsyncClient, test_author, admin_token):
    book = {
        "title": "test title",
        "description": "test description",
        "price": 120.50,
        "stock_quantity": 1,
        "author_id": test_author.id,
    }
    response = await client.post(
        "/api/v1/books", json=book, headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == book["title"]
    assert data["description"] == book["description"]
    assert data["price"] == book["price"]
    assert data["stock_quantity"] == book["stock_quantity"]
    assert data["author_id"] == book["author_id"]


async def test_create_book_unauthorized(client: AsyncClient, test_author):
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "test title",
            "description": "test description",
            "price": 120.50,
            "stock_quantity": 1,
            "author_id": test_author.id,
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_create_book_forbidden(client: AsyncClient, test_author, user_token):
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "test title",
            "description": "test description",
            "price": 120.50,
            "stock_quantity": 1,
            "author_id": test_author.id,
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_create_book_not_existed_author(client: AsyncClient, admin_token):
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "test title",
            "description": "test description",
            "price": 120.50,
            "stock_quantity": 1,
            "author_id": 999,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"


@mark.parametrize(
    ["field_name", "value"],
    [("price", -10.50), ("price", 0), ("stock_quantity", -10), ("title", "")],
)
async def test_create_book_invalid_data(
    client: AsyncClient, test_author, admin_token, field_name, value
):
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "Test title",
            "price": 10,
            "author_id": test_author.id,
            field_name: value,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


async def test_update_book_success(client: AsyncClient, test_book, admin_token):
    book_update = {"title": "test title", "description": "test description"}
    response = await client.patch(
        f"/api/v1/books/{test_book.id}",
        json=book_update,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == book_update["title"]
    assert data["description"] == book_update["description"]
    assert data["price"] == test_book.price
    assert data["stock_quantity"] == test_book.stock_quantity
    assert data["author_id"] == test_book.author_id


async def test_update_book_unauthorized(client: AsyncClient, test_book):
    response = await client.patch(
        f"/api/v1/books/{test_book.id}",
        json={
            "title": "test title",
            "description": "test description",
            "price": 120.50,
            "stock_quantity": 1,
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_update_book_forbidden(client: AsyncClient, test_book, user_token):
    response = await client.patch(
        f"/api/v1/books/{test_book.id}",
        json={"title": "new title"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_update_book_not_found(client: AsyncClient, test_book, admin_token):
    response = await client.patch(
        "/api/v1/books/999",
        json={
            "title": "new title",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


async def test_update_book_not_existed_author(
    client: AsyncClient, test_book, admin_token
):
    response = await client.patch(
        f"/api/v1/books/{test_book.id}",
        json={
            "author_id": 999,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Author not found"


@mark.parametrize(
    ["field_name", "value"],
    [("price", -10.50), ("price", 0), ("stock_quantity", -10), ("title", "")],
)
async def test_update_book_invalid_data(
    client: AsyncClient, test_book, admin_token, field_name, value
):
    response = await client.patch(
        f"/api/v1/books/{test_book.id}",
        json={field_name: value},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


async def test_delete_book_success(client: AsyncClient, test_book, admin_token):
    response = await client.delete(
        f"/api/v1/books/{test_book.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    response = await client.get(f"/api/v1/books/{test_book.id}")
    assert response.status_code == 404


async def test_delete_book_unauthorized(client: AsyncClient, test_book):
    response = await client.delete(
        f"/api/v1/books/{test_book.id}",
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_delete_book_forbidden(client: AsyncClient, test_book, user_token):
    response = await client.delete(
        f"/api/v1/books/{test_book.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permission required"


async def test_delete_book_not_found(client: AsyncClient, admin_token):
    response = await client.delete(
        "/api/v1/books/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"
