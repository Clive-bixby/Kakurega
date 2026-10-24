from datetime import datetime

from pydantic import BaseModel, Field


class CurrentlyReading(BaseModel):
    book_id: int
    book_title: str
    member_id: int
    member_name: str
    current_page: int | None
    pages: int | None


class NamedCount(BaseModel):
    id: int
    name: str
    count: int


class RecentlyAdded(BaseModel):
    book_id: int
    title: str
    cover_url: str | None
    created_at: datetime


class InsightsResponse(BaseModel):
    total_books: int
    total_members: int
    by_published_year: dict[int, int]
    by_genre: list[NamedCount] = Field(default_factory=list)
    by_author: list[NamedCount] = Field(default_factory=list)
    by_language: dict[str, int] = Field(default_factory=dict)
    currently_reading: list[CurrentlyReading] = Field(default_factory=list)
    recently_added: list[RecentlyAdded] = Field(default_factory=list)
