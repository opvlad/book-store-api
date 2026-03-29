from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.models import User, Author
from app.schemas import UserCreateInDB, UserUpdate, AuthorCreate, AuthorUpdate
from sqlalchemy import select, func


# USERS


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


# AUTHORS


async def get_author_by_id(db: AsyncSession, author_id: int) -> Author | None:
    return await db.get(Author, author_id)


async def get_authors(
    db: AsyncSession, offset: int, limit: int
) -> tuple[int, list[Author]]:
    result = await db.execute(
        select(Author).order_by(Author.id).offset(offset).limit(limit)
    )
    total = await db.scalar(select(func.count(Author.id)))
    return total, list(result.scalars().all())


async def create_author(db: AsyncSession, author: AuthorCreate) -> Author:
    db_author = Author(**author.model_dump())
    db.add(db_author)
    await db.flush()
    await db.refresh(db_author)
    return db_author


async def update_author(
    db: AsyncSession, author_id: int, author_update: AuthorUpdate
) -> Author:
    db_author = await get_author_by_id(db, author_id)

    update_data = author_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_author, key, value)

    await db.flush()
    await db.refresh(db_author)
    return db_author


async def delete_author(db: AsyncSession, author_id: int) -> None:
    db_author = await get_author_by_id(db, author_id)
    await db.delete(db_author)
    await db.flush()
