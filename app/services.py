from datetime import datetime, date
from decimal import Decimal
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.config import priority_points
from app.models import User, Author, Book, Order, UserRole, OrderStatus
from app.security import get_password_hash, verify_password, create_access_token
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
    UserUpdateAsAdmin,
    OrderFilter,
)
from app.exceptions import (
    PermissionDeniedError,
    InsufficientStockQuantityError,
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


async def update_user(
    db: AsyncSession, user_id: int, user: UserUpdate | UserUpdateAsAdmin
) -> User:
    existing_user = await crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise UserNotFoundError()

    updated_data = user.model_dump(exclude_unset=True)

    if "username" in updated_data:
        duplicate = await crud.get_user_by_username(db, user.username)
        if duplicate and duplicate.id != user_id:
            raise DuplicateFieldError("Username already exists")

    if "email" in updated_data:
        duplicate = await crud.get_user_by_email(db, user.email)
        if duplicate and duplicate.id != user_id:
            raise DuplicateFieldError("Email already exists")

    return await crud.update_user(db, user_id, updated_data)


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


def calculate_priority(
    user_status: str, delivery_type: str, order_amount: Decimal
) -> float:

    def get_order_amount_points(amount: Decimal) -> int:
        if amount < 500:
            return priority_points["order_amount"]["under_500"]

        elif amount <= 2000:
            return priority_points["order_amount"]["in_range_500_2000"]

        else:
            return priority_points["order_amount"]["over_2000"]

    user_status_points = priority_points["user_status"].get(user_status, 0)
    delivery_type_points = priority_points["delivery_type"].get(delivery_type, 0)
    order_amount_points = get_order_amount_points(order_amount)

    score = (
        user_status_points * 0.4
        + delivery_type_points * 0.35
        + order_amount_points * 0.25
    )

    return round(score, 1)


async def get_order(db: AsyncSession, order_id: int, user: User) -> Order:
    order = await crud.get_order_by_id(db, order_id)

    if not order:
        raise OrderNotFoundError()

    if order.user_id != user.id and user.role != UserRole.ADMIN:
        raise PermissionDeniedError()

    return order


async def get_orders(
    db: AsyncSession,
    limit: int,
    offset: int,
    user: User,
    admin_action: bool = False,
    filters: OrderFilter | None = None,
) -> tuple[int, list[Order]]:
    if admin_action:
        return await crud.get_orders(db, limit=limit, offset=offset, filters=filters)

    return await crud.get_orders(
        db,
        limit=limit,
        offset=offset,
        owner_id=user.id,
    )


async def create_order(db: AsyncSession, order: OrderCreate, user: User) -> Order:
    items = order.model_dump()["items"]
    items_map = {item["book_id"]: item["quantity"] for item in items}

    books_task = [crud.get_book_by_id(db, id) for id in items_map.keys()]
    books = await asyncio.gather(*books_task)

    books_map = dict(zip(items_map.keys(), books))

    not_existed_book_ids = [id for id, book in books_map.items() if book is None]
    if not_existed_book_ids:
        raise EntityNotFoundError(entity_name="Book", entity_ids=not_existed_book_ids)

    insufficient_stock_qty_book_ids = [
        id for id, book in books_map.items() if book.stock_quantity < items_map[id]
    ]
    if insufficient_stock_qty_book_ids:
        raise InsufficientStockQuantityError(book_ids=insufficient_stock_qty_book_ids)

    total_amount = Decimal(
        sum([items_map[id] * book.price for id, book in books_map.items()])
    )
    priority = calculate_priority(
        user_status=user.status,
        delivery_type=order.delivery_type,
        order_amount=total_amount,
    )

    order_create_in_db = OrderCreateInDB(
        **order.model_dump(),
        user_id=user.id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        priority=priority,
    )
    return await crud.create_order(db, order_create_in_db)


async def update_order(
    db: AsyncSession, order_id: int, order_update: OrderUpdate
) -> Order:
    order = await crud.get_order_by_id(db, order_id)
    if not order:
        raise OrderNotFoundError()

    return await crud.update_order(db, order_id, order_update)


async def delete_order(db: AsyncSession, order_id: int) -> None:
    order = await crud.get_order_by_id(db, order_id)
    if not order:
        raise OrderNotFoundError()

    await crud.delete_order(db, order_id)
