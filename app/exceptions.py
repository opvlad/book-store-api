class DuplicateFieldError(Exception):
    pass


class ZeroStockQuantityError(Exception):
    def __init__(self, book_id: int):
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} has zero stock quantity")


class UnauthorizedError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class EntityNotFoundError(Exception):
    def __init__(self, entity_name: str, entity_id: int):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(f"{entity_name} with id {entity_id} not found")


class UserNotFoundError(Exception):
    pass


class AuthorNotFoundError(Exception):
    pass


class AuthorIsNotAdultError(Exception):
    pass


class BookNotFoundError(Exception):
    pass


class OrderNotFoundError(Exception):
    pass

