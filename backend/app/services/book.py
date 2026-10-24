from sqlalchemy.orm import Session

from app.models.book import Book
from app.repositories.book import BookRepository
from app.schemas.book import BookCreate, BookUpdate


class BookService:
    def __init__(self, db: Session):
        self.repo = BookRepository(db)

    def list_books(self) -> list[Book]:
        return self.repo.list()

    def get_book(self, book_id: int) -> Book | None:
        return self.repo.get(book_id)

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
