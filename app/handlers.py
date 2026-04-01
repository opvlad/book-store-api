from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import AuthorNotFoundError, AuthorIsNotAdultError, BookNotFoundError


async def author_not_found_handler(request: Request, exc: AuthorNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Author not found"})


async def author_is_not_adult(request: Request, exc: AuthorIsNotAdultError):
    return JSONResponse(status_code=400, content={"detail": "Author is not adult"})


async def book_not_found_handler(request: Request, exc: BookNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Book not found"})
