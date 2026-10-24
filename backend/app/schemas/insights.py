from pydantic import BaseModel


class InsightsResponse(BaseModel):
    total_books: int
    by_published_year: dict[int, int]
