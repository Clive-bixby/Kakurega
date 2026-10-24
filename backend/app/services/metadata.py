import logging
import re
import threading
import time

import httpx

from app.core.config import get_settings
from app.core.isbn import canonicalize_isbns, normalize_isbn

logger = logging.getLogger(__name__)

OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"
OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

# Open Library regularly takes several seconds to build an edition response, so
# give it more room than Google before treating the request as failed.
OPEN_LIBRARY_TIMEOUT = 10.0
GOOGLE_BOOKS_TIMEOUT = 5.0

CACHE_TTL_SECONDS = 24 * 60 * 60
CACHE_MAX_ENTRIES = 256
# Google resets its daily quota at midnight Pacific time, but we only need to
# stop hammering it while the process is serving requests.
GOOGLE_QUOTA_COOLDOWN_SECONDS = 15 * 60

NOT_FOUND = "not_found"
UNAVAILABLE = "unavailable"
QUOTA_EXCEEDED = "quota_exceeded"

QUOTA_MESSAGE = (
    "Book metadata lookup is unavailable because the Google Books API quota is "
    "exhausted. Enter the book details manually, or configure "
    "KAKUREGA_GOOGLE_BOOKS_API_KEY with a Google Cloud project that has Books "
    "API quota. The ISBN itself is valid."
)
UNAVAILABLE_MESSAGE = (
    "Book metadata providers are unavailable right now. Enter the book details "
    "manually and try the lookup again later."
)


class MetadataLookupError(Exception):
    status_code = 502


class MetadataQuotaExceeded(MetadataLookupError):
    status_code = 503


class InvalidIsbnError(ValueError):
    pass


_cache: dict[str, tuple[float, dict]] = {}
_google_quota_blocked_until = 0.0
_lock = threading.Lock()


def reset_lookup_state() -> None:
    """Clear cached lookups and quota back-off. Used by tests."""
    global _google_quota_blocked_until
    with _lock:
        _cache.clear()
        _google_quota_blocked_until = 0.0


def _cache_get(key: str) -> dict | None:
    now = time.monotonic()
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        stored_at, value = entry
        if now - stored_at > CACHE_TTL_SECONDS:
            _cache.pop(key, None)
            return None
        return dict(value)


def _cache_put(key: str, value: dict) -> None:
    with _lock:
        if len(_cache) >= CACHE_MAX_ENTRIES:
            oldest = min(_cache, key=lambda item: _cache[item][0])
            _cache.pop(oldest, None)
        _cache[key] = (time.monotonic(), dict(value))


def _google_quota_blocked() -> bool:
    with _lock:
        return time.monotonic() < _google_quota_blocked_until


def _block_google_quota() -> None:
    global _google_quota_blocked_until
    with _lock:
        _google_quota_blocked_until = (
            time.monotonic() + GOOGLE_QUOTA_COOLDOWN_SECONDS
        )


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


def _with_isbns(
    result: dict, isbn10: str | None, isbn13: str | None
) -> dict:
    enriched = dict(result)
    enriched["isbn10"] = enriched.get("isbn10") or isbn10
    enriched["isbn13"] = enriched.get("isbn13") or isbn13
    return enriched


def _safe_result(builder, payload: dict) -> dict | None:
    """Map provider payloads defensively so odd records cannot crash a lookup."""
    try:
        return builder(payload)
    except (AttributeError, IndexError, KeyError, TypeError):
        logger.warning("Metadata provider returned an unusable payload")
        return None


def _volume_has_isbn(item: dict, isbn: str) -> bool:
    info = item.get("volumeInfo")
    if not isinstance(info, dict):
        return False
    identifiers = info.get("industryIdentifiers")
    if not isinstance(identifiers, list):
        return False
    for identifier in identifiers:
        if not isinstance(identifier, dict):
            continue
        value = identifier.get("identifier")
        if isinstance(value, str) and value.replace("-", "") == isbn:
            return True
    return False


def _first_google_match(items: list, isbn: str | None) -> dict | None:
    """Google's search is fuzzy, so never accept a volume for a different ISBN."""
    for item in items:
        if not isinstance(item, dict):
            continue
        if isbn and not _volume_has_isbn(item, isbn):
            continue
        result = _safe_result(_google_books_result, item)
        if result:
            return result
    return None


def _open_library_result(data: dict) -> dict | None:
    if not data or not data.get("title"):
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
        "pages": data.get("number_of_pages"),
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
        "pages": doc.get("number_of_pages_median"),
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
        "pages": info.get("pageCount"),
        "source": "google_books",
        "confidence": 0.8,
    }


def _http_failure(response: httpx.Response, provider: str) -> str | None:
    """Classify a non-successful response without leaking request details."""
    if response.status_code < 400:
        return None
    if response.status_code == 404:
        logger.info("%s has no record for this lookup", provider)
        return NOT_FOUND
    if response.status_code == 429:
        logger.warning("%s rate limit reached (HTTP 429)", provider)
        return QUOTA_EXCEEDED
    logger.warning(
        "%s lookup failed with HTTP %s", provider, response.status_code
    )
    return UNAVAILABLE


def _json_body(response: httpx.Response, provider: str) -> dict | None:
    try:
        payload = response.json()
    except ValueError:
        logger.warning("%s returned malformed JSON", provider)
        return None
    if not isinstance(payload, dict):
        logger.warning("%s returned an unexpected payload", provider)
        return None
    return payload


def lookup_open_library(
    isbn: str | None, title: str | None, author: str | None
) -> tuple[dict | None, str | None]:
    try:
        with httpx.Client(timeout=OPEN_LIBRARY_TIMEOUT) as client:
            if isbn:
                response = client.get(
                    OPEN_LIBRARY_URL,
                    params={"bibkeys": f"ISBN:{isbn}", "format": "json", "jscmd": "data"},
                )
                error = _http_failure(response, "Open Library")
                if error:
                    return None, error
                data = _json_body(response, "Open Library")
                if data is None:
                    return None, UNAVAILABLE
                result = _safe_result(
                    _open_library_result, data.get(f"ISBN:{isbn}") or {}
                )
                return (result, None) if result else (None, NOT_FOUND)

            params = {"limit": 1}
            if title:
                params["title"] = title
            if author:
                params["author"] = author
            response = client.get(OPEN_LIBRARY_SEARCH_URL, params=params)
            error = _http_failure(response, "Open Library")
            if error:
                return None, error
            payload = _json_body(response, "Open Library")
            if payload is None:
                return None, UNAVAILABLE
            docs = payload.get("docs") or []
            result = (
                _safe_result(_open_library_search_result, docs[0])
                if docs
                else None
            )
            return (result, None) if result else (None, NOT_FOUND)
    except httpx.TimeoutException:
        logger.warning("Open Library request timed out")
        return None, UNAVAILABLE
    except httpx.HTTPError as exc:
        logger.warning("Open Library request failed: %s", type(exc).__name__)
        return None, UNAVAILABLE
    except ValueError:
        logger.warning("Open Library returned malformed JSON")
        return None, UNAVAILABLE


def _google_error(response: httpx.Response) -> str | None:
    error = _http_failure(response, "Google Books")
    if error != UNAVAILABLE:
        return error

    payload = _json_body(response, "Google Books")
    if payload is None:
        return UNAVAILABLE
    api_error = payload.get("error") or {}
    status = api_error.get("status") or ""
    message = api_error.get("message") or ""
    reasons = {
        item.get("reason")
        for item in api_error.get("errors") or []
        if item.get("reason")
    }
    if status == "RESOURCE_EXHAUSTED" or reasons & {
        "rateLimitExceeded",
        "dailyLimitExceeded",
        "quotaExceeded",
    }:
        logger.warning("Google Books quota exhausted: %s", message)
        return QUOTA_EXCEEDED
    logger.warning("Google Books rejected the lookup: %s", message or status)
    return UNAVAILABLE


def lookup_google_books(
    isbn: str | None, title: str | None, author: str | None
) -> tuple[dict | None, str | None]:
    if _google_quota_blocked():
        logger.debug("Skipping Google Books while quota back-off is active")
        return None, QUOTA_EXCEEDED

    if isbn:
        query = f"isbn:{isbn}"
    else:
        parts = []
        if title:
            parts.append(f"intitle:{title}")
        if author:
            parts.append(f"inauthor:{author}")
        query = " ".join(parts)
    if not query:
        return None, NOT_FOUND

    params = {"q": query, "maxResults": 5 if isbn else 1}
    api_key = get_settings().google_books_api_key.strip()
    if api_key:
        params["key"] = api_key

    try:
        with httpx.Client(timeout=GOOGLE_BOOKS_TIMEOUT) as client:
            response = client.get(GOOGLE_BOOKS_URL, params=params)
            error = _google_error(response)
            if error:
                if error == QUOTA_EXCEEDED:
                    _block_google_quota()
                return None, error
            payload = _json_body(response, "Google Books")
            if payload is None:
                return None, UNAVAILABLE
            items = payload.get("items") or []
            result = _first_google_match(items, isbn)
            return (result, None) if result else (None, NOT_FOUND)
    except httpx.TimeoutException:
        logger.warning("Google Books request timed out")
        return None, UNAVAILABLE
    except httpx.HTTPError as exc:
        logger.warning("Google Books request failed: %s", type(exc).__name__)
        return None, UNAVAILABLE
    except ValueError:
        logger.warning("Google Books returned malformed JSON")
        return None, UNAVAILABLE


def _resolve_isbn(isbn: str) -> tuple[str | None, str | None]:
    normalized = normalize_isbn(isbn)
    if normalized is None:
        raise InvalidIsbnError("ISBN must contain 10 or 13 digits.")
    try:
        return canonicalize_isbns(
            normalized if len(normalized) == 10 else None,
            normalized if len(normalized) == 13 else None,
        )
    except ValueError as exc:
        raise InvalidIsbnError(str(exc)) from exc


def lookup_metadata(isbn: str | None, title: str | None, author: str | None) -> dict | None:
    isbn10 = isbn13 = None
    cache_key = None
    lookup_isbn = None
    if isbn:
        isbn10, isbn13 = _resolve_isbn(isbn)
        lookup_isbn = isbn13 or isbn10
        cache_key = f"isbn:{lookup_isbn}"
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached

    open_result, open_error = lookup_open_library(lookup_isbn, title, author)
    if open_result is not None:
        result = _with_isbns(open_result, isbn10, isbn13)
        if cache_key:
            _cache_put(cache_key, result)
        return result

    google_result, google_error = lookup_google_books(lookup_isbn, title, author)
    if google_result is not None:
        result = _with_isbns(google_result, isbn10, isbn13)
        if cache_key:
            _cache_put(cache_key, result)
        return result

    if QUOTA_EXCEEDED in (open_error, google_error):
        raise MetadataQuotaExceeded(QUOTA_MESSAGE)
    if UNAVAILABLE in (open_error, google_error):
        raise MetadataLookupError(UNAVAILABLE_MESSAGE)
    return None
