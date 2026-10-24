# Kakurega — Project State

## Purpose

This document provides a concise snapshot of the current implementation of Kakurega.

It exists so AI coding agents can quickly understand what has already been built without scanning the entire repository.

Unlike the documentation in `/docs`, this file reflects the **current implementation**, not the planned design.

Keep this document concise and up to date.

---

# Update Policy

Update this document whenever the implementation changes in a meaningful way.

Examples:

- New module
- New service
- New API
- New reusable component
- New database entity
- New infrastructure
- Major refactor

Do not update this file for:

- Bug fixes
- Small refactors
- Formatting changes
- Documentation changes
- Temporary experiments

Replace outdated information instead of appending duplicates.

---

# Technology Stack

Frontend

React + Vite + TypeScript scaffold implemented.

Backend

FastAPI scaffold implemented.

Database

PostgreSQL in Docker Compose; SQLite for tests.

Infrastructure

Docker Compose for PostgreSQL, backend, and frontend. Local image storage under `backend/storage/images`.

---

# Current Modules

Frontend

- React frontend in `frontend`
- Routing configured with pages for Dashboard, Library, Tags, Add Book, Book
  Details, Reading, Search, Import, Insights, and Settings
- API client in `frontend/src/services/api.ts`
- Data fetching hook in `frontend/src/hooks/useBooks.ts`
- Reusable `BookForm` (add/edit) and `TaxonomyPicker` (chips + debounced
  server search + create)
- Shared `StatusBadge`, `ProgressBar`, `EmptyState`, `BarList`, and `BookCover`;
  `ReadingPanel` on Book Details
- Literary Noir theme in `frontend/src/styles.css`: 260px sidebar, sticky topbar
  search (`Ctrl/Cmd+K`), layered surface cards, pill chips, thin progress bars,
  cover grid; content column capped at 1240px. Tokens follow
  `design/stitch/theme/DESIGN.md`.
- Brand assets in `frontend/public`: `icon.svg` (detailed install icon),
  `favicon.svg` (bold small-size mark used in the tab and sidebar), `logo.svg`
  lockup, PNG derivatives (`icon-192/512`, `apple-touch-icon`, `favicon-32/48`),
  and `site.webmanifest`. `BookCover` reuses `favicon.svg` for cover fallbacks.

Backend

- FastAPI application package in `backend/app`
- Versioned API router under `backend/app/api/v1`
- Shared route dependencies (`get_db`) in `backend/app/api/deps.py`
- Core settings, database session factory, and helpers under `backend/app/core`
  (`config`, `database`, `isbn`, `csv_import`, `uploads`, `errors`, `storage`)
- SQLAlchemy models and associations under `backend/app/models`
- Book, catalog, taxonomy, and reading repositories under
  `backend/app/repositories`
- Book, metadata, barcode, import, and reading services under
  `backend/app/services`
- Alembic migrations under `backend/alembic/versions`

---

# Reusable Components

Frontend

- App layout with persistent sidebar, topbar search, and mobile header
- Shared page header (`eyebrow`, `title`, `description`, actions)
- `useBooks` hook
- `BookForm` — all book fields, taxonomy pickers, cover upload, duplicate link
- `TaxonomyPicker` — removable chips, debounced search, create-on-enter
- `StatusBadge` / `ProgressBar` — reading status and derived page progress
- `BookCover` — cover image with a generated typographic fallback
- `EmptyState` — consistent empty/error-free placeholders
- `BarList` — accessible horizontal breakdown bars for insights
- `ReadingPanel` — per-book reading entries and upsert form

Backend

- `create_app()` in `backend/app/main.py`
- `BookRepository` (filtering, pagination, eager loading, ISBN dedupe)
- `BookService`
- `BookFilters` dataclass for list queries
- `app.core.isbn` — ISBN normalisation, checksum, ISBN-10 ↔ 13 conversion
- `app.core.uploads.read_limited` — chunked upload cap (5 MB)
- `app.core.errors` — `DomainError`, `DuplicateBookError`, `InvalidReferenceError`
- `app.core.csv_import.parse_csv` — pure Goodreads/Kakurega CSV parsing
- `ImportService` — per-row savepoints, duplicate handling, relationships
- `CatalogRepository` — case-insensitive create-or-get for authors, publishers, genres, tags
- `TaxonomyRepository` — taxonomy list/search and committed create-or-get
- `ReadingRepository` / `ReadingService` — member CRUD, entry upsert,
  progress/date validation, per-book and household reading lists
- Metadata lookup service
- Barcode decoding service

---

# Shared Services

Backend

- `BookService` handles book CRUD.
- `ReadingService` handles household members and reading entries.
- Metadata lookup queries Open Library, then Google Books.
- Barcode decoding uses `zxing-cpp`.

Frontend

- `api.ts` contains typed API client functions.

---

# API Surface

- `GET /api/v1/health`
- `GET /api/v1/books` — paginated, filterable list; also the search endpoint
  (`q`, `genre_id`, `tag`, `year_from`, `year_to`, `member_id`, `status`,
  `sort`, `limit`, `offset`). Returns `{items, total, limit, offset}`; items
  omit `description`, `notes`, and resolved taxonomy objects, but include
  `author_names` for card bylines.
- `GET /api/v1/books/{id}` — full book plus resolved `authors`, `genres`,
  `tags`, and `publisher`
- `GET /api/v1/books/isbn/{isbn}` — existing book by either ISBN form, 404 when
  absent; used to intercept duplicates before creating
- `POST /api/v1/books` — 409 with `detail.book_id` on duplicate ISBN
- `PUT /api/v1/books/{id}` — `title: null`/blank → 422
- `DELETE /api/v1/books/{id}`
- `GET/POST /api/v1/authors`, `/publishers`, `/genres`, `/tags` — taxonomy list
  (`q`, `limit`) and case-insensitive create-or-get. `/tags` includes derived
  `book_count`.
- `PATCH/DELETE /api/v1/tags/{id}` — rename (duplicate → 409) and delete
  (removes it from books, keeps the books)
- `GET/POST /api/v1/members`, `PATCH/DELETE /api/v1/members/{id}` — household
  members; duplicate name → 409, blank → 422
- `GET /api/v1/books/{id}/reading` — entries for one book
- `PUT/DELETE /api/v1/books/{id}/reading/{member_id}` — upsert/remove a member's
  entry; page > `pages` → 422, finished before started → 422
- `GET /api/v1/reading?member_id&status` — household entries, newest first
- `POST /api/v1/import/csv` — Goodreads/Kakurega CSV, 10 MB cap, per-row results
- `GET /api/v1/insights` — totals, by year/genre/author/language,
  `currently_reading`, and five most recently added books; currently-reading and
  recently-added items carry `cover_url` and `author_name`
- `POST /api/v1/upload/image` — 413 past 5 MB
- `POST /api/v1/lookup`
- `POST /api/v1/barcode` — only valid ISBN-10 / 978-979 ISBN-13 accepted

`GET /api/v1/search` was removed; use `GET /api/v1/books?q=...`.

---

# Database

Tables

- `authors`
- `books`
- `publishers`
- `genres`
- `book_authors`
- `book_genres`
- `tags`
- `book_tags`
- `members`
- `reading_entries`

Relationships

- `books.publisher_id` -> `publishers.id`
- `book_authors` links books and authors
- `book_genres` links books and genres
- `book_tags` links books and tags (cascade delete)
- `reading_entries.book_id` -> `books.id` and `reading_entries.member_id` ->
  `members.id`, both cascading; one row per book/member pair

Identity and indexes

- `books.isbn10` / `books.isbn13` are unique when present (partial unique indexes).
- An ISBN-10 is stored with its derived ISBN-13; either form finds the same book.
- `lower(name)` is unique on authors, publishers, genres, and tags.
- `books.title`, `books.published_year`, and `books.publisher_id` are indexed.
- `books.created_at` and `books.notes` were added in `0003`.
- `members.name` is unique case-insensitively (`lower(name)`); reading entries
  index `member_id` and `status` and check the status values.
- Tags are household-wide; tag `book_count` is derived from `book_tags`, never
  stored.

Migrations

- `0001_create_books`
- `0002_relationships`
- `0003_identity_and_listing`
- `0004_members_and_reading`

---

# External Integrations

- Open Library for metadata lookup
- Google Books for metadata fallback
- `zxing-cpp` for barcode decoding
- Local filesystem for uploaded images

---

# Project Structure

Current top-level modules

frontend/

backend/

docs/

.ai/

---

# Current Architecture

Backend follows the planned FastAPI architecture and implements models, repositories, services, schemas, migrations, and tests.

Frontend implements routing, a Literary Noir app shell (sidebar, topbar search, mobile header), API client, and wired pages for Dashboard, Library, Tags, Add Book, Book Details, Reading, Import, Insights, Search, and Settings. Add Book performs ISBN/barcode lookup and duplicate interception; Book Details displays and edits every catalog field and hosts per-member reading tracking; Library composes search, genre, tag, year, member, status, and sort filters; Tags supports rename/delete with book counts; Dashboard and Insights render currently-reading, recently-added, and collection breakdowns.

---

# Feature Status

## Roadmap

Phased plan: `docs/superpowers/plans/2026-10-24-phase-1-closeout.md`.

| Phase | Scope | Status |
|---|---|---|
| 1 | Foundation and correctness | **Complete** |
| 2 | Bulk import | **Complete** |
| 3 | Catalog workflow | **Complete** |
| 4 | Reading tracking | **Complete** |
| 5 | Tags, notes, filters, dashboard | **Complete** |

## Foundation

- [x] Repository setup
- [x] Backend scaffold
- [x] Frontend scaffold
- [x] Docker

## Backend

- [x] Book CRUD
- [x] Author, Publisher, and Genre relationships
- [x] Search (as `GET /books?q=`)
- [x] Paginated / filtered / sorted book list
- [x] ISBN identity and payload validation
- [x] Tag schema and CRUD-through-books (`tag_ids`); taxonomy list/create API
- [x] Tag rename/delete with derived `book_count`
- [x] Book tag filtering and extended insights breakdowns
- [x] Book lookup by ISBN for duplicate interception
- [x] Chunked upload cap (5 MB)
- [x] Upload
- [x] Barcode (ISBN-only)
- [x] Metadata Lookup
- [x] CSV / Goodreads bulk import
- [x] Reading tracking (members, status, progress, dates, notes)
- [ ] OCR
- [ ] Gemini Vision

## Frontend

- [x] Dashboard
- [x] Library (paginated; search, genre, tag, year, member, status, sort)
- [x] Tags (counts, rename, delete)
- [x] Book Details (full display and edit, reading panel)
- [x] Reading (members, activity, filters)
- [x] Search
- [x] Add Book (ISBN lookup, barcode capture, manual entry, duplicate link)
- [x] Catalog workflow (taxonomy pickers, ISBN by-line identity)
- [x] Import (CSV results panel)
- [x] Insights (year, genre, author, language breakdowns)
- [x] Settings (theme summary, shortcuts to tags/reading/import, data notes)

## Identification Pipeline

- [x] Barcode
- [ ] OCR
- [x] Metadata Lookup
- [ ] Gemini Vision

---

# Development Notes

Backend tests use a temporary SQLite database and `Base.metadata.create_all`.

Frontend build uses TypeScript and Vite.

Visual source of truth: `design/stitch/theme/DESIGN.md` plus the screen PNGs in `design/stitch/`. Class names and tokens live in the single stylesheet `frontend/src/styles.css`; pages compose those classes rather than inline styles.
