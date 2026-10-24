from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.book import Book
from app.schemas.insights import InsightsResponse

router = APIRouter()


@router.get("", response_model=InsightsResponse)
def insights(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    years = Counter(b.published_year for b in books if b.published_year is not None)
    return InsightsResponse(total_books=len(books), by_published_year=dict(years))
