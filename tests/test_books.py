from pytest import mark
from httpx import AsyncClient

from app.models import Book


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


@mark.parametrize("price", [-10.50, 0])
async def test_create_book_error_invalid_price(
    client: AsyncClient, test_author, admin_token, price
):
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "Test title",
            "price": price,
            "author_id": test_author.id,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


async def test_create_book_error_negative_stock(
    client: AsyncClient, test_author, admin_token
):
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "Test title",
            "price": 100,
            "stock_quantity": -1,
            "author_id": test_author.id,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


async def test_create_book_error_empty_title(
    client: AsyncClient, test_author, admin_token
):
    response = await client.post(
        "/api/v1/books",
        json={
            "title": "",
            "price": 100,
            "stock_quantity": 1,
            "author_id": test_author.id,
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


async def test_delete_book_bot_found(client: AsyncClient, admin_token):
    response = await client.delete(
        "/api/v1/books/999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"
