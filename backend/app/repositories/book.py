from sqlalchemy.orm import Session

from app.models.author import Author
from app.models.book import Book
from app.models.genre import Genre
from app.models.publisher import Publisher
from app.schemas.book import BookCreate, BookUpdate


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Book]:
        return self.db.query(Book).all()

    def get(self, book_id: int) -> Book | None:
        return self.db.get(Book, book_id)

    def _validate_ids(self, publisher_id, author_ids, genre_ids):
        if publisher_id is not None and self.db.get(Publisher, publisher_id) is None:
            raise ValueError("Publisher not found")
        if author_ids:
            for author_id in author_ids:
                if self.db.get(Author, author_id) is None:
                    raise ValueError("Author not found")
        if genre_ids:
            for genre_id in genre_ids:
                if self.db.get(Genre, genre_id) is None:
                    raise ValueError("Genre not found")

    def create(self, data: BookCreate) -> Book:
        self._validate_ids(data.publisher_id, data.author_ids, data.genre_ids)
        payload = data.model_dump(exclude={"author_ids", "genre_ids"})
        book = Book(**payload)
        if data.author_ids:
            book.authors = self.db.query(Author).filter(Author.id.in_(data.author_ids)).all()
        if data.genre_ids:
            book.genres = self.db.query(Genre).filter(Genre.id.in_(data.genre_ids)).all()
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def update(self, book: Book, data: BookUpdate) -> Book:
        values = data.model_dump(exclude_unset=True)
        author_ids = values.pop("author_ids", None)
        genre_ids = values.pop("genre_ids", None)
        publisher_id = values.pop("publisher_id", None) if "publisher_id" in values else None
        has_publisher = "publisher_id" in data.model_dump(exclude_unset=True)

        self._validate_ids(
            publisher_id if has_publisher else None,
            author_ids,
            genre_ids,
        )
        for key, value in values.items():
            setattr(book, key, value)
        if has_publisher:
            book.publisher_id = publisher_id
        if author_ids is not None:
            book.authors = self.db.query(Author).filter(Author.id.in_(author_ids)).all() if author_ids else []
        if genre_ids is not None:
            book.genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all() if genre_ids else []
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        self.db.delete(book)
        self.db.commit()
