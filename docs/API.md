# API.md

# Book Catalog --- API Specification

**Version:** 1.0\
**Status:** Draft

------------------------------------------------------------------------

# 1. API Overview

-   Style: REST
-   Base URL: `/api/v1`
-   Format: JSON
-   Authentication: None (v1)
-   Future: JWT Authentication

Standard success response: the resource object itself (or, for lists, a page
object). There is no `{success, data}` envelope.

Standard error response (FastAPI/Pydantic):

``` json
{
  "detail": "Human readable message or validation details"
}
```

A duplicate ISBN returns `409` with the existing book's id:

``` json
{
  "detail": {
    "message": "Book with this ISBN already exists",
    "book_id": 7
  }
}
```

------------------------------------------------------------------------

# 2. Books

## GET /books

Returns a paginated page of books. This is also the search endpoint.

Query parameters:

| Name | Type | Default | Notes |
|---|---|---|---|
| `q` | string | | Free text over title, subtitle, ISBNs, description, author and publisher names. `%`, `_`, and `\` are literal. A valid ISBN matches either ISBN form, with or without hyphens. |
| `genre_id` | int | | Only books in this genre |
| `year_from` / `year_to` | int | | Inclusive publication-year range |
| `sort` | `title` \| `added` \| `year` | `title` | `added` is newest first, `year` is newest publication first |
| `limit` | int | 50 | 1–200 |
| `offset` | int | 0 | |

Response:

```json
{
  "items": [
    {
      "id": 1,
      "title": "Example",
      "subtitle": null,
      "isbn10": null,
      "isbn13": null,
      "pages": null,
      "language": null,
      "published_year": null,
      "cover_url": null,
      "publisher_id": null,
      "author_ids": [],
      "genre_ids": [],
      "created_at": "2026-10-24T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

List items omit `description` and `notes`; fetch `GET /books/{id}` for those.

------------------------------------------------------------------------

## GET /books/{id}

Returns complete details for a single book.

------------------------------------------------------------------------

## POST /books

Creates a new book.

Request body:

```json
{
  "title": "Example",
  "subtitle": null,
  "isbn10": null,
  "isbn13": null,
  "description": null,
  "pages": null,
  "language": null,
  "published_year": null,
  "cover_url": null,
  "google_books_id": null,
  "openlibrary_id": null,
  "publisher_id": 1,
  "author_ids": [1],
  "genre_ids": [1]
}
```

Returns the created book.

Validation rules:

- `title` is trimmed and must be 1–500 characters.
- `pages` is 1–100,000; `published_year` is 1000 to next year.
- ISBNs are normalised (hyphens/spaces removed, `x` uppercased) and must pass
  checksum validation. An ISBN-10 is converted and stored alongside its derived
  ISBN-13; both forms identify the same book.
- Invalid `publisher_id`, `author_ids`, or `genre_ids` return 400.
- A book with an existing ISBN (either form) returns 409 with
  `detail.book_id`.

------------------------------------------------------------------------

## PUT /books/{id}

Updates book metadata.

Request body accepts the same fields as create, all optional. Omitting a field
leaves it unchanged; setting `title` to `null` or blank returns 422. Returns 404
when the book does not exist, 400 for invalid relationship IDs, and 409 when the
new ISBN belongs to another book.
------------------------------------------------------------------------

## DELETE /books/{id}

Deletes a book from the catalog. Returns 204 on success and 404 when not found.

------------------------------------------------------------------------

# 3. Upload

## POST /upload/image

Uploads a book image (`multipart/form-data`, field `file`). Accepts JPEG, PNG, and WebP up to 5 MB. The file bytes are validated and the extension is derived from the detected image format, not the client filename.

Response:

``` json
{
  "image_id":"...",
  "path":"/storage/images/..."
}
```

The returned `path` is served directly by the API (mount at `/storage`); use it as a book's `cover_url`. Returns 400 for empty, oversized, or non-image files.

------------------------------------------------------------------------

# 4. Identification Pipeline

## POST /identify

Runs:

1.  Barcode detection
2.  OCR
3.  Metadata lookup
4.  AI fallback

Returns metadata with confidence score.

------------------------------------------------------------------------

## POST /barcode

Extracts an ISBN from an uploaded image.

Request: multipart form data with `file`.

Response:

```json
{
  "isbn": "9780140328721"
}
```

Returns 400 for invalid or unsupported images and 404 when no ISBN barcode is found.

------------------------------------------------------------------------

## POST /ocr

Extract visible text from image.

------------------------------------------------------------------------

## POST /lookup

Looks up metadata using Open Library, then Google Books.

Request body:

```json
{
  "isbn": "9780140328721",
  "title": "Example",
  "author": "Author Name"
}
```

All fields are optional.

Response:

```json
{
  "title": "Example",
  "authors": ["Author Name"],
  "publisher": "Publisher",
  "published_year": 2020,
  "isbn10": "0140328726",
  "isbn13": "9780140328721",
  "description": "Description",
  "cover_url": "https://example.com/cover.jpg",
  "source": "open_library",
  "confidence": 0.9
}
```

Returns 404 when no match is found and 502 when both upstreams fail.

------------------------------------------------------------------------

# 5. Search

`GET /search` has been removed. Search is part of `GET /books` (`?q=...`), so
results are paginated and filterable in one request.

Searches books by title, ISBN, and description.

Query parameter:

- `q`

Returns a list of matching books.

------------------------------------------------------------------------

# 6. Tags

## GET /tags

## POST /tags

## PUT /tags/{id}

## DELETE /tags/{id}

------------------------------------------------------------------------

# 7. Authors

## GET /authors

## GET /authors/{id}

------------------------------------------------------------------------

# 8. Publishers

## GET /publishers

------------------------------------------------------------------------

# 9. Genres

## GET /genres

------------------------------------------------------------------------

# 10. Insights

## GET /insights

Returns dashboard statistics:

- `total_books`
- `by_published_year`

------------------------------------------------------------------------

# 11. Import / Export

## POST /import/csv

Multipart upload with field `file` (CSV, header row required, ≤ 10 MB) and
optional query parameter `update_existing` (default `false`).

Recognized headers (case-insensitive; Goodreads names and Kakurega names both
work):

| Field | Headers |
|---|---|
| title | `Title` |
| authors | `Author`, `Authors`, `Author(s)` |
| isbn10 | `ISBN`, `ISBN10` |
| isbn13 | `ISBN13` |
| pages | `Pages`, `Number of Pages`, `Page Count` |
| publisher | `Publisher` |
| published_year | `Published_Year`, `Published Year`, `Year Published`, `Year`, `Publication Year` |
| tags | `Tags`, `Bookshelves` |
| genres | `Genre`, `Genres` |
| notes | `Notes`, `My Review`, `Review` |

Behaviour:

- Import never calls Open Library or Google Books; only the CSV values are used.
- Missing authors, publishers, genres, and tags are created case-insensitively.
- `Bookshelves` becomes tags; the Goodreads default shelves `read`,
  `currently-reading`, and `to-read` are dropped.
- `My Rating`, `Exclusive Shelf`, `Date Read`, and any unknown headers are
  reported in `ignored_columns` (capped at 50) instead of being silently lost.
- Each row is processed independently: one bad row never aborts the file.
- A malformed ISBN imports the book without an ISBN and adds a warning. A row
  without a title is reported in `failed`.
- Duplicate ISBNs (either form) are skipped, or with `update_existing=true`
  fill only blank fields on the existing book without overwriting anything.
  Rows without a usable ISBN fall back to a case-insensitive title + author
  match, so importing the same file twice is idempotent.
- `failed` and `warnings` are capped at 100 entries each.
- Row numbers are 1-based file rows; the header is row 1.

Response:

```json
{
  "created": 493,
  "updated": 0,
  "skipped_duplicates": 5,
  "failed": [{"row": 500, "reason": "Missing title"}],
  "warnings": [{"row": 497, "reason": "Invalid ISBN; imported without ISBN"}],
  "ignored_columns": ["My Rating", "Exclusive Shelf", "Date Read"]
}
```

Returns 400 when the CSV is empty or has no title column, and 413 above 10 MB.

## GET /export

Not implemented yet. Planned for CSV and JSON.

------------------------------------------------------------------------

# 12. Settings

## GET /settings

## PUT /settings

Examples:

-   Theme
-   Metadata source
-   AI provider
-   OCR preferences

------------------------------------------------------------------------

# 13. Status Codes

-   200 OK
-   201 Created
-   204 No Content
-   400 Bad Request
-   404 Not Found
-   409 Conflict (duplicate ISBN)
-   413 Payload Too Large
-   422 Validation Error
-   500 Internal Server Error

------------------------------------------------------------------------

# 14. Future Endpoints

Authentication

    POST /auth/login
    POST /auth/logout
    POST /auth/register

Recommendations

    GET /recommendations/{bookId}

Reading

    POST /reading/session
    GET /reading/history

Users

    GET /users
    GET /users/{id}

------------------------------------------------------------------------

# 15. API Principles

-   RESTful naming
-   Consistent JSON responses
-   Pagination on list endpoints (implemented on `GET /books`)
-   Validation via Pydantic
-   Business logic only in service layer
-   Versioned endpoints (`/api/v1`)
-   Backend is the single source of truth
