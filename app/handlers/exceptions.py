import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import (
    UnauthorizedError,
    DuplicateFieldError,
    PermissionDeniedError,
    InsufficientStockQuantityError,
    EntityNotFoundError,
    AuthorIsNotAdultError,
    InvalidTokenError,
)


logger = logging.getLogger(__name__)


async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def duplicate_field_handler(request: Request, exc: DuplicateFieldError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    logger.warning(f"PERMISSION_DENIED | user_id={exc.user_id}")
    return JSONResponse(status_code=403, content={"detail": str(exc)})


async def insufficient_stock_quantity_handler(
    request: Request, exc: InsufficientStockQuantityError
):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def author_is_not_adult(request: Request, exc: AuthorIsNotAdultError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def invalid_token_handler(request: Request, exc: InvalidTokenError):
    logger.warning(f"TOKEN_INVALID | {request.method} {request.url.path} | ip={request.client.host} | error="
                   f"{exc.detail}")
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def sql_alchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"DB_ERROR | error={type(exc).__name__}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
