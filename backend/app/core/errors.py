class DomainError(Exception):
    """Base class for errors that map to a client-facing HTTP status."""


class DuplicateBookError(DomainError):
    def __init__(self, book_id: int):
        self.book_id = book_id
        super().__init__("A book with this ISBN already exists")


class InvalidReferenceError(DomainError):
    pass


class DuplicateMemberError(DomainError):
    def __init__(self):
        super().__init__("A member with this name already exists")


class InvalidReadingError(DomainError):
    pass
