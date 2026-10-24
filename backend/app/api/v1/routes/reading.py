from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import InvalidReadingError
from app.schemas.reading import ReadingEntryRead, ReadingEntryUpsert, ReadingStatus
from app.services.reading import ReadingService

router = APIRouter()


@router.get("/books/{book_id}/reading", response_model=list[ReadingEntryRead])
def book_reading(book_id: int, db: Session = Depends(get_db)):
    entries = ReadingService(db).list_book_entries(book_id)
    if entries is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return entries


@router.put(
    "/books/{book_id}/reading/{member_id}", response_model=ReadingEntryRead
)
def upsert_reading(
    book_id: int,
    member_id: int,
    data: ReadingEntryUpsert,
    db: Session = Depends(get_db),
):
    try:
        entry = ReadingService(db).upsert_entry(book_id, member_id, data)
    except InvalidReadingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if entry is None:
        raise HTTPException(status_code=404, detail="Book or member not found")
    return entry


@router.delete("/books/{book_id}/reading/{member_id}", status_code=204)
def delete_reading(book_id: int, member_id: int, db: Session = Depends(get_db)):
    if not ReadingService(db).delete_entry(book_id, member_id):
        raise HTTPException(status_code=404, detail="Reading entry not found")
    return None


@router.get("/reading", response_model=list[ReadingEntryRead])
def list_reading(
    member_id: int | None = None,
    status: ReadingStatus | None = None,
    db: Session = Depends(get_db),
):
    return ReadingService(db).list_entries(member_id, status)
