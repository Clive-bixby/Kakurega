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

Returns paginated list of books.

### Query Parameters

-   page
-   limit
-   search
-   sort
-   order

### Filters

-   author
-   genre
-   publisher
-   language
-   read_status
-   favorite
-   tag
-   year

------------------------------------------------------------------------

## GET /books/{id}

Returns complete details for a single book.

------------------------------------------------------------------------

## POST /books

Creates a new book.

Request body:

``` json
{
  "title": "",
  "isbn13": "",
  "author_ids": [],
  "publisher_id": 1
}
```

------------------------------------------------------------------------

## PUT /books/{id}

Updates book metadata.

------------------------------------------------------------------------

## DELETE /books/{id}

Deletes a book from the catalog.

------------------------------------------------------------------------

# 3. Upload

## POST /upload/image

Uploads a book image.

Response:

``` json
{
  "image_id":"...",
  "path":"storage/images/..."
}
```

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

Extract ISBN from uploaded image.

------------------------------------------------------------------------

## POST /ocr

Extract visible text from image.

------------------------------------------------------------------------

## POST /lookup

Lookup metadata using:

-   Open Library
-   Google Books

------------------------------------------------------------------------

# 5. Search

## GET /search

Global search across:

-   Title
-   Author
-   ISBN
-   Publisher
-   Genre
-   Tags
-   Notes

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

-   Total books
-   Books read
-   Unread books
-   Favorites
-   Genre distribution
-   Reading trends
-   Publication timeline
-   Books added

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
