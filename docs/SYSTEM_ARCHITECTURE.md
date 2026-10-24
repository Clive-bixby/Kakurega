# SYSTEM_ARCHITECTURE.md

# Book Catalog --- System Architecture

**Version:** 1.0\
**Status:** Draft

------------------------------------------------------------------------

## 1. Overview

Book Catalog is a full-stack web application for cataloging and managing
physical book collections with minimal manual effort.

The application identifies books using barcode detection, OCR, public
book metadata APIs, and AI vision as a fallback.

The first release targets a single user but is designed to support
future family accounts without major architectural changes.

------------------------------------------------------------------------

## 2. Goals

-   Modular
-   Maintainable
-   Docker-friendly
-   Cloud-ready
-   Low-cost
-   API-first
-   Scalable
-   Easy to understand

------------------------------------------------------------------------

## 3. High-Level Architecture

``` text
React Frontend
      │
 REST API
      ▼
FastAPI Backend
      │
 ┌────┼───────────────┐
 │    │               │
 ▼    ▼               ▼
PostgreSQL      Local Storage    External Services
 Database        Images                │
                                       ├── Open Library
                                       ├── Google Books
                                       └── Gemini Vision
```

------------------------------------------------------------------------

## 4. Technology Stack

### Frontend

-   React
-   Vite
-   TypeScript
-   Plain CSS (`styles.css`), not Tailwind
-   React Router

### Backend

-   FastAPI
-   SQLAlchemy
-   Alembic
-   Pydantic
-   httpx
-   python-multipart
-   zxing-cpp
-   Pillow

### Database

-   PostgreSQL
-   SQLite for tests

### Containerization

-   Docker
-   Docker Compose

### Image Storage

Initially local filesystem:

``` text
backend/storage/images/
```

Served by the API at `/storage/images/<file>` (`StaticFiles` mount). Docker
Compose keeps it in the `backend_storage` named volume.

Future: - AWS S3 - Google Cloud Storage

------------------------------------------------------------------------

## 5. Backend Architecture

``` text
backend/
└── app/
    ├── api/
    ├── core/
    ├── models/
    ├── repositories/
    ├── schemas/
    ├── services/
    ├── utils/
    ├── workers/
    └── tests/
```

### Responsibilities

-   **api/** → Request/response handling
-   **services/** → Business logic
-   **repositories/** → Database access
-   **models/** → SQLAlchemy models
-   **schemas/** → Pydantic DTOs
-   **workers/** → Background tasks

------------------------------------------------------------------------

## 6. Frontend Architecture

``` text
frontend/
├── assets/
├── components/
├── contexts/
├── hooks/
├── layouts/
├── pages/
├── services/
├── types/
└── utils/
```

Main pages: Dashboard, Library, Tags, Book Details, Reading, Add Book, Import,
Search, Insights, Settings

------------------------------------------------------------------------

## 7. Book Identification Pipeline

``` text
Upload Image
      │
      ▼
Barcode Detection
      │
      ├── Found
      │      ▼
      │ Metadata Lookup
      │      ▼
      │ Save Book
      │
      └── Not Found
             ▼
            OCR
             ▼
      Metadata Lookup
             │
      ├── Found
      │      ▼
      │ Save Book
      │
      └── Not Found
             ▼
        Gemini Vision
             ▼
      Review Metadata
             ▼
          Save Book
```

------------------------------------------------------------------------

## 7.1 Catalog Workflow (Add and Edit)

Adding a book is a client-driven flow; the server only supplies data and
enforces identity.

``` text
Add Book page
      │  ISBN typed ──────────────┐
      │  Barcode photo ──► /barcode┤
      ▼                           ▼
 /lookup (Open Library → Google Books)
      │
      ├── found ──► prefilled editable form
      └── not found ──► empty form + notice
                              │
                              ▼
                 /books/isbn/{isbn} check
                     │            │
                  existing      404
                     │            ▼
        "Already in library"    POST /books
                                   │
                        409 duplicate (detail.book_id)
                                   ▼
                        "Open the existing book"
```

- `BookForm` is shared by Add Book and Book Details. Fields: title, subtitle,
  both ISBNs, pages, year, language, cover (URL or upload), publisher, authors,
  genres, tags, description, notes.
- `TaxonomyPicker` debounces `GET /authors|publishers|genres|tags?q=`, filters
  already-selected items, and offers `Add "<name>"`. New names are only sent to
  `POST` when the form is saved, so cancelling never pollutes the catalog.
- Lookup authors and publisher arrive as names; they resolve to ids through the
  create-or-get endpoints on save.
- ISBN entries are still canonicalised and validated server-side; the UI's
  pre-check is an optimisation, not the source of truth.
- `GET /books/{id}` returns resolved `authors`, `genres`, `tags`, and
  `publisher` objects so Book Details can render and prefill without extra
  requests for each name.

------------------------------------------------------------------------

## 8. Import Pipeline

`POST /import/csv` accepts a CSV upload, parses it with `app/core/csv_import.py`
(pure header/row parsing), then persists it through `ImportService`. Each row
runs in its own savepoint so a bad row cannot abort the file. The importer only
uses values in the CSV — it never calls Open Library or Google Books — and
creates missing authors, publishers, genres, and tags by name. Duplicates are
matched by ISBN (or by title + author when no ISBN is usable); with
`update_existing=true` only blank fields are filled.

------------------------------------------------------------------------

## 8.1 Reading Tracking

Members are household names, not accounts. `GET/POST /members` and
`PATCH/DELETE /members/{id}` manage them; names are unique case-insensitively.

`ReadingEntry` is the single row that describes one member's state for one
book (`unique(book_id, member_id)`). `ReadingService` owns the rules:

``` text
Reading page ──► GET /reading?member_id&status
Book page    ──► GET /books/{id}/reading
                 PUT /books/{id}/reading/{member_id}  (upsert)
                 DELETE /books/{id}/reading/{member_id}
Library      ──► GET /books?member_id&status  (IN subquery, one row per book)
Dashboard    ──► GET /insights → currently_reading
```

- `status=reading` defaults `started_on` to today and clears a stale
  `finished_on`; `status=finished` defaults `finished_on` to today and sets
  `current_page` to the book's page count when omitted.
- `current_page` is validated against `books.pages`; `finished_on` may not
  precede `started_on`.
- Progress is derived in the UI from `current_page / pages`; the API never
  stores a percentage.
- Entries cascade when a book or member is deleted, and the ORM relationship
  uses `delete-orphan` so this also holds on SQLite without FK pragmas.

---

## 8.2 Tags, Filters, and Insights

Tags are household-wide labels. `GET /tags` returns each tag with a derived
`book_count`; `PATCH /tags/{id}` renames one everywhere and `DELETE /tags/{id}`
removes its `book_tags` rows without deleting books.

The Library filter bar composes one `GET /books` request from text (debounced),
genre, tag name, publication-year range, member, reading status, and sort. The
tag filter joins `book_tags` and matches the tag name case-insensitively, so the
list-item shape stays lean; the UI resolves `tag_ids` to names from the tag list
it already loads.

`GET /insights` powers both the Dashboard and the Insights page with grouped SQL
(no full-table scans in Python):

``` text
Dashboard ──► totals, currently_reading, recently_added
Insights  ──► by_published_year, by_genre (top 10),
              by_author (top 10), by_language
```

Tags and notes are edited through the existing `BookForm` (household note) and
`ReadingPanel` (per-member note); no separate note storage exists.

---

## 9. External Services

### Open Library

Primary metadata source.

### Google Books

Secondary metadata source.

### Gemini Vision

Fallback when metadata cannot be identified.

### Barcode Decoding

Uses zxing-cpp with Pillow for local image decoding.

------------------------------------------------------------------------

## 10. Search

Current: - Case-insensitive `ILIKE` matching in `GET /books?q=...`

Fields: - Title - Subtitle - ISBN - Description - Author - Publisher

`Genres` and `Notes` are not searched yet; genre and tag are filters
(`?genre_id=`, `?tag=`). `%`, `_`, and `\` are treated literally. Paginated 50
rows at a time by default.

Future: - Vector embeddings - Semantic search

------------------------------------------------------------------------

## 11. Recommendations

### Version 1

-   Same author
-   Same genre
-   Same series

### Future

-   Embedding-based similarity
-   Hybrid recommendation engine

------------------------------------------------------------------------

## 12. Analytics

Generated entirely from local database data.

Examples: - Books read - Reading trends - Favorite genres - Publication
timeline - Books added

------------------------------------------------------------------------

## 13. Deployment

Development:

``` text
Docker Compose

Frontend
Backend
PostgreSQL
```

Future:

``` text
React
  │
Cloud CDN
  │
FastAPI Container
  │
PostgreSQL
  │
Object Storage
```

------------------------------------------------------------------------

## 14. Security

Current: - No authentication

Future: - JWT authentication - Private image storage - Environment
variables for secrets

------------------------------------------------------------------------

## 15. Design Principles

-   Backend is the single source of truth.
-   Frontend never calls external metadata APIs directly.
-   Business logic belongs in services.
-   Database access belongs in repositories.
-   Keep AI usage minimal by using barcode and OCR first.
-   Build for extensibility without unnecessary complexity.

------------------------------------------------------------------------

## 16. Future Evolution

-   Family accounts
-   Mobile application
-   Redis cache
-   Background workers
-   AI recommendations
-   Vector search
-   Cloud deployment
-   Book lending
-   Notifications
