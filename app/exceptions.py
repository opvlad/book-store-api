class DuplicateFieldError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InsufficientStockQuantityError(Exception):
    def __init__(self, book_ids: list[int]):
        self.book_ids = book_ids
        super().__init__(f"Books with ids {book_ids} have insufficient stock quantity")


class UnauthorizedError(Exception):
    def __init__(self):
        message = "Incorrect username or password"
        super().__init__(message)


class PermissionDeniedError(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id
        message = "Permission denied"
        super().__init__(message)


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


class InvalidTokenError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        message = "Invalid token"
        super().__init__(message)
