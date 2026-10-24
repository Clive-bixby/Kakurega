from sqlalchemy.orm import Session

from app.core.isbn import canonicalize_isbns, normalize_isbn
from app.models.book import Book
from app.repositories.book import BookFilters, BookRepository
from app.schemas.book import BookCreate, BookUpdate


class BookService:
    def __init__(self, db: Session):
        self.repo = BookRepository(db)

    def list_books(
        self,
        filters: BookFilters,
        limit: int,
        offset: int,
        sort: str = "title",
    ) -> tuple[list[Book], int]:
        return self.repo.list(filters, limit, offset, sort)

    def get_book(self, book_id: int) -> Book | None:
        return self.repo.get(book_id)

    def get_book_by_isbn(self, isbn: str) -> Book | None:
        cleaned = normalize_isbn(isbn)
        if cleaned is None:
            return None
        try:
            if len(cleaned) == 10:
                isbn10, isbn13 = canonicalize_isbns(cleaned, None)
            else:
                isbn10, isbn13 = canonicalize_isbns(None, cleaned)
        except ValueError:
            return None
        book = self.repo.find_by_isbn(isbn10, isbn13)
        if book is None:
            return None
        return self.repo.get(book.id)

    def create_book(self, data: BookCreate) -> Book:
        return self.repo.create(data)

    def update_book(self, book_id: int, data: BookUpdate) -> Book | None:
        book = self.repo.get(book_id)
        if book is None:
            return None
        return self.repo.update(book, data)

    def delete_book(self, book_id: int) -> bool:
        book = self.repo.get(book_id)
        if book is None:
            return False
        self.repo.delete(book)
        return True
