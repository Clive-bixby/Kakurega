from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookRead

router = APIRouter()


def get_db(request: Request):
    factory = request.app.state.session_factory
    db = factory()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[BookRead])
def search_books(q: str = Query(default=""), db: Session = Depends(get_db)):
    term = f"%{q}%"
    return (
        db.query(Book)
        .filter(
            or_(
                Book.title.ilike(term),
                Book.isbn10.ilike(term),
                Book.isbn13.ilike(term),
                Book.description.ilike(term),
            )
        )
        .all()
    )
