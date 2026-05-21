from typing import TypeAlias

from app.models import Order, Book, User, Author
from app.schemas import (
    OrderResponse,
    OrderAdminResponse,
    BookResponse,
    UserResponse,
    AuthorResponse,
)


AnyModel: TypeAlias = Order | Book | User | Author
AnyResponse: TypeAlias = (
    OrderResponse | OrderAdminResponse | BookResponse | UserResponse | AuthorResponse
)


def assert_response_data(
    response_data: dict, model: type[AnyModel], response_schema: type[AnyResponse]
) -> None:
    response_data = response_schema.model_validate(response_data)
    db_data = response_schema.model_validate(model)

    assert response_data == db_data
