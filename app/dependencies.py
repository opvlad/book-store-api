from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

security = HTTPBearer()


sessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(db: sessionDep, token: str = Depends(security)):
    pass