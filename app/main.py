from fastapi import FastAPI

from app.routers.v1.users import router as users_router
from app.routers.v1.auth import router as auth_router
from app.routers.v1.authors import router as authors_router

from app.exceptions import AuthorNotFoundError, AuthorIsNotAdultError
from app.handlers import author_not_found_handler, author_is_not_adult


app = FastAPI()


app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(authors_router, prefix="/api/v1/authors", tags=["authors"])


app.add_exception_handler(AuthorNotFoundError, author_not_found_handler)
app.add_exception_handler(AuthorIsNotAdultError, author_is_not_adult)


@app.get("/health")
async def check_health():
    return {"status": "ok"}
