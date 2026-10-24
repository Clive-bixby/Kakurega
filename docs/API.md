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
| `member_id` | int | | Only books this household member has any reading entry for |
| `status` | `want_to_read` \| `reading` \| `finished` \| `abandoned` | | Only books with a reading entry in this status (any member unless `member_id` is also set) |
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
      "tag_ids": [],
      "created_at": "2026-10-24T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

List items omit `description`, `notes`, and the resolved `authors`, `genres`,
`tags`, and `publisher` objects; fetch `GET /books/{id}` for those.

------------------------------------------------------------------------

## GET /books/{id}

Returns complete details for a single book, including resolved names:

```json
{
  "id": 1,
  "title": "Example",
  "authors": [{"id": 1, "name": "Author Name"}],
  "genres": [{"id": 1, "name": "Fantasy"}],
  "tags": [{"id": 1, "name": "sci-fi"}],
  "publisher": {"id": 1, "name": "Publisher", "country": null},
  "author_ids": [1],
  "genre_ids": [1],
  "tag_ids": [1],
  "publisher_id": 1
}
```

------------------------------------------------------------------------

## GET /books/isbn/{isbn}

Looks up an existing book by either ISBN form, with or without hyphens or
spaces. Returns the full book object, or 404 when the ISBN is invalid or not in
the library. The Add Book screen uses this to offer the existing book instead of
creating a duplicate.

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
  "notes": null,
  "pages": null,
  "language": null,
  "published_year": null,
  "cover_url": null,
  "google_books_id": null,
  "openlibrary_id": null,
  "publisher_id": 1,
  "author_ids": [1],
  "genre_ids": [1],
  "tag_ids": [1]
}
```

Returns the created book.

Validation rules:

- `title` is trimmed and must be 1–500 characters.
- `pages` is 1–100,000; `published_year` is 1000 to next year.
- ISBNs are normalised (hyphens/spaces removed, `x` uppercased) and must pass
  checksum validation. An ISBN-10 is converted and stored alongside its derived
  ISBN-13; both forms identify the same book.
- Invalid `publisher_id`, `author_ids`, `genre_ids`, or `tag_ids` return 400.
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
  "pages": 320,
  "source": "open_library",
  "confidence": 0.9
}
```

Returns 404 when no match is found and 502 when both upstreams fail.

------------------------------------------------------------------------

# 5. Search

`GET /search` has been removed. Search is part of `GET /books` (`?q=...`), so
results are paginated and filterable in one request.

------------------------------------------------------------------------

# 6. Taxonomy

Authors, publishers, genres, and tags share one create-or-get API surface.
Names are trimmed and unique case-insensitively: posting an existing name in a
different case returns the existing row instead of creating a duplicate.

## GET /authors, GET /publishers, GET /genres, GET /tags

Query parameters:

| Name | Type | Default | Notes |
|---|---|---|---|
| `q` | string | | Case-insensitive substring match on name; `%`, `_`, and `\` are literal |
| `limit` | int | 50 | 1–500 |

Results are ordered by name (case-insensitive). Response:

```json
[
  {"id": 1, "name": "Ursula K. Le Guin"}
]
```

Publisher items also include `country`:

```json
[{"id": 1, "name": "Ace", "country": "US"}]
```

## POST /authors, POST /publishers, POST /genres, POST /tags

Request body:

```json
{"name": "Ursula K. Le Guin"}
```

Publishers additionally accept an optional `country`. Names are required, are
trimmed, and cannot be blank (422). Returns the existing or newly created
entity with 200.

Tag management (rename/delete) is planned for the dashboard phase; the list and
create endpoints above already support the book editor.

------------------------------------------------------------------------

# 7. Insights

## GET /insights

Returns dashboard statistics:

- `total_books`
- `by_published_year`
- `currently_reading` — one item per entry whose status is `reading`:

```json
{
  "total_books": 42,
  "by_published_year": {"2020": 4},
  "currently_reading": [
    {
      "book_id": 7,
      "book_title": "Example",
      "member_id": 2,
      "member_name": "Maya",
      "current_page": 120,
      "pages": 320
    }
  ]
}
```

`current_page` and `pages` are `null` when unknown. Items are ordered by member
name, then book title.

---

# 7.1 Household members and reading

There is no authentication. A member is just a name in this household.

## GET /members

Returns all members ordered by name (case-insensitive):

```json
[{"id": 2, "name": "Maya", "created_at": "2026-10-24T10:00:00Z"}]
```

## POST /members

Request body: `{"name": "Maya"}`. Names are trimmed, 1–100 characters, and
unique case-insensitively (422 when blank, 409 when the name already exists).
Returns 201 with the member. A duplicate name returns 409 with a plain string
`detail`.

## PATCH /members/{id}

Renames a member. Same validation and 409 rules; 404 when the member does not
exist.

## DELETE /members/{id}

Deletes a member and all of their reading entries (cascade). Returns 204, or 404
when not found.

## GET /books/{id}/reading

Returns every member's reading entry for one book, ordered by member name. 404
when the book does not exist. Each entry:

```json
{
  "id": 11,
  "book_id": 7,
  "member_id": 2,
  "member_name": "Maya",
  "book_title": "Example",
  "book_pages": 320,
  "status": "reading",
  "current_page": 120,
  "started_on": "2026-10-20",
  "finished_on": null,
  "note": "Chapter 8 is great",
  "updated_at": "2026-10-24T18:30:00Z"
}
```

## PUT /books/{id}/reading/{member_id}

Creates or replaces one member's entry for a book (at most one entry per
book/member pair). Request body:

```json
{
  "status": "reading",
  "current_page": 120,
  "started_on": "2026-10-20",
  "finished_on": null,
  "note": "Chapter 8 is great"
}
```

Behaviour:

- `status` is required and is one of `want_to_read`, `reading`, `finished`,
  `abandoned`.
- Omitted optional fields are left unchanged on an existing entry; explicit
  `null` clears them.
- `status=reading` clears `finished_on` (unless explicitly provided) and
  defaults `started_on` to today when absent.
- `status=finished` defaults `finished_on` to today and, when the book has a
  page count and `current_page` is omitted, sets `current_page` to that count.
- `current_page` must be ≥ 0 and cannot exceed the book's `pages` when known
  (422). `finished_on` before `started_on` is 422.
- Progress is derived from `current_page / pages`; no percentage is stored.
- Returns 404 when the book or member does not exist.

## DELETE /books/{id}/reading/{member_id}

Removes one entry. Returns 204, or 404 when there is no such entry.

## GET /reading

Returns every entry in the household, most recently updated first, optionally
filtered by `member_id` and/or `status`. Items use the same shape as
`GET /books/{id}/reading`. An invalid `status` is 422.

------------------------------------------------------------------------

# 8. Import / Export

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

# 9. Settings

## GET /settings

## PUT /settings

Examples:

-   Theme
-   Metadata source
-   AI provider
-   OCR preferences

------------------------------------------------------------------------

# 10. Status Codes

-   200 OK
-   201 Created
-   204 No Content
-   400 Bad Request
-   404 Not Found
-   409 Conflict (duplicate ISBN or member name)
-   413 Payload Too Large
-   422 Validation Error
-   500 Internal Server Error

------------------------------------------------------------------------

# 11. Future Endpoints

Authentication

    POST /auth/login
    POST /auth/logout
    POST /auth/register

Recommendations

    GET /recommendations/{bookId}

Reading

    Reading tracking is implemented for household members: `GET/POST /members`,
    `PATCH/DELETE /members/{id}`, `GET /reading`, and
    `GET/PUT/DELETE /books/{id}/reading[/{member_id}]`.

    Future: `POST /reading/session`, `GET /reading/history` for page-level
    sessions.

Users

    GET /users
    GET /users/{id}

------------------------------------------------------------------------

# 12. API Principles

-   RESTful naming
-   Consistent JSON responses
-   Pagination on list endpoints (implemented on `GET /books`)
-   Validation via Pydantic
-   Business logic only in service layer
-   Versioned endpoints (`/api/v1`)
-   Backend is the single source of truth
