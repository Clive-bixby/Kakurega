from dataclasses import dataclass

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.errors import DuplicateBookError, InvalidReferenceError
from app.core.isbn import isbn_search_terms
from app.models.author import Author
from app.models.book import Book
from app.models.genre import Genre
from app.models.publisher import Publisher
from app.schemas.book import BookCreate, BookUpdate


@dataclass
class BookFilters:
    q: str | None = None
    genre_id: int | None = None
    year_from: int | None = None
    year_to: int | None = None


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _sorted(statement, sort: str):
    if sort == "added":
        return statement.order_by(Book.created_at.desc(), Book.id.desc())
    if sort == "year":
        return statement.order_by(
            Book.published_year.desc().nulls_last(), func.lower(Book.title)
        )
    return statement.order_by(func.lower(Book.title), Book.id)


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        filters: BookFilters,
        limit: int,
        offset: int,
        sort: str = "title",
    ) -> tuple[list[Book], int]:
        statement = select(Book)
        count_statement = select(func.count(distinct(Book.id)))

        if filters.q:
            pattern = f"%{_escape_like(filters.q)}%"
            conditions = [
                Book.title.ilike(pattern, escape="\\"),
                Book.subtitle.ilike(pattern, escape="\\"),
                Book.description.ilike(pattern, escape="\\"),
                Author.name.ilike(pattern, escape="\\"),
                Publisher.name.ilike(pattern, escape="\\"),
            ]
            isbn10, isbn13 = isbn_search_terms(filters.q)
            isbn_conditions = []
            if isbn10:
                isbn_conditions.append(Book.isbn10 == isbn10)
            if isbn13:
                isbn_conditions.append(Book.isbn13 == isbn13)
            if isbn_conditions:
                conditions.append(or_(*isbn_conditions))

            condition = or_(*conditions)
            statement = statement.outerjoin(Book.authors).outerjoin(Book.publisher)
            count_statement = count_statement.outerjoin(Book.authors).outerjoin(
                Book.publisher
            )
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        if filters.genre_id is not None:
            statement = statement.join(Book.genres).where(Genre.id == filters.genre_id)
            count_statement = count_statement.join(Book.genres).where(
                Genre.id == filters.genre_id
            )

        if filters.year_from is not None:
            statement = statement.where(Book.published_year >= filters.year_from)
            count_statement = count_statement.where(
                Book.published_year >= filters.year_from
            )

        if filters.year_to is not None:
            statement = statement.where(Book.published_year <= filters.year_to)
            count_statement = count_statement.where(
                Book.published_year <= filters.year_to
            )

        total = self.db.execute(count_statement).scalar_one()
        statement = (
            statement.options(selectinload(Book.authors), selectinload(Book.genres))
            .offset(offset)
            .limit(limit)
        )
        books = self.db.execute(_sorted(statement, sort)).scalars().unique().all()
        return list(books), total

    def get(self, book_id: int) -> Book | None:
        statement = (
            select(Book)
            .where(Book.id == book_id)
            .options(selectinload(Book.authors), selectinload(Book.genres))
        )
        return self.db.execute(statement).scalars().first()

    def find_by_isbn(
        self, isbn10: str | None, isbn13: str | None, exclude_id: int | None = None
    ) -> Book | None:
        conditions = []
        if isbn10:
            conditions.append(Book.isbn10 == isbn10)
        if isbn13:
            conditions.append(Book.isbn13 == isbn13)
        if not conditions:
            return None
        statement = select(Book).where(or_(*conditions))
        if exclude_id is not None:
            statement = statement.where(Book.id != exclude_id)
        return self.db.execute(statement).scalars().first()

    def _validate_ids(self, publisher_id, author_ids, genre_ids):
        if publisher_id is not None and self.db.get(Publisher, publisher_id) is None:
            raise InvalidReferenceError("Publisher not found")
        for author_id in author_ids or []:
            if self.db.get(Author, author_id) is None:
                raise InvalidReferenceError("Author not found")
        for genre_id in genre_ids or []:
            if self.db.get(Genre, genre_id) is None:
                raise InvalidReferenceError("Genre not found")

    def _ensure_unique_isbn(self, isbn10, isbn13, exclude_id=None) -> None:
        existing = self.find_by_isbn(isbn10, isbn13, exclude_id)
        if existing is not None:
            raise DuplicateBookError(existing.id)

    def create(self, data: BookCreate) -> Book:
        self._validate_ids(data.publisher_id, data.author_ids, data.genre_ids)
        self._ensure_unique_isbn(data.isbn10, data.isbn13)

        payload = data.model_dump(exclude={"author_ids", "genre_ids"})
        book = Book(**payload)
        if data.author_ids:
            book.authors = (
                self.db.query(Author).filter(Author.id.in_(data.author_ids)).all()
            )
        if data.genre_ids:
            book.genres = (
                self.db.query(Genre).filter(Genre.id.in_(data.genre_ids)).all()
            )
        self.db.add(book)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            self._ensure_unique_isbn(data.isbn10, data.isbn13)
            raise InvalidReferenceError("Invalid book data") from exc
        self.db.refresh(book)
        return book

    def update(self, book: Book, data: BookUpdate) -> Book:
        values = data.model_dump(exclude_unset=True)
        author_ids = values.pop("author_ids", None)
        genre_ids = values.pop("genre_ids", None)
        has_publisher = "publisher_id" in values
        publisher_id = values.pop("publisher_id", None)

        self._validate_ids(
            publisher_id if has_publisher else None,
            author_ids,
            genre_ids,
        )
        if "isbn10" in values or "isbn13" in values:
            self._ensure_unique_isbn(
                values.get("isbn10", book.isbn10),
                values.get("isbn13", book.isbn13),
                exclude_id=book.id,
            )

        for key, value in values.items():
            setattr(book, key, value)
        if has_publisher:
            book.publisher_id = publisher_id
        if author_ids is not None:
            book.authors = (
                self.db.query(Author).filter(Author.id.in_(author_ids)).all()
                if author_ids
                else []
            )
        if genre_ids is not None:
            book.genres = (
                self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
                if genre_ids
                else []
            )
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise InvalidReferenceError("Invalid book data") from exc
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        self.db.delete(book)
        self.db.commit()
