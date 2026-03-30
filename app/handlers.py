from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import AuthorNotFoundError, AuthorIsNotAdultError


async def author_not_found_handler(request: Request, exc: AuthorNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Author not found"})


async def author_is_not_adult(request: Request, exc: AuthorIsNotAdultError):
    return JSONResponse(status_code=422, content={"detail": "Author is not adult"})
