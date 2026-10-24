from sqlalchemy.orm import Session

from app.core.csv_import import ParsedRow, parse_csv
from app.models.book import Book
from app.repositories.book import BookRepository
from app.repositories.catalog import CatalogRepository
from app.schemas.book import BookCreate
from app.schemas.importing import ImportProblem, ImportResult

MAX_PROBLEMS = 100


class ImportRowError(Exception):
    pass


def _append(target: list[ImportProblem], row: int, reason: str) -> None:
    if len(target) < MAX_PROBLEMS:
        target.append(ImportProblem(row=row, reason=reason))


class ImportService:
    def __init__(self, db: Session):
        self.db = db
        self.books = BookRepository(db)
        self.catalog = CatalogRepository(db)

    def import_csv(self, data: bytes, update_existing: bool = False) -> ImportResult:
        parsed = parse_csv(data)

        created = 0
        updated = 0
        skipped = 0
        failed: list[ImportProblem] = []
        warnings: list[ImportProblem] = []

        for row in parsed.rows:
            outcome = "failed"
            try:
                with self.db.begin_nested():
                    outcome = self._import_row(row, update_existing)
            except ImportRowError as exc:
                _append(failed, row.row_number, str(exc))
                continue
            except Exception as exc:
                _append(failed, row.row_number, str(exc) or "Invalid row")
                continue

            if outcome == "created":
                created += 1
            elif outcome == "updated":
                updated += 1
            elif outcome == "skipped":
                skipped += 1

            for warning in row.warnings:
                _append(warnings, row.row_number, warning)

        self.db.commit()
        return ImportResult(
            created=created,
            updated=updated,
            skipped_duplicates=skipped,
            failed=failed,
            warnings=warnings,
            ignored_columns=parsed.ignored_columns,
        )

    def _import_row(self, row: ParsedRow, update_existing: bool) -> str:
        if not row.title:
            raise ImportRowError("Missing title")

        existing = self.books.find_by_isbn(row.isbn10, row.isbn13)
        if existing is None and row.isbn10 is None and row.isbn13 is None:
            existing = self.books.find_by_title_and_authors(row.title, row.authors)
        if existing is not None:
            if not update_existing:
                return "skipped"
            self._fill_blanks(existing, row)
            return "updated"

        authors = [
            self.catalog.author(name) for name in row.authors if name.strip()
        ]
        genres = [
            self.catalog.genre(name) for name in row.genres if name.strip()
        ]
        tags = [self.catalog.tag(name) for name in row.tags if name.strip()]
        publisher = (
            self.catalog.publisher(row.publisher) if row.publisher else None
        )

        data = BookCreate(
            title=row.title,
            isbn10=row.isbn10,
            isbn13=row.isbn13,
            pages=row.pages,
            published_year=row.published_year,
            notes=row.notes,
            publisher_id=publisher.id if publisher else None,
            author_ids=[author.id for author in authors],
            genre_ids=[genre.id for genre in genres],
        )
        book = self.books.create(data, commit=False)
        book.tags = tags
        self.db.flush()
        return "created"

    def _fill_blanks(self, book: Book, row: ParsedRow) -> None:
        authors = (
            [self.catalog.author(name) for name in row.authors if name.strip()]
            if row.authors and not book.authors
            else None
        )
        genres = (
            [self.catalog.genre(name) for name in row.genres if name.strip()]
            if row.genres and not book.genres
            else None
        )
        tags = (
            [self.catalog.tag(name) for name in row.tags if name.strip()]
            if row.tags and not book.tags
            else None
        )

        values: dict[str, object] = {
            "isbn10": row.isbn10,
            "isbn13": row.isbn13,
            "pages": row.pages,
            "published_year": row.published_year,
            "notes": row.notes,
        }
        if row.publisher and book.publisher_id is None:
            values["publisher_id"] = self.catalog.publisher(row.publisher).id

        self.books.fill_blanks(
            book, values, authors=authors, genres=genres, tags=tags
        )
