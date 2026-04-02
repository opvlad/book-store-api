from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.models import User, Author, Book, Order
from app.schemas import (
    UserCreateInDB,
    UserUpdate,
    AuthorCreate,
    AuthorUpdate,
    BookCreate,
    BookUpdate,
    OrderCreateInDB,
    OrderUpdate,
)

from sqlalchemy import select, func


# USERS


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str | EmailStr) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession, offset: int, limit: int
) -> tuple[int, list[User]]:
    result = await db.execute(
        select(User).offset(offset).limit(limit).order_by(User.id)
    )
    total = await db.scalar(select(func.count(User.id)))
    return total, list(result.scalars().all())


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


# BOOKS


async def get_book_by_id(db: AsyncSession, book_id: int) -> Book | None:
    return await db.get(Book, book_id)


async def get_books(
    db: AsyncSession, limit: int, offset: int
) -> tuple[int, list[Book]]:
    items = await db.execute(select(Book).order_by(Book.id).limit(limit).offset(offset))
    total = await db.scalar(select(func.count(Book.id)))
    return total, list(items.scalars().all())


async def create_book(db: AsyncSession, book: BookCreate) -> Book:
    db_book = Book(**book.model_dump())
    db.add(db_book)
    await db.flush()
    await db.refresh(db_book)
    return db_book


async def update_book(db: AsyncSession, book_id: int, book_update: BookUpdate) -> Book:
    db_book = await get_book_by_id(db, book_id)

    updated_data = book_update.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_book, key, value)

    await db.flush()
    await db.refresh(db_book)
    return db_book


async def delete_book(db: AsyncSession, book_id: int) -> None:
    db_book = await get_book_by_id(db, book_id)
    await db.delete(db_book)
    await db.flush()


# ORDERS


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    return await db.get(Order, order_id)


async def get_orders(
    db: AsyncSession, limit: int, offset: int
) -> tuple[int, list[Order]]:
    items = await db.execute(
        select(Order).order_by(Order.id).limit(limit).offset(offset)
    )
    total = await db.scalar(select(func.count(Order.id)))
    return total, list(items.scalars().all())


async def create_order(db: AsyncSession, order: OrderCreateInDB) -> Order:
    db_order = Order(**order.model_dump())
    db.add(db_order)
    await db.flush()
    await db.refresh(db_order)
    return db_order


async def update_order(
    db: AsyncSession, order_id: int, order_update: OrderUpdate
) -> Order:
    db_order = await get_order_by_id(db, order_id)

    updated_data = order_update.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_order, key, value)

    await db.flush()
    await db.refresh(db_order)
    return db_order


async def delete_order(db: AsyncSession, order_id: int) -> None:
    db_order = await get_order_by_id(db, order_id)
    await db.delete(db_order)
