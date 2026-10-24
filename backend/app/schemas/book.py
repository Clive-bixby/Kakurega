from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.isbn import canonicalize_isbns
from app.schemas.taxonomy import NamedEntityRead, PublisherRead


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    subtitle: str | None = Field(default=None, max_length=500)
    isbn10: str | None = None
    isbn13: str | None = None
    description: str | None = None
    notes: str | None = None
    pages: int | None = Field(default=None, gt=0, le=100_000)
    language: str | None = Field(default=None, max_length=20)
    published_year: int | None = Field(default=None, ge=1000)
    cover_url: str | None = Field(default=None, max_length=1000)
    google_books_id: str | None = Field(default=None, max_length=100)
    openlibrary_id: str | None = Field(default=None, max_length=100)
    publisher_id: int | None = None
    author_ids: list[int] = Field(default_factory=list)
    genre_ids: list[int] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)

    @field_validator("title", "subtitle", "language", "notes", mode="before")
    @classmethod
    def _strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("published_year")
    @classmethod
    def _year_not_in_future(cls, value: int | None) -> int | None:
        if value is not None and value > datetime.now(timezone.utc).year + 1:
            raise ValueError("published_year cannot be in the future")
        return value

    @model_validator(mode="before")
    @classmethod
    def _canonicalize_isbns(cls, data):
        if isinstance(data, dict) and ("isbn10" in data or "isbn13" in data):
            data = {**data}
            data["isbn10"], data["isbn13"] = canonicalize_isbns(
                data.get("isbn10"), data.get("isbn13")
            )
        return data


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    subtitle: str | None = Field(default=None, max_length=500)
    isbn10: str | None = None
    isbn13: str | None = None
    description: str | None = None
    notes: str | None = None
    pages: int | None = Field(default=None, gt=0, le=100_000)
    language: str | None = Field(default=None, max_length=20)
    published_year: int | None = Field(default=None, ge=1000)
    cover_url: str | None = Field(default=None, max_length=1000)
    google_books_id: str | None = Field(default=None, max_length=100)
    openlibrary_id: str | None = Field(default=None, max_length=100)
    publisher_id: int | None = None
    author_ids: list[int] | None = None
    genre_ids: list[int] | None = None
    tag_ids: list[int] | None = None

    @field_validator("title", "subtitle", "language", "notes", mode="before")
    @classmethod
    def _strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("published_year")
    @classmethod
    def _year_not_in_future(cls, value: int | None) -> int | None:
        if value is not None and value > datetime.now(timezone.utc).year + 1:
            raise ValueError("published_year cannot be in the future")
        return value

    @model_validator(mode="before")
    @classmethod
    def _reject_null_title(cls, data):
        if isinstance(data, dict) and "title" in data:
            title = data["title"]
            if title is None or (isinstance(title, str) and not title.strip()):
                raise ValueError("title cannot be null or blank")
        return data

    @model_validator(mode="before")
    @classmethod
    def _canonicalize_isbns(cls, data):
        if isinstance(data, dict) and ("isbn10" in data or "isbn13" in data):
            data = {**data}
            data["isbn10"], data["isbn13"] = canonicalize_isbns(
                data.get("isbn10"), data.get("isbn13")
            )
        return data


class BookRead(BookCreate):
    id: int
    created_at: datetime
    authors: list[NamedEntityRead] = Field(default_factory=list)
    genres: list[NamedEntityRead] = Field(default_factory=list)
    tags: list[NamedEntityRead] = Field(default_factory=list)
    publisher: PublisherRead | None = None

    model_config = ConfigDict(from_attributes=True)


class BookListItem(BaseModel):
    id: int
    title: str
    subtitle: str | None
    isbn10: str | None
    isbn13: str | None
    pages: int | None
    language: str | None
    published_year: int | None
    cover_url: str | None
    publisher_id: int | None
    created_at: datetime
    author_ids: list[int]
    genre_ids: list[int]
    tag_ids: list[int]

    model_config = ConfigDict(from_attributes=True)


class BookPage(BaseModel):
    items: list[BookListItem]
    total: int
    limit: int
    offset: int
