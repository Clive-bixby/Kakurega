from pydantic import BaseModel


class LookupRequest(BaseModel):
    isbn: str | None = None
    title: str | None = None
    author: str | None = None


class MetadataResponse(BaseModel):
    title: str
    authors: list[str] = []
    publisher: str | None = None
    published_year: int | None = None
    isbn10: str | None = None
    isbn13: str | None = None
    description: str | None = None
    cover_url: str | None = None
    pages: int | None = None
    source: str
    confidence: float
