from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.models import User


async def get_user_details(user_id: int, db: AsyncSession) -> User | None:
    result = await crud.get_user_by_id(user_id, db)
    return result


async def get_users(
    db: AsyncSession, offset: int = 0, limit: int = 100
) -> dict[str, int | list[User]]:
    items = await crud.get_users(db, offset, limit)
    result = {"total": len(items), "limit": limit, "offset": offset, "items": items}
    return result
