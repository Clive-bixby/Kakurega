from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    title: str
    subtitle: str | None = None
    isbn10: str | None = None
    isbn13: str | None = None
    description: str | None = None
    pages: int | None = None
    language: str | None = None
    published_year: int | None = None
    cover_url: str | None = None
    google_books_id: str | None = None
    openlibrary_id: str | None = None
    publisher_id: int | None = None
    author_ids: list[int] = []
    genre_ids: list[int] = []


class BookRead(BookCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    isbn10: str | None = None
    isbn13: str | None = None
    description: str | None = None
    pages: int | None = None
    language: str | None = None
    published_year: int | None = None
    cover_url: str | None = None
    google_books_id: str | None = None
    openlibrary_id: str | None = None
    publisher_id: int | None = None
    author_ids: list[int] | None = None
    genre_ids: list[int] | None = None
