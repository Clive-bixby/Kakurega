from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.book import Book
from app.models.reading import ReadingEntry
from app.schemas.insights import CurrentlyReading, InsightsResponse

router = APIRouter()


@router.get("", response_model=InsightsResponse)
def insights(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    years = Counter(b.published_year for b in books if b.published_year is not None)

    entries = (
        db.query(ReadingEntry)
        .options(
            joinedload(ReadingEntry.member), joinedload(ReadingEntry.book)
        )
        .filter(ReadingEntry.status == "reading")
        .all()
    )
    entries.sort(key=lambda entry: (entry.member.name.lower(), entry.book.title.lower()))

    return InsightsResponse(
        total_books=len(books),
        by_published_year=dict(years),
        currently_reading=[
            CurrentlyReading(
                book_id=entry.book_id,
                book_title=entry.book.title,
                member_id=entry.member_id,
                member_name=entry.member.name,
                current_page=entry.current_page,
                pages=entry.book.pages,
            )
            for entry in entries
        ],
    )
