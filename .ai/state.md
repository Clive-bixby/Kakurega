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
- Routing configured with pages for Dashboard, Library, Add Book, Book Details, Search, Insights, and Settings
- API client in `frontend/src/services/api.ts`
- Data fetching hook in `frontend/src/hooks/useBooks.ts`

Backend

- FastAPI application package in `backend/app`
- Versioned API router under `backend/app/api/v1`
- Shared route dependencies (`get_db`) in `backend/app/api/deps.py`
- Core settings, database session factory, and helpers under `backend/app/core`
  (`config`, `database`, `isbn`, `uploads`, `errors`, `storage`)
- SQLAlchemy models and associations under `backend/app/models`
- Book repository under `backend/app/repositories`
- Book, metadata, and barcode services under `backend/app/services`
- Alembic migrations under `backend/alembic/versions`

---

# Reusable Components

Frontend

- App layout with persistent navigation
- Shared page header
- `useBooks` hook

Backend

- `create_app()` in `backend/app/main.py`
- `BookRepository` (filtering, pagination, eager loading, ISBN dedupe)
- `BookService`
- `BookFilters` dataclass for list queries
- `app.core.isbn` — ISBN normalisation, checksum, ISBN-10 ↔ 13 conversion
- `app.core.uploads.read_limited` — chunked upload cap (5 MB)
- `app.core.errors` — `DomainError`, `DuplicateBookError`, `InvalidReferenceError`
- Metadata lookup service
- Barcode decoding service

---

# Shared Services

Backend

- `BookService` handles book CRUD.
- Metadata lookup queries Open Library, then Google Books.
- Barcode decoding uses `zxing-cpp`.

Frontend

- `api.ts` contains typed API client functions.

---

# API Surface

- `GET /api/v1/health`
- `GET /api/v1/books` — paginated, filterable list; also the search endpoint
  (`q`, `genre_id`, `year_from`, `year_to`, `sort`, `limit`, `offset`). Returns
  `{items, total, limit, offset}`; items omit `description` and `notes`.
- `GET /api/v1/books/{id}`
- `POST /api/v1/books` — 409 with `detail.book_id` on duplicate ISBN
- `PUT /api/v1/books/{id}` — `title: null`/blank → 422
- `DELETE /api/v1/books/{id}`
- `GET /api/v1/insights`
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

Relationships

- `books.publisher_id` -> `publishers.id`
- `book_authors` links books and authors
- `book_genres` links books and genres
- `book_tags` links books and tags (cascade delete)

Identity and indexes

- `books.isbn10` / `books.isbn13` are unique when present (partial unique indexes).
- An ISBN-10 is stored with its derived ISBN-13; either form finds the same book.
- `lower(name)` is unique on authors, publishers, genres, and tags.
- `books.title`, `books.published_year`, and `books.publisher_id` are indexed.
- `books.created_at` and `books.notes` were added in `0003`.

Migrations

- `0001_create_books`
- `0002_relationships`
- `0003_identity_and_listing`

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

Frontend implements routing, layout, API client, and wired pages for Dashboard, Library, Add Book, Book Details, and Search.

---

# Feature Status

## Roadmap

Phased plan: `docs/superpowers/plans/2026-10-24-phase-1-closeout.md`.

| Phase | Scope | Status |
|---|---|---|
| 1 | Foundation and correctness | **Complete** |
| 2 | Bulk import | Not started |
| 3 | Catalog workflow | Not started |
| 4 | Reading tracking | Not started |
| 5 | Tags, notes, filters, dashboard | Not started |

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
- [x] Tag schema (tables only; no tag API yet)
- [x] Chunked upload cap (5 MB)
- [x] Upload
- [x] Barcode (ISBN-only)
- [x] Metadata Lookup
- [ ] Bulk import
- [ ] Reading tracking
- [ ] OCR
- [ ] Gemini Vision

## Frontend

- [x] Dashboard
- [x] Library (paginated)
- [x] Book Details
- [x] Search
- [x] Add Book
- [ ] Insights
- [ ] Settings

## Identification Pipeline

- [x] Barcode
- [ ] OCR
- [x] Metadata Lookup
- [ ] Gemini Vision

---

# Development Notes

Backend tests use a temporary SQLite database and `Base.metadata.create_all`.

Frontend build uses TypeScript and Vite.
