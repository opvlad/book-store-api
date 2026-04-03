from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.models import User, Author, Book, Order, UserRole, OrderStatus
from app.schemas import (
    UserCreate,
    UserCreateInDB,
    UserUpdate,
    LoginForm,
    AuthorCreate,
    AuthorUpdate,
    BookCreate,
    BookUpdate,
    OrderCreate,
    OrderCreateInDB,
    OrderUpdate,
)
from app.security import get_password_hash, verify_password, create_access_token
from app.exceptions import (
    PermissionDeniedError,
    EntityNotFoundError,
    UserNotFoundError,
    DuplicateFieldError,
    UnauthorizedError,
    AuthorNotFoundError,
    AuthorIsNotAdultError,
    BookNotFoundError,
    OrderNotFoundError,
)


# USERS


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await crud.get_user_by_id(db, user_id)


async def get_users(
    db: AsyncSession, offset: int, limit: int
) -> tuple[int, list[User]]:
    return await crud.get_users(db, offset, limit)


async def register_user(db: AsyncSession, user: UserCreate) -> User:
    if await crud.get_user_by_username(db, user.username):
        raise DuplicateFieldError("Username already exists")

    if await crud.get_user_by_email(db, user.email):
        raise DuplicateFieldError("Email already exists")

    user_in_db = UserCreateInDB(
        **user.model_dump(exclude={"password"}),
        password_hash=get_password_hash(user.password),
    )

    return await crud.create_user(db, user_in_db)


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate) -> User:
    existing_user = await crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise UserNotFoundError()

    if user.username:
        duplicate = await crud.get_user_by_username(db, user.username)
        if duplicate and duplicate.id != user_id:
            raise DuplicateFieldError("Username already exists")

    if user.email:
        duplicate = await crud.get_user_by_email(db, user.email)
        if duplicate and duplicate.id != user_id:
            raise DuplicateFieldError("Email already exists")

    return await crud.update_user(db, user_id, user)


async def delete_user(db: AsyncSession, user_id: int) -> None:
    if not await crud.get_user_by_id(db, user_id):
        raise UserNotFoundError()

    await crud.delete_user(db, user_id)


async def login_user(db: AsyncSession, credentials: LoginForm) -> str:
    db_user = await crud.get_user_by_username(db, credentials.username)

    if not db_user:
        raise UserNotFoundError()

    if not verify_password(credentials.password, db_user.password_hash):
        raise UnauthorizedError()

    return create_access_token({"id": db_user.id})


# AUTHORS


def is_adult(birth_date: date, adulthood_age: int = 18) -> bool:
    current_date = datetime.now().date()
    age = (
        current_date.year
        - birth_date.year
        - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    )
    return age >= adulthood_age


async def get_author(db: AsyncSession, author_id: int) -> Author:
    result = await crud.get_author_by_id(db, author_id)
    if not result:
        raise AuthorNotFoundError()
    return result


async def get_authors(
    db: AsyncSession, offset: int, limit: int
) -> tuple[int, list[Author]]:
    return await crud.get_authors(db, offset, limit)


async def create_author(db: AsyncSession, author: AuthorCreate) -> Author:
    if not is_adult(author.birth_date):
        raise AuthorIsNotAdultError()

    return await crud.create_author(db, author)


async def update_author(
    db: AsyncSession, author_id: int, author: AuthorUpdate
) -> Author:
    existing_author = await crud.get_author_by_id(db, author_id)
    if not existing_author:
        raise AuthorNotFoundError()

    if author.birth_date and not is_adult(author.birth_date):
        raise AuthorIsNotAdultError()

    return await crud.update_author(db, author_id, author)


async def delete_author(db: AsyncSession, author_id: int) -> None:
    existing_author = await crud.get_author_by_id(db, author_id)
    if not existing_author:
        raise AuthorNotFoundError()

    await crud.delete_author(db, author_id)


# BOOKS


async def get_book(db: AsyncSession, book_id: int) -> Book:
    book = await crud.get_book_by_id(db, book_id)
    if not book:
        raise BookNotFoundError()
    return book


async def get_books(
    db: AsyncSession, limit: int, offset: int
) -> tuple[int, list[Book]]:
    return await crud.get_books(db, limit, offset)


async def create_book(db: AsyncSession, book: BookCreate) -> Book:
    existing_author = await crud.get_author_by_id(db, book.author_id)
    if not existing_author:
        raise AuthorNotFoundError()

    return await crud.create_book(db, book)


async def update_book(db: AsyncSession, book_id: int, book_update: BookUpdate) -> Book:
    existing_book = await crud.get_book_by_id(db, book_id)
    if not existing_book:
        raise BookNotFoundError()

    if book_update.author_id is not None:
        existing_author = await crud.get_author_by_id(db, book_update.author_id)
        if not existing_author:
            raise AuthorNotFoundError()

    return await crud.update_book(db, book_id, book_update)


async def delete_book(db: AsyncSession, book_id: int) -> None:
    existing_book = await crud.get_book_by_id(db, book_id)
    if not existing_book:
        raise BookNotFoundError()

    await crud.delete_book(db, book_id)


# ORDERS


async def get_order(db: AsyncSession, order_id: int, user: User) -> Order:
    order = await crud.get_order_by_id(db, order_id)

    if not order:
        raise OrderNotFoundError()

    if order.user_id != user.id and user.role != UserRole.ADMIN:
        raise PermissionDeniedError()

    return order


async def get_orders(
    db: AsyncSession, limit: int, offset: int, user: User
) -> tuple[int, list[Order]]:

    # add where to crud, user can get only own orders

    if user.role != UserRole.ADMIN:
        total, items = await crud.get_orders(db, limit=limit, offset=offset, )


async def create_order(db: AsyncSession, order: OrderCreate, user: User) -> Order:
    book = await crud.get_book_by_id(db, order.book_id)
    if not book:
        raise EntityNotFoundError(
            status_code=400, entity_name="Book", entity_id=order.book_id
        )

    total_amount = Decimal(book.price * order.quantity)

    order_create_in_db = OrderCreateInDB(
        **order.model_dump(),
        user_id=user.id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
    )
    return await crud.create_order(db, order_create_in_db)
