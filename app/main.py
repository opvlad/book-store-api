from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis

from app.routers.v1.users import router as users_router
from app.routers.v1.auth import router as auth_router
from app.routers.v1.authors import router as authors_router
from app.routers.v1.books import router as books_router
from app.routers.v1.orders import router as orders_router

from app.exceptions import (
    PermissionDeniedError,
    InsufficientStockQuantityError,
    EntityNotFoundError,
    AuthorNotFoundError,
    AuthorIsNotAdultError,
    BookNotFoundError,
    OrderNotFoundError,
)
from app.handlers.exceptions import (
    permission_denied_handler,
    insufficient_stock_quantity_handler,
    entity_not_found_handler,
    author_not_found_handler,
    author_is_not_adult,
    book_not_found_handler,
    order_not_found_handler,
)
import app.handlers.cache


def bookstore_key_builder(
        func,
        namespace: str = "",
        *,
        request: Request = None,
        response: Response = None,
        args: tuple = None,
        kwargs: dict = None,
):
    copy_kwargs = kwargs.copy()

    copy_kwargs.pop("db", None)
    copy_kwargs.pop("request", None)
    copy_kwargs.pop("response", None)

    return f"{namespace}:{copy_kwargs}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url("redis://localhost", decode_responses=False)
    FastAPICache.init(RedisBackend(redis_client), prefix="bookstore", key_builder=bookstore_key_builder)
    yield
    await redis_client.close()


app = FastAPI(lifespan=lifespan)


app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(authors_router, prefix="/api/v1/authors", tags=["authors"])
app.include_router(books_router, prefix="/api/v1/books", tags=["books"])
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])


app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(
    InsufficientStockQuantityError, insufficient_stock_quantity_handler
)
app.add_exception_handler(EntityNotFoundError, entity_not_found_handler)
app.add_exception_handler(AuthorNotFoundError, author_not_found_handler)
app.add_exception_handler(AuthorIsNotAdultError, author_is_not_adult)
app.add_exception_handler(BookNotFoundError, book_not_found_handler)
app.add_exception_handler(OrderNotFoundError, order_not_found_handler)


@app.get("/health")
async def check_health():
    return {"status": "ok"}
