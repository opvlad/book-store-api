from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from app.dependencies import sessionDep, get_current_admin
from app.event_bus import bus
from app.models import User
from app.schemas import BookResponse, BookListPaginatedResponse, BookCreate, BookUpdate
from app.services import (
    get_book as service_get_book,
    get_books as service_get_books,
    create_book as service_create_book,
    update_book as service_update_book,
    delete_book as service_delete_book,
)


router = APIRouter()


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_details(db: sessionDep, book_id: int):
    return await service_get_book(db, book_id)


@router.get("", response_model=BookListPaginatedResponse)
@cache(expire=600, namespace="books-list")
async def get_list_books(db: sessionDep, limit: int = 100, offset: int = 0):
    total, items = await service_get_books(db, limit, offset)
    return {"total": total, "limit": limit, "offset": offset, "items": items}


@router.post("", response_model=BookResponse, status_code=201)
async def add_book(
    db: sessionDep, book: BookCreate, admin: User = Depends(get_current_admin)
):
    book_created = await service_create_book(db, book, requester=admin)
    await bus.emit("book.created")
    return book_created


@router.patch("/{book_id}", response_model=BookResponse)
async def modify_book(
    db: sessionDep,
    book_id: int,
    book_update: BookUpdate,
    admin: User = Depends(get_current_admin),
):
    book_updated = await service_update_book(db, book_id, book_update, requester=admin)
    await bus.emit("book.updated")
    return book_updated


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    db: sessionDep, book_id: int, admin: User = Depends(get_current_admin)
):
    await service_delete_book(db, book_id, requester=admin)
    await bus.emit("book.deleted")
