from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import DuplicateBookError, InvalidReferenceError
from app.core.isbn import canonicalize_isbns, normalize_isbn
from app.repositories.book import BookFilters
from app.schemas.book import BookCreate, BookPage, BookRead, BookUpdate
from app.schemas.reading import ReadingStatus
from app.services.book import BookService

router = APIRouter()


@router.get("", response_model=BookPage)
def list_books(
    q: str = Query(default=""),
    genre_id: int | None = None,
    year_from: int | None = Query(default=None, ge=1000),
    year_to: int | None = Query(default=None, ge=1000),
    member_id: int | None = None,
    status: ReadingStatus | None = None,
    sort: Literal["title", "added", "year"] = "title",
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    filters = BookFilters(
        q=q.strip() or None,
        genre_id=genre_id,
        year_from=year_from,
        year_to=year_to,
        member_id=member_id,
        status=status,
    )
    items, total = BookService(db).list_books(filters, limit, offset, sort)
    return BookPage(items=items, total=total, limit=limit, offset=offset)


@router.get("/isbn/{isbn}", response_model=BookRead)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    book = BookService(db).get_book_by_isbn(isbn)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = BookService(db).get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=BookRead, status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    try:
        return BookService(db).create_book(data)
    except DuplicateBookError as exc:
        raise HTTPException(
            status_code=409,
            detail={"message": "Book with this ISBN already exists", "book_id": exc.book_id},
        ) from exc
    except InvalidReferenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    try:
        book = BookService(db).update_book(book_id, data)
    except DuplicateBookError as exc:
        raise HTTPException(
            status_code=409,
            detail={"message": "Book with this ISBN already exists", "book_id": exc.book_id},
        ) from exc
    except InvalidReferenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    if not BookService(db).delete_book(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return None
