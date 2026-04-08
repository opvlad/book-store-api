from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from cashews import cache
from datetime import date
from decimal import Decimal

from app.main import app
from app.database import Base, get_db
from app.models import UserRole, User, Author, Book, Order
from app.security import get_password_hash, create_access_token
from app.services import calculate_priority


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
async def test_author(db_session) -> Author:
    test_author = Author(
        name="John Doe", bio="Test biography", birth_date=date(2000, 2, 1)
    )
    db_session.add(test_author)
    await db_session.commit()
    await db_session.refresh(test_author)
    return test_author


@pytest.fixture()
async def test_book(db_session, test_author) -> Book:
    test_book = Book(
        title="Test Book",
        description="Test description",
        price=Decimal("100"),
        stock_quantity=10,
        author_id=test_author.id,
    )
    db_session.add(test_book)
    await db_session.commit()
    await db_session.refresh(test_book)
    return test_book


@pytest.fixture()
async def test_other_book(db_session, test_author) -> Book:
    test_book = Book(
        title="Other Book",
        description="Other description",
        price=Decimal("50.2"),
        stock_quantity=5,
        author_id=test_author.id,
    )
    db_session.add(test_book)
    await db_session.commit()
    await db_session.refresh(test_book)
    return test_book


@pytest.fixture()
async def test_order(db_session, test_user, test_book) -> Order:
    test_order = Order(
        user_id=test_user.id,
        book_id=test_book.id,
        quantity=5,
        total_amount=Decimal(test_book.price * 5),
        priority=calculate_priority(test_user.status, "standard", Decimal(test_book.price * 5))
    )
    db_session.add(test_order)
    await db_session.commit()
    await db_session.refresh(test_order)
    return test_order


@pytest.fixture()
async def user_token(db_session, test_user) -> str:
    return create_access_token(data={"id": test_user.id})


@pytest.fixture()
async def admin_token(db_session, test_admin) -> str:
    return create_access_token(data={"id": test_admin.id})


