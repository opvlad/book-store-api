from pygments.lexers.templates import VelocityLexer
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.models import User
from app.schemas import UserCreate, UserCreateInDB, UserUpdate
from app.security import get_password_hash
from app.exeptions import UserNotFoundError, DuplicateFieldError



async def get_user_details(user_id: int, db: AsyncSession) -> User | None:
    result = await crud.get_user_by_id(db, user_id)
    return result


async def get_users(
    db: AsyncSession, offset: int = 0, limit: int = 100
) -> dict[str, int | list[User]]:
    items = await crud.get_users(db, offset, limit)
    result = {"total": len(items), "limit": limit, "offset": offset, "items": items}
    return result


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    if await crud.get_user_by_username(db, user.username):
        raise ValueError("Username already exists")
    if await crud.get_user_by_email(db, user.email):
        raise ValueError("Email already exists")

    user_in_db = UserCreateInDB(
        **user.model_dump(exclude={"password"}),
        password_hash = get_password_hash(user.password),
    )

    result = await crud.create_user(db, user_in_db)
    return result


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

    result = await crud.update_user(db, user_id, user)
    return result


async def delete_user(db: AsyncSession, user_id: int) -> None:
    if not await crud.get_user_by_id(db, user_id):
        raise UserNotFoundError()

    await crud.delete_user(db, user_id)
