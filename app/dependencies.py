import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserRole
from app.security import decode_token
from app.crud import get_user_by_id
from app.exceptions import InvalidTokenError, PermissionDeniedError


logger = logging.getLogger(__name__)


security = HTTPBearer()


sessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: sessionDep, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise InvalidTokenError(detail="Invalid token")

    user_id = payload.get("id")
    if not user_id:
        raise InvalidTokenError(detail="Not id in payload")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise InvalidTokenError(detail=f"User with id {user_id} not found")

    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise PermissionDeniedError(user_id=user.id)
    return user
