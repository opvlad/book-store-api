from fastapi import FastAPI
from cashews import cache

from app.routers.v1.users import router as users_router


cache.setup("mem://")

app = FastAPI()




app.include_router(users_router, prefix="/api/v1/users", tags=["users"])


@app.get("/health")
async def check_health():
    return {"status": "ok"}
