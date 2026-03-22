from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, offset: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(
        select(User).offset(offset).limit(limit).order_by(User.id)
    )
    return list(result.scalars().all())


# async def create_user(db: AsyncSession, user: UserCreate) -> User:
