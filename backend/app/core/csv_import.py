import csv
import io
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.isbn import canonicalize_isbns

DEFAULT_SHELVES = {"read", "currently-reading", "to-read"}

HEADER_ALIASES = {
    "title": "title",
    "author": "authors",
    "authors": "authors",
    "author(s)": "authors",
    "isbn": "isbn10",
    "isbn10": "isbn10",
    "isbn13": "isbn13",
    "pages": "pages",
    "number of pages": "pages",
    "page count": "pages",
    "publisher": "publisher",
    "published_year": "published_year",
    "published year": "published_year",
    "year published": "published_year",
    "year": "published_year",
    "publication year": "published_year",
    "tags": "tags",
    "bookshelves": "tags",
    "genre": "genres",
    "genres": "genres",
    "notes": "notes",
    "my review": "notes",
    "review": "notes",
}

MAX_IGNORED_COLUMNS = 50
MAX_TITLE_LENGTH = 500


@dataclass
class ParsedRow:
    row_number: int
    title: str = ""
    authors: list[str] = field(default_factory=list)
    isbn10: str | None = None
    isbn13: str | None = None
    pages: int | None = None
    publisher: str | None = None
    published_year: int | None = None
    tags: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    notes: str | None = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class ParsedCsv:
    rows: list[ParsedRow]
    ignored_columns: list[str]


def _decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


def _normalize_header(value: str) -> str:
    return " ".join(value.strip().lstrip("\ufeff").lower().split())


def _clean_isbn_cell(value: str) -> str | None:
    cleaned = value.strip()
    if len(cleaned) >= 3 and cleaned.startswith('="') and cleaned.endswith('"'):
        cleaned = cleaned[2:-1]
    cleaned = cleaned.strip()
    if cleaned in {"", "0", "-"}:
        return None
    return cleaned


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.casefold()
        if key and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _parse_int(
    value: str, minimum: int, maximum: int, label: str, warnings: list[str]
) -> int | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    try:
        number = int(cleaned)
    except ValueError:
        warnings.append(f"Invalid {label}; ignored")
        return None
    if number < minimum or number > maximum:
        warnings.append(f"Invalid {label}; ignored")
        return None
    return number


def _resolve_isbns(
    raw10: str | None, raw13: str | None, warnings: list[str]
) -> tuple[str | None, str | None]:
    if not raw10 and not raw13:
        return None, None

    try:
        return canonicalize_isbns(raw10, raw13)
    except ValueError:
        pass

    if raw10:
        try:
            resolved = canonicalize_isbns(raw10, None)
            warnings.append("ISBN pair invalid; used ISBN-10")
            return resolved
        except ValueError:
            pass

    if raw13:
        try:
            resolved = canonicalize_isbns(None, raw13)
            warnings.append("ISBN pair invalid; used ISBN-13")
            return resolved
        except ValueError:
            pass

    warnings.append("Invalid ISBN; imported without ISBN")
    return None, None


def _first(values: list[str]) -> str:
    for value in values:
        if value.strip():
            return value.strip()
    return ""


def parse_csv(data: bytes) -> ParsedCsv:
    text = _decode(data)
    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        header_row = next(reader)
    except StopIteration as exc:
        raise ValueError("CSV file is empty") from exc

    headers = [_normalize_header(value) for value in header_row]
    field_indexes: dict[str, list[int]] = {}
    ignored_columns: list[str] = []

    for index, header in enumerate(headers):
        mapped = HEADER_ALIASES.get(header)
        if mapped is None:
            if header and len(ignored_columns) < MAX_IGNORED_COLUMNS:
                ignored_columns.append(header_row[index].strip())
            continue
        field_indexes.setdefault(mapped, []).append(index)

    if "title" not in field_indexes:
        raise ValueError("CSV must include a Title column")

    next_year = datetime.now(timezone.utc).year + 1
    rows: list[ParsedRow] = []

    for row_number, cells in enumerate(reader, start=2):
        if all(not cell.strip() for cell in cells):
            continue

        def values(name: str) -> list[str]:
            return [
                cells[index] if index < len(cells) else ""
                for index in field_indexes.get(name, [])
            ]

        warnings: list[str] = []
        title = _first(values("title"))
        if len(title) > MAX_TITLE_LENGTH:
            title = title[:MAX_TITLE_LENGTH]
            warnings.append("Title truncated to 500 characters")

        authors = _dedupe(
            [
                part.strip()
                for value in values("authors")
                for part in value.split(";")
                if part.strip()
            ]
        )
        tags = _dedupe(
            [
                name
                for value in values("tags")
                for name in _split(value)
                if name.casefold() not in DEFAULT_SHELVES
            ]
        )
        genres = _dedupe(
            [name for value in values("genres") for name in _split(value)]
        )
        isbn10, isbn13 = _resolve_isbns(
            _clean_isbn_cell(_first(values("isbn10"))),
            _clean_isbn_cell(_first(values("isbn13"))),
            warnings,
        )

        rows.append(
            ParsedRow(
                row_number=row_number,
                title=title,
                authors=authors,
                isbn10=isbn10,
                isbn13=isbn13,
                pages=_parse_int(
                    _first(values("pages")), 1, 100_000, "pages", warnings
                ),
                publisher=_first(values("publisher")) or None,
                published_year=_parse_int(
                    _first(values("published_year")),
                    1000,
                    next_year,
                    "published year",
                    warnings,
                ),
                tags=tags,
                genres=genres,
                notes=_first(values("notes")) or None,
                warnings=warnings,
            )
        )

    return ParsedCsv(rows=rows, ignored_columns=ignored_columns)
