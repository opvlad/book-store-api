from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    PermissionDeniedError,
    EntityNotFoundError,
    AuthorNotFoundError,
    AuthorIsNotAdultError,
    BookNotFoundError,
    OrderNotFoundError,
)


async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(status_code=403, content={"detail": "Permission denied"})


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def author_not_found_handler(request: Request, exc: AuthorNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Author not found"})


async def author_is_not_adult(request: Request, exc: AuthorIsNotAdultError):
    return JSONResponse(status_code=400, content={"detail": "Author is not adult"})


async def book_not_found_handler(request: Request, exc: BookNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Book not found"})


async def order_not_found_handler(request: Request, exc: OrderNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Order not found"})
