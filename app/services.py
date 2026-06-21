import os
import logging
from datetime import datetime, date, UTC
from decimal import Decimal
from tempfile import mkstemp

from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import Workbook
from resend.exceptions import ResendError

from app import crud
from app.config.settings import priority_points
from app.config.base_email_messages import get_base_message
from app.models import User, Author, Book, Order, UserRole, OrderStatus
from app.security import get_password_hash, verify_password, create_access_token
from app.utils import send_email
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
    DuplicateFieldError,
    UnauthorizedError,
    AuthorIsNotAdultError,
)


logger = logging.getLogger(__name__)


# USERS


async def get_user(db: AsyncSession, user_id: int, requester: User) -> User | None:
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        logger.warning(
            f"USER_NOT_FOUND | requester_id={requester.id} | user_id={user_id}"
        )
        raise EntityNotFoundError(entity_name="User", entity_ids=user_id)
    return user


async def get_users(
    db: AsyncSession, offset: int, limit: int
) -> tuple[int, list[User]]:
    return await crud.get_users(db, offset=offset, limit=limit)


async def register_user(db: AsyncSession, user: UserCreate) -> User:
    if await crud.get_user_by_username(db, user.username):
        logger.warning(f"REGISTER_DUPLICATE | username={user.username}")
        raise DuplicateFieldError("Username already exists")

    if await crud.get_user_by_email(db, user.email):
        logger.warning(f"REGISTER_DUPLICATE | email={user.email}")
        raise DuplicateFieldError("Email already exists")

    user_in_db = UserCreateInDB(
        **user.model_dump(exclude={"password"}),
        password_hash=get_password_hash(user.password),
    )
    new_user = await crud.create_user(db, user_in_db)

    logger.info(f"REGISTER_SUCCESS | user_id={new_user.id}")

    return new_user


async def update_user(
    db: AsyncSession,
    user_id: int,
    user: UserUpdate | UserUpdateAsAdmin,
    requester: User,
) -> User:
    existing_user = await crud.get_user_by_id(db, user_id)
    if not existing_user:
        logger.warning(
            f"USER_UPDATE_NOT_FOUND | requester_id={requester.id} | user_id={user_id}"
        )
        raise EntityNotFoundError(entity_name="User", entity_ids=user_id)

    updated_data = user.model_dump(exclude_unset=True)

    if "username" in updated_data:
        duplicate = await crud.get_user_by_username(db, user.username)
        if duplicate and duplicate.id != user_id:
            logger.warning(
                f"USER_UPDATE_DUPLICATE | requester_id={requester.id} | user_id={user_id} | username={user.username}"
            )
            raise DuplicateFieldError("Username already exists")

    if "email" in updated_data:
        duplicate = await crud.get_user_by_email(db, user.email)
        if duplicate and duplicate.id != user_id:
            logger.warning(
                f"USER_UPDATE_DUPLICATE | requester_id={requester.id} | user_id={user_id} | email={user.email}"
            )
            raise DuplicateFieldError("Email already exists")

    user_updated = await crud.update_user(db, user_id, updated_data)
    logger.info(
        f"USER_UPDATED | requester_id={requester.id} | user_id={user_id} | data={updated_data}"
    )
    return user_updated


async def delete_user(db: AsyncSession, user_id: int, requester: User) -> None:
    if not await crud.get_user_by_id(db, user_id):
        logger.warning(
            f"USER_DELETE_NOT_FOUND | requester_id={requester.id} | user_id={user_id}"
        )
        raise EntityNotFoundError(entity_name="User", entity_ids=user_id)

    await crud.delete_user(db, user_id)
    logger.info(f"USER_DELETED | requester_id={requester.id} | user_id={user_id}")


async def login_user(db: AsyncSession, credentials: LoginForm) -> str:
    db_user = await crud.get_user_by_username(db, credentials.username)

    if not db_user:
        logger.warning(f"LOGIN_USER_NOT_FOUND | username={credentials.username}")
        raise UnauthorizedError()

    if not verify_password(credentials.password, db_user.password_hash):
        logger.warning(f"LOGIN_INVALID_PASSWORD | user_id={db_user.id}")
        raise UnauthorizedError()

    access_token = create_access_token({"id": db_user.id})
    logger.info(f"LOGIN_SUCCESS | user_id={db_user.id}")
    return access_token


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
        logger.warning(f"AUTHOR_NOT_FOUND | author_id={author_id}")
        raise EntityNotFoundError(entity_name="Author", entity_ids=author_id)
    return result


async def get_authors(
    db: AsyncSession, offset: int, limit: int
) -> tuple[int, list[Author]]:
    return await crud.get_authors(db, offset=offset, limit=limit)


async def create_author(
    db: AsyncSession, author: AuthorCreate, requester: User
) -> Author:
    if not is_adult(author.birth_date):
        logger.warning(
            f"AUTHOR_CREATE_UNDERAGE | requester_id={requester.id} | birth_date={author.birth_date}"
        )
        raise AuthorIsNotAdultError()

    author_created = await crud.create_author(db, author)
    logger.info(
        f"AUTHOR_CREATED | requester_id={requester.id} | author_id={author_created.id}"
    )
    return author_created


async def update_author(
    db: AsyncSession, author_id: int, author: AuthorUpdate, requester: User
) -> Author:
    existing_author = await crud.get_author_by_id(db, author_id)
    if not existing_author:
        logger.warning(
            f"AUTHOR_UPDATE_NOT_FOUND | requester_id={requester.id} | author_id={author_id}"
        )
        raise EntityNotFoundError(entity_name="Author", entity_ids=author_id)

    if author.birth_date and not is_adult(author.birth_date):
        logger.warning(
            f"AUTHOR_UPDATE_UNDERAGE | requester_id={requester.id} | birth_date={author.birth_date}"
        )
        raise AuthorIsNotAdultError()

    author_updated = await crud.update_author(db, author_id, author)
    logger.info(
        f"AUTHOR_UPDATED | requester_id={requester.id} | author_id={author_id}"
        f"{author.model_dump_json(exclude_unset=True)}"
    )
    return author_updated


async def delete_author(db: AsyncSession, author_id: int, requester: User) -> None:
    existing_author = await crud.get_author_by_id(db, author_id)
    if not existing_author:
        logger.warning(
            f"AUTHOR_DELETE_NOT_FOUND | requester_id={requester.id} | author_id={author_id}"
        )
        raise EntityNotFoundError(entity_name="Author", entity_ids=author_id)

    await crud.delete_author(db, author_id)
    logger.info(f"AUTHOR_DELETED | requester_id={requester.id} | author_id={author_id}")


# BOOKS


async def get_book(db: AsyncSession, book_id: int) -> Book:
    book = await crud.get_book_by_id(db, book_id)
    if not book:
        logger.warning(f"BOOK_NOT_FOUND | book_id={book_id}")
        raise EntityNotFoundError(entity_name="Book", entity_ids=book_id)
    return book


async def get_books(
    db: AsyncSession, limit: int, offset: int
) -> tuple[int, list[Book]]:
    return await crud.get_books(db, limit=limit, offset=offset)


async def create_book(db: AsyncSession, book: BookCreate, requester: User) -> Book:
    existing_author = await crud.get_author_by_id(db, book.author_id)
    if not existing_author:
        logger.warning(
            f"BOOK_CREATE_AUTHOR_NOT_FOUND | requester_id={requester.id} | author_id={book.author_id}"
        )
        raise EntityNotFoundError(entity_name="Author", entity_ids=book.author_id)

    book_created = await crud.create_book(db, book)
    logger.info(
        f"BOOK_CREATED | requester_id={requester.id} | book_id={book_created.id}"
    )
    return book_created


async def update_book(
    db: AsyncSession, book_id: int, book_update: BookUpdate, requester: User
) -> Book:
    existing_book = await crud.get_book_by_id(db, book_id)
    if not existing_book:
        logger.warning(
            f"BOOK_UPDATE_NOT_FOUND | requester_id={requester.id} | book_id={book_id}"
        )
        raise EntityNotFoundError(entity_name="Book", entity_ids=book_id)

    if book_update.author_id is not None:
        existing_author = await crud.get_author_by_id(db, book_update.author_id)
        if not existing_author:
            logger.warning(
                f"BOOK_UPDATE_AUTHOR_NOT_FOUND | requester_id={requester.id} | author_id={book_update.author_id}"
            )
            raise EntityNotFoundError(
                entity_name="Author", entity_ids=book_update.author_id
            )

    book_updated = await crud.update_book(db, book_id, book_update)
    logger.info(
        f"BOOK_UPDATED | requester_id={requester.id} | book_id={book_id} | data={book_update.model_dump_json(exclude_unset=True)}"
    )
    return book_updated


async def delete_book(db: AsyncSession, book_id: int, requester: User) -> None:
    existing_book = await crud.get_book_by_id(db, book_id)
    if not existing_book:
        logger.warning(
            f"BOOK_DELETE_NOT_FOUND | requester_id={requester.id} | book_id={book_id}"
        )
        raise EntityNotFoundError(entity_name="Book", entity_ids=book_id)

    await crud.delete_book(db, book_id)
    logger.info(f"BOOK_DELETED | requester_id={requester.id} | book_id={book_id}")


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
        logger.warning(
            f"ORDER_NOT_FOUND | requester_id={user.id} | order_id={order_id}"
        )
        raise EntityNotFoundError(entity_name="Order", entity_ids=order_id)

    if order.user_id != user.id and user.role != UserRole.ADMIN:
        raise PermissionDeniedError(user_id=user.id)

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

    books = await crud.get_books_by_ids(db, list(items_map.keys()))
    books_map = {book.id: book for book in books}

    not_existed_book_ids = list(items_map.keys() - books_map.keys())
    if not_existed_book_ids:
        logger.warning(
            f"ORDER_CREATE_NOT_FOUND | requester_id={user.id} | book_ids={not_existed_book_ids}"
        )
        raise EntityNotFoundError(entity_name="Book", entity_ids=not_existed_book_ids)

    insufficient_stock_qty_book_ids = [
        book_id
        for book_id, book in books_map.items()
        if book.stock_quantity < items_map[book_id]
    ]
    if insufficient_stock_qty_book_ids:
        logger.warning(
            f"ORDER_CREATE_INSUFFICIENT_BOOKS | requester_id={user.id} | book_ids={insufficient_stock_qty_book_ids}"
        )
        raise InsufficientStockQuantityError(book_ids=insufficient_stock_qty_book_ids)

    for book in books:
        new_stock_quantity = book.stock_quantity - items_map[book.id]
        await crud.update_book(
            db, book.id, BookUpdate(stock_quantity=new_stock_quantity)
        )

    total_amount = Decimal(
        sum([items_map[book_id] * book.price for book_id, book in books_map.items()])
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
    order_created = await crud.create_order(db, order_create_in_db)
    logger.info(f"ORDER_CREATED | order_id={order_created.id}")

    message = get_base_message(
        "order_created", user_name=user.username, order=order_created
    )
    if message is not None:
        try:
            send_email(subject="Order is created", body=message, to=[user.email])
        except ResendError:
            pass
        except Exception:
            raise
    else:
        logger.warning("EMAIL_ERROR | message is None")

    return order_created


async def update_order(
    db: AsyncSession, order_id: int, order_update: OrderUpdate, requester: User
) -> Order:
    order = await crud.get_order_by_id(db, order_id)
    if not order:
        logger.warning(
            f"ORDER_UPDATE_NOT_FOUND | requester_id={requester.id} | order_id={order_id}"
        )
        raise EntityNotFoundError(entity_name="Order", entity_ids=order_id)

    order_updated = await crud.update_order(db, order_id, order_update)
    logger.info(
        f"ORDER_UPDATED | requester_id={requester.id} | order_id={order_updated.id} | data="
        f"{order_update.model_dump_json(exclude_none=True)}"
    )
    return order_updated


async def delete_order(db: AsyncSession, order_id: int, requester: User) -> None:
    order = await crud.get_order_by_id(db, order_id)
    if not order:
        logger.warning(
            f"ORDER_DELETE_NOT_FOUND | requester_id={requester.id} | order_id={order_id}"
        )
        raise EntityNotFoundError(entity_name="Order", entity_ids=order_id)

    await crud.delete_order(db, order_id)
    logger.info(f"ORDER_DELETED | requester_id={requester.id} | order_id={order_id}")


async def export_orders(db: AsyncSession, limit: int, offset: int) -> tuple[str, str]:
    orders_steam = await crud.get_orders_stream(db, limit=limit, offset=offset)
    updated_at = datetime.now(UTC)
    final_file_name = f"Orders_report_{updated_at.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

    wb = Workbook(write_only=True)
    ws = wb.create_sheet("Orders Report")

    columns = list(Order.__table__.columns.keys())
    ws.append(columns)

    async for order in orders_steam:
        result_row = []

        for column in columns:
            if column == "items":
                cell = []
                for item in order.items:
                    cell.append(
                        f"book_id: {item['book_id']}, quantity: {item['quantity']}"
                    )
                result_row.append("\n".join(cell))
                continue

            if column == "created_at":
                result_row.append(order.created_at.strftime("%Y-%m-%d %H:%M:%S"))
                continue

            result_row.append(getattr(order, column))

        ws.append(result_row)

    fd, temp_file_path = mkstemp()
    os.close(fd)

    wb.save(temp_file_path)
    return temp_file_path, final_file_name
