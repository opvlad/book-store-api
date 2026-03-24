from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from cashews import cache

from app.main import app
from app.database import Base, get_db
from app.models import User, UserRole
from app.security import get_password_hash, create_access_token


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def setup_cache():
    cache.set_config("mem://")


@pytest.fixture(autouse=True)
async def clear_cache():
    yield
    await cache.clear()


@pytest.fixture()
async def test_user(db_session) -> User:
    test_user = User(
        username="test_username",
        email="test@test.com",
        password_hash=get_password_hash("secret"),
        role=UserRole.USER,
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


@pytest.fixture()
async def test_other_user(db_session) -> User:
    test_user = User(
        username="other_username",
        email="other@test.com",
        password_hash=get_password_hash("secret"),
        role=UserRole.USER,
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user


@pytest.fixture()
async def test_admin(db_session) -> User:
    test_admin = User(
        username="test_admin_username",
        email="admin@test.com",
        password_hash=get_password_hash("secret"),
        role=UserRole.ADMIN,
    )
    db_session.add(test_admin)
    await db_session.commit()
    await db_session.refresh(test_admin)
    return test_admin


@pytest.fixture()
async def admin_token(db_session, test_admin) -> str:
    return create_access_token(data={"id": test_admin.id})


@pytest.fixture()
async def get_update_context(test_user, admin_token):
    def _payload(update_type) -> dict:
        if update_type == "user_action":
            token = create_access_token(data={"id": test_user.id})
            return {
                "url": "api/v1/users/me/update",
                "headers": {"Authorization": f"Bearer {token}"},
            }

        return {
            "url": f"api/v1/users/{test_user.id}",
            "headers": {"Authorization": f"Bearer {admin_token}"},
        }

    return _payload
