from enum import StrEnum
from decimal import Decimal
from datetime import date, datetime, UTC

from sqlalchemy import String, Text, Identity, ForeignKey, Numeric, DateTime, func, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    books: Mapped[list["Book"]] = relationship(back_populates="author", lazy="selectin")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    stock_quantity: Mapped[int] = mapped_column(default=0, server_default="0")
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    author: Mapped["Author"] = relationship(back_populates="books", lazy="joined")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            values_callable=lambda elements: [element.value for element in elements],
        ),
        default=UserRole.USER,
        server_default="user",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        lazy="selectin",
        order_by="Order.id",
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            values_callable=lambda elements: [element.value for element in elements],
        ),
        default=OrderStatus.PENDING,
        server_default="pending",
    )
    quantity: Mapped[int]
    total_amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="orders", lazy="joined")
    book: Mapped["Book"] = relationship(lazy="joined")
