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

Standard success response:

``` json
{
  "success": true,
  "data": {}
}
```

Standard error response:

``` json
{
  "success": false,
  "message": "Human readable message",
  "code": "ERROR_CODE"
}
```

------------------------------------------------------------------------

# 2. Books

## GET /books

Returns all books.

Response:

```json
[
  {
    "id": 1,
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
    "publisher_id": null,
    "author_ids": [],
    "genre_ids": []
  }
]
```

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

Returns the created book. Invalid `publisher_id`, `author_ids`, or `genre_ids` return 400.

------------------------------------------------------------------------

## PUT /books/{id}

Updates book metadata.

Request body accepts the same fields as create, all optional. Returns 404 when the book does not exist and 400 for invalid relationship IDs.

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

## GET /search

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

## POST /import

Supported:

-   CSV
-   JSON

## GET /export

Supported:

-   CSV
-   JSON

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
-   409 Conflict
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
-   Pagination on list endpoints
-   Validation via Pydantic
-   Business logic only in service layer
-   Versioned endpoints (`/api/v1`)
-   Backend is the single source of truth
