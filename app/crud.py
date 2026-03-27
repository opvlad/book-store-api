from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.models import User
from app.schemas import UserCreateInDB, UserUpdate
from sqlalchemy import select


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str | EmailStr) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, offset: int, limit: int) -> list[User]:
    result = await db.execute(
        select(User).offset(offset).limit(limit).order_by(User.id)
    )
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user: UserCreateInDB) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate) -> User:
    db_user = await get_user_by_id(db, user_id)

    updated_data = user.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_user, key, value)

    await db.flush()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    db_user = await get_user_by_id(db, user_id)
    await db.delete(db_user)
    await db.flush()
