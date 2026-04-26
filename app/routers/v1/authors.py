from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from app.dependencies import sessionDep, get_current_admin
from app.event_bus import bus
from app.models import User
from app.schemas import (
    AuthorResponse,
    AuthorListPaginatedResponse,
    AuthorCreate,
    AuthorUpdate,
)
from app.services import (
    get_author as service_get_author,
    get_authors as service_get_authors,
    create_author as service_create_author,
    update_author as service_update_author,
    delete_author as service_delete_author,
)


router = APIRouter()


@router.get("", response_model=AuthorListPaginatedResponse)
@cache(expire=600, namespace="authors-list")
async def authors_list(db: sessionDep, limit: int = 100, offset: int = 0):
    total, items = await service_get_authors(db, limit=limit, offset=offset)
    items_list = [AuthorResponse.model_validate(author) for author in items]
    return {"total": total, "limit": limit, "offset": offset, "items": items_list}


@router.get("/{author_id}", response_model=AuthorResponse)
async def read_author_details(db: sessionDep, author_id: int):
    return await service_get_author(db, author_id)


@router.post("", response_model=AuthorResponse, status_code=201)
async def create_author(
    db: sessionDep, author: AuthorCreate, admin: User = Depends(get_current_admin)
):
    author_created = await service_create_author(db, author, requester=admin)
    await bus.emit("author.created")
    return author_created


@router.patch("/{author_id}", response_model=AuthorResponse)
async def modify_author(
    db: sessionDep,
    author_id: int,
    author_update: AuthorUpdate,
    admin: User = Depends(get_current_admin),
):
    author_updated = await service_update_author(db, author_id, author_update, requester=admin)
    await bus.emit("author.updated")
    return author_updated


@router.delete("/{author_id}", status_code=204)
async def delete_author(
    db: sessionDep, author_id: int, admin: User = Depends(get_current_admin)
):
    await service_delete_author(db, author_id, requester=admin)
    await bus.emit("author.deleted")
