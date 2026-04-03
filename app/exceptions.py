class DuplicateFieldError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class EntityNotFoundError(Exception):
    def __init__(self, status_code: int, entity_name: str, entity_id: int):
        self.status_code = status_code
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

