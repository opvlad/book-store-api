from fastapi import FastAPI

from app.routers.v1.users import router as users_router
from app.routers.v1.auth import router as auth_router


app = FastAPI()


app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])


@app.get("/health")
async def check_health():
    return {"status": "ok"}
