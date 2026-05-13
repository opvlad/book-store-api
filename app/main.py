import logging
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis

from app.routers.v1.users import router as users_router
from app.routers.v1.auth import router as auth_router
from app.routers.v1.authors import router as authors_router
from app.routers.v1.books import router as books_router
from app.routers.v1.orders import router as orders_router
from app.config.settings import settings

from app.exceptions import (
    UnauthorizedError,
    DuplicateFieldError,
    PermissionDeniedError,
    InsufficientStockQuantityError,
    EntityNotFoundError,
    AuthorIsNotAdultError,
    InvalidTokenError,
)
from app.handlers.exceptions import (
    unauthorized_handler,
    duplicate_field_handler,
    permission_denied_handler,
    insufficient_stock_quantity_handler,
    entity_not_found_handler,
    author_is_not_adult,
    invalid_token_handler,
)
import app.handlers.cache
import app.config.logging


logger = logging.getLogger(__name__)


def bookstore_key_builder(
    func,
    namespace: str = "",
    *,
    request: Request = None,
    response: Response = None,
    args: tuple = None,
    kwargs: dict = None,
) -> str:
    copy_kwargs = kwargs.copy()

    copy_kwargs.pop("db", None)
    copy_kwargs.pop("request", None)
    copy_kwargs.pop("response", None)

    return f"{namespace}:{copy_kwargs}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(settings.redis_url, decode_responses=False)
    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="bookstore",
        key_builder=bookstore_key_builder,
    )
    logger.info("application started")
    yield
    await redis_client.close()
    logger.info("application stopped")


app = FastAPI(lifespan=lifespan)


app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(authors_router, prefix="/api/v1/authors", tags=["authors"])
app.include_router(books_router, prefix="/api/v1/books", tags=["books"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])


app.add_exception_handler(UnauthorizedError, unauthorized_handler)
app.add_exception_handler(DuplicateFieldError, duplicate_field_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(
    InsufficientStockQuantityError, insufficient_stock_quantity_handler
)
app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
app.add_exception_handler(AuthorIsNotAdultError, author_is_not_adult)
app.add_exception_handler(InvalidTokenError, invalid_token_handler)


@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = perf_counter()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            f"UNHANDLED_ERROR | {request.method} {request.url.path} | ip={request.client.host} | error={e}",
            exc_info=True,
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    process_time = perf_counter() - start_time
    logger.info(
        f"{request.method} {request.url.path} | {response.status_code} | ip={request.client.host} pt="
        f"{process_time * 1000:.2f} ms"
    )
    return response


@app.get("/health")
async def check_health():
    return {"status": "ok"}
