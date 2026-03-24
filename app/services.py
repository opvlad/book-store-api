from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.models import User
from app.schemas import UserCreate, UserCreateInDB, UserUpdate, LoginForm, Token
from app.security import get_password_hash, verify_password, create_access_token
from app.exeptions import UserNotFoundError, DuplicateFieldError, UnauthorizedError


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await crud.get_user_by_id(db, user_id)
    return result


async def get_users(
    db: AsyncSession, offset: int = 0, limit: int = 100
) -> dict[str, int | list[User]]:
    items = await crud.get_users(db, offset, limit)
    result = {"total": len(items), "limit": limit, "offset": offset, "items": items}
    return result


async def register_user(db: AsyncSession, user: UserCreate) -> User:
    if await crud.get_user_by_username(db, user.username):
        raise DuplicateFieldError("Username already exists")

    if await crud.get_user_by_email(db, user.email):
        raise DuplicateFieldError("Email already exists")

    user_in_db = UserCreateInDB(
        **user.model_dump(exclude={"password"}),
        password_hash=get_password_hash(user.password),
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


async def login_user(db: AsyncSession, credentials: LoginForm) -> Token:
    db_user = await crud.get_user_by_username(db, credentials.username)

    if not db_user:
        raise UserNotFoundError()

    if not verify_password(credentials.password, db_user.password_hash):
        raise UnauthorizedError()

    access_token = create_access_token({"id": db_user.id})
    return Token(access_token=access_token)
