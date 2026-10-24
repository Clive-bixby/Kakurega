from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.schemas.book import BookCreate, BookRead, BookUpdate

router = APIRouter()


def get_db(request: Request):
    factory = request.app.state.session_factory
    db = factory()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[BookRead])
def list_books(db: Session = Depends(get_db)):
    from app.services.book import BookService

    return BookService(db).list_books()


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    from app.services.book import BookService

    book = BookService(db).get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=BookRead, status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    from app.services.book import BookService

    try:
        return BookService(db).create_book(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    from app.services.book import BookService

    try:
        book = BookService(db).update_book(book_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    from app.services.book import BookService

    if not BookService(db).delete_book(book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return None
