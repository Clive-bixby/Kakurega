import re

import httpx

OPEN_LIBRARY_TIMEOUT = 5.0
GOOGLE_BOOKS_TIMEOUT = 5.0


class MetadataLookupError(Exception):
    pass


def _year_from_text(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d{4}", value)
    return int(match.group(0)) if match else None


def _normalize_isbns(values: list[str] | None) -> tuple[str | None, str | None]:
    isbn10 = None
    isbn13 = None
    for value in values or []:
        cleaned = value.replace("-", "").replace(" ", "")
        if len(cleaned) == 10 and isbn10 is None:
            isbn10 = cleaned
        elif len(cleaned) == 13 and isbn13 is None:
            isbn13 = cleaned
    return isbn10, isbn13


def _open_library_result(data: dict) -> dict | None:
    if not data:
        return None
    authors = [author.get("name") for author in data.get("authors", []) if author.get("name")]
    publishers = data.get("publishers", [])
    publisher = publishers[0].get("name") if publishers and publishers[0].get("name") else None
    isbn10, isbn13 = _normalize_isbns(data.get("isbn_10", []) + data.get("isbn_13", []))
    cover = data.get("cover", {})
    return {
        "title": data.get("title"),
        "authors": authors,
        "publisher": publisher,
        "published_year": _year_from_text(data.get("publish_date")),
        "isbn10": isbn10,
        "isbn13": isbn13,
        "description": data.get("excerpts", [{}])[0].get("text") if data.get("excerpts") else None,
        "cover_url": cover.get("large") or cover.get("medium") or cover.get("small"),
        "source": "open_library",
        "confidence": 0.9,
    }


def _open_library_search_result(doc: dict) -> dict | None:
    if not doc.get("title"):
        return None
    isbn10, isbn13 = _normalize_isbns(doc.get("isbn", []))
    cover_id = doc.get("cover_i")
    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None
    return {
        "title": doc.get("title"),
        "authors": doc.get("author_name", []),
        "publisher": (doc.get("publisher") or [None])[0],
        "published_year": doc.get("first_publish_year"),
        "isbn10": isbn10,
        "isbn13": isbn13,
        "description": None,
        "cover_url": cover_url,
        "source": "open_library",
        "confidence": 0.75,
    }


def _google_books_result(item: dict) -> dict | None:
    info = item.get("volumeInfo", {})
    if not info.get("title"):
        return None
    identifiers = info.get("industryIdentifiers", [])
    isbn_values = [identifier.get("identifier") for identifier in identifiers if identifier.get("identifier")]
    isbn10, isbn13 = _normalize_isbns(isbn_values)
    image_links = info.get("imageLinks", {})
    return {
        "title": info.get("title"),
        "authors": info.get("authors", []),
        "publisher": info.get("publisher"),
        "published_year": _year_from_text(info.get("publishedDate")),
        "isbn10": isbn10,
        "isbn13": isbn13,
        "description": info.get("description"),
        "cover_url": image_links.get("thumbnail") or image_links.get("smallThumbnail"),
        "source": "google_books",
        "confidence": 0.8,
    }


def lookup_open_library(isbn: str | None, title: str | None, author: str | None) -> tuple[dict | None, bool]:
    try:
        with httpx.Client(timeout=OPEN_LIBRARY_TIMEOUT) as client:
            if isbn:
                response = client.get(
                    "https://openlibrary.org/api/books",
                    params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
                )
                response.raise_for_status()
                data = response.json()
                book_data = data.get(f"ISBN:{isbn}")
                if book_data:
                    return _open_library_result(book_data), False
                return None, False

            params = {"limit": 1}
            if title:
                params["title"] = title
            if author:
                params["author"] = author
            response = client.get("https://openlibrary.org/search.json", params=params)
            response.raise_for_status()
            docs = response.json().get("docs", [])
            if docs:
                return _open_library_search_result(docs[0]), False
            return None, False
    except httpx.HTTPError:
        return None, True


def lookup_google_books(isbn: str | None, title: str | None, author: str | None) -> tuple[dict | None, bool]:
    try:
        with httpx.Client(timeout=GOOGLE_BOOKS_TIMEOUT) as client:
            if isbn:
                query = f"isbn:{isbn}"
            else:
                parts = []
                if title:
                    parts.append(f"intitle:{title}")
                if author:
                    parts.append(f"inauthor:{author}")
                query = " ".join(parts) if parts else ""
            if not query:
                return None, False
            response = client.get(
                "https://www.googleapis.com/books/v1/volumes",
                params={"q": query, "maxResults": 1},
            )
            response.raise_for_status()
            items = response.json().get("items", [])
            if items:
                return _google_books_result(items[0]), False
            return None, False
    except httpx.HTTPError:
        return None, True


def lookup_metadata(isbn: str | None, title: str | None, author: str | None) -> dict | None:
    open_result, open_failed = lookup_open_library(isbn, title, author)
    if open_result is not None:
        return open_result

    google_result, google_failed = lookup_google_books(isbn, title, author)
    if google_result is not None:
        return google_result

    if open_failed or google_failed:
        raise MetadataLookupError
    return None
