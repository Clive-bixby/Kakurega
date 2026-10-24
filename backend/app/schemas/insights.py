from pydantic import BaseModel, Field


class CurrentlyReading(BaseModel):
    book_id: int
    book_title: str
    member_id: int
    member_name: str
    current_page: int | None
    pages: int | None


class InsightsResponse(BaseModel):
    total_books: int
    by_published_year: dict[int, int]
    currently_reading: list[CurrentlyReading] = Field(default_factory=list)
