from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.associations import book_authors, book_genres
from app.models.author import Author
from app.models.book import Book
from app.models.genre import Genre
from app.models.member import Member
from app.models.reading import ReadingEntry
from app.schemas.insights import (
    CurrentlyReading,
    InsightsResponse,
    NamedCount,
    RecentlyAdded,
)

router = APIRouter()

RECENT_LIMIT = 5
TOP_LIMIT = 10


def _top_by(db: Session, model, association, id_column) -> list[NamedCount]:
    count = func.count(association.c.book_id)
    statement = (
        select(model.id, model.name, count.label("count"))
        .join(association, id_column == model.id)
        .group_by(model.id, model.name)
        .order_by(count.desc(), func.lower(model.name))
        .limit(TOP_LIMIT)
    )
    return [
        NamedCount(id=row.id, name=row.name, count=row.count)
        for row in db.execute(statement).all()
    ]


@router.get("", response_model=InsightsResponse)
def insights(db: Session = Depends(get_db)):
    total_books = db.execute(select(func.count(Book.id))).scalar_one()
    total_members = db.execute(select(func.count(Member.id))).scalar_one()

    year_rows = db.execute(
        select(Book.published_year, func.count(Book.id))
        .where(Book.published_year.is_not(None))
        .group_by(Book.published_year)
        .order_by(Book.published_year)
    ).all()
    by_published_year = {year: count for year, count in year_rows}

    language_rows = db.execute(
        select(Book.language, func.count(Book.id))
        .where(Book.language.is_not(None), Book.language != "")
        .group_by(Book.language)
        .order_by(func.count(Book.id).desc(), func.lower(Book.language))
    ).all()
    by_language = {language: count for language, count in language_rows}

    entries = (
        db.execute(
            select(ReadingEntry)
            .join(ReadingEntry.member)
            .join(ReadingEntry.book)
            .where(ReadingEntry.status == "reading")
            .options(
                joinedload(ReadingEntry.member), joinedload(ReadingEntry.book)
            )
            .order_by(func.lower(Member.name), func.lower(Book.title))
        )
        .scalars()
        .unique()
        .all()
    )

    recent = (
        db.execute(
            select(Book)
            .order_by(Book.created_at.desc(), Book.id.desc())
            .limit(RECENT_LIMIT)
        )
        .scalars()
        .all()
    )

    return InsightsResponse(
        total_books=total_books,
        total_members=total_members,
        by_published_year=by_published_year,
        by_genre=_top_by(
            db, Genre, book_genres, book_genres.c.genre_id
        ),
        by_author=_top_by(
            db, Author, book_authors, book_authors.c.author_id
        ),
        by_language=by_language,
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
        recently_added=[
            RecentlyAdded(
                book_id=book.id,
                title=book.title,
                cover_url=book.cover_url,
                created_at=book.created_at,
            )
            for book in recent
        ],
    )
