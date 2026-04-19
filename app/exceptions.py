class DuplicateFieldError(Exception):
    pass


class InsufficientStockQuantityError(Exception):
    def __init__(self, book_ids: list[int]):
        self.book_ids = book_ids
        super().__init__(f"Books with ids {book_ids} have insufficient stock quantity")


class UnauthorizedError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class EntityNotFoundError(Exception):
    def __init__(self, entity_name: str, entity_ids: list[id]):
        self.entity_name = entity_name
        self.entity_ids = entity_ids
        super().__init__(f"{entity_name}s with ids {entity_ids} not found")


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

