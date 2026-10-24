from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.associations import book_authors, book_genres


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        Index(
            "uq_books_isbn10",
            "isbn10",
            unique=True,
            postgresql_where=text("isbn10 IS NOT NULL"),
            sqlite_where=text("isbn10 IS NOT NULL"),
        ),
        Index(
            "uq_books_isbn13",
            "isbn13",
            unique=True,
            postgresql_where=text("isbn13 IS NOT NULL"),
            sqlite_where=text("isbn13 IS NOT NULL"),
        ),
        Index("ix_books_title", "title"),
        Index("ix_books_published_year", "published_year"),
        Index("ix_books_publisher_id", "publisher_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500))
    isbn10: Mapped[str | None] = mapped_column(String(10))
    isbn13: Mapped[str | None] = mapped_column(String(13))
    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    pages: Mapped[int | None] = mapped_column(Integer)
    language: Mapped[str | None] = mapped_column(String(20))
    published_year: Mapped[int | None] = mapped_column(Integer)
    cover_url: Mapped[str | None] = mapped_column(String(1000))
    google_books_id: Mapped[str | None] = mapped_column(String(100))
    openlibrary_id: Mapped[str | None] = mapped_column(String(100))
    publisher_id: Mapped[int | None] = mapped_column(ForeignKey("publishers.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    publisher: Mapped["Publisher | None"] = relationship("Publisher")
    authors: Mapped[list["Author"]] = relationship("Author", secondary=book_authors)
    genres: Mapped[list["Genre"]] = relationship("Genre", secondary=book_genres)

    @property
    def author_ids(self) -> list[int]:
        return [author.id for author in self.authors]

    @property
    def genre_ids(self) -> list[int]:
        return [genre.id for genre in self.genres]
