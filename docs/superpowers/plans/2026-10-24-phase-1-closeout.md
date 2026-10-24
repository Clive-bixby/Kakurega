# Phase 1 Closeout — Implementation Plan

> **For agentic workers:** Work **one phase at a time**. Do not start a phase
> until the previous phase's gate is green and its row in the status table says
> `Complete`. Detailed task plans for Phases 2–5 are written when their phase
> starts; the design spec is the contract for all of them.

**Goal:** Turn the scaffold into a household library you can populate in bulk and
read against: correct identity, validation, fast paginated lists, reliable
barcode capture, and a UI that still works.

**Architecture:** Keep route → service → repository layering. Add ISBN
canonicalisation as a pure module, database constraints as Alembic migrations,
and a single paginated `/books` endpoint that absorbs `/search`. Frontend adapts
to the paginated envelope.

**Tech Stack:** FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL (SQLite in tests),
React + TypeScript + Vite.

**Spec:** `docs/superpowers/specs/2026-10-24-phase-1-closeout-design.md`

## Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Foundation and correctness | **Complete** |
| 2 | Bulk import | Not started |
| 3 | Catalog workflow | Not started |
| 4 | Reading tracking | Not started |
| 5 | Tags, notes, filters, dashboard | Not started |

**Gate (run at the end of every phase, tick before moving on):**

- [x] `cd backend && python -m pytest -q` — all green (53 passed)
- [x] `cd frontend && npm run build` — green (`tsc -b` clean)
- [x] Migrations: `alembic upgrade head` → `downgrade -1` → `upgrade head` — **SQLite** cycle green; PostgreSQL DDL generated offline (`--sql`) and validated. Real Postgres run pending Docker availability.
- [x] Docs updated for behaviour/API changes
- [x] This status table and `.ai/state.md` updated; phase committed

## Global Constraints

- No auth this phase; app is trusted-LAN only.
- API responses are bare objects; no `{success, data}` envelope.
- ISBN-13 is identity; ISBN-10 is derived/stored alongside.
- Tests use SQLite; migrations must run on PostgreSQL.
- No new frontend UI library; no new backend framework.
- No feature may leave `main` unable to boot, migrate, or pass tests.

## Review Focus

- An ISBN typed with hyphens must find the same book as one typed without.
- A second create with the same ISBN-10/13 pair must never create a row.
- A 1,000-book list must not issue one query per book.
- A 13-digit grocery barcode must not be accepted as a book ISBN.
- An oversized upload must be rejected before it is fully buffered.

---

## Phase 1 — Foundation and correctness

### Task 1: ISBN normalisation and validation

**Files:**
- Create: `backend/app/core/isbn.py`
- Test: `backend/tests/test_isbn.py`

**Interfaces:**
- `normalize_isbn(value: str) -> str | None`
- `is_valid_isbn10(value: str) -> bool`
- `is_valid_isbn13(value: str) -> bool`
- `isbn10_to_isbn13(value: str) -> str`
- `isbn13_to_isbn10(value: str) -> str | None`
- `canonicalize_isbns(isbn10: str | None, isbn13: str | None) -> tuple[str | None, str | None]` — raises `ValueError` on a malformed or mismatched pair

- [ ] Write tests: `0-14-032872-6` normalises and converts to `9780140328721`; checksum-invalid values rejected; `978` vs `979` conversion behaviour; mismatched pair raises.
- [ ] Run tests, confirm they fail.
- [ ] Implement the module.
- [ ] Run tests, confirm they pass.
- [ ] Commit `feat(backend): add ISBN normalisation helpers`.

### Task 2: Schema constraints and new tables

**Files:**
- Create: `backend/alembic/versions/0003_identity_and_listing.py`
- Modify: `backend/app/models/book.py`, `backend/app/models/associations.py`, `backend/app/models/__init__.py`
- Create: `backend/app/models/tag.py`

**Interfaces:**
- `books.created_at` (timezone-aware, server default now), `books.notes`
- `tags(id, name)`, `book_tags(book_id, tag_id)`
- Partial unique indexes `uq_books_isbn10` / `uq_books_isbn13`
- Unique `lower(name)` indexes on authors, publishers, genres, tags
- Indexes: `books.title`, `books.published_year`, `books.publisher_id`

- [ ] Add model fields, `Tag`, and table args with indexes (SQLite + PostgreSQL partial-index syntax).
- [ ] Write the migration with batch alter for `books`, full `downgrade()`.
- [ ] Verify model↔migration parity by generating DDL for PostgreSQL offline.
- [ ] Commit `feat(backend): add identity constraints and tag schema`.

### Task 3: Book validation

**Files:**
- Modify: `backend/app/schemas/book.py`
- Test: `backend/tests/test_book_validation.py`

**Interfaces:** `BookCreate`, `BookUpdate`, `BookRead`, `BookListItem`, `BookPage`

- [ ] Tests: blank/whitespace title → 422; `pages` 0 and 100001 → 422; `published_year` 999 and future+2 → 422; `PUT {"title": null}` → 422; ISBN normalised in response; list item has no `description`; page envelope has `items/total/limit/offset`.
- [ ] Implement validators (`field_validator`, `model_validator` for ISBN pair) and the two read schemas.
- [ ] Commit `feat(backend): validate book payloads`.

### Task 4: Repository — filtering, pagination, eager loading, dedupe

**Files:**
- Modify: `backend/app/repositories/book.py`, `backend/app/services/book.py`
- Create: `backend/app/core/errors.py` (or `app/services/errors.py`)
- Test: `backend/tests/test_books.py`

**Interfaces:**
- `BookRepository.list(filters: BookFilters, limit: int, offset: int) -> tuple[list[Book], int]`
- `DuplicateBookError(book_id: int)`, `InvalidReferenceError`
- `BookService.list_books(filters, limit, offset)`

- [ ] Tests: pagination totals; sort by title/added/year; `q` matches author and publisher; `%` and `_` are literal; duplicate ISBN (either form) → `DuplicateBookError` with existing id; constant query count for a 20-book list (`selectinload`).
- [ ] Implement filters dataclass, joins + `distinct`, `selectinload`, escapes, dedupe query, `IntegrityError` → domain errors.
- [ ] Commit `feat(backend): paginate and filter book lists`.

### Task 5: Routes — one list endpoint, 409/422 semantics

**Files:**
- Modify: `backend/app/api/v1/routes/books.py`, `backend/app/api/v1/router.py`
- Delete: `backend/app/api/v1/routes/search.py`
- Modify: `backend/app/api/shared deps` — extract `get_db` into `backend/app/api/deps.py` while touching the routes
- Test: `backend/tests/test_books.py`, delete `backend/tests/test_search.py` cases into `/books`

- [ ] Tests: `GET /books` envelope + filters; `GET /search` → 404; duplicate create → 409 with `book_id`; null title → 422.
- [ ] Implement query parameters (`q`, `genre_id`, `year_from`, `year_to`, `sort`, `limit`, `offset`; `status`/`member_id`/`tag` accepted and ignored-with-400 until later phases? **No** — omit them until the owning phase), response model.
- [ ] Commit `feat(backend): consolidate search into paginated book list`.

### Task 6: Barcode ISBN validation

**Files:**
- Modify: `backend/app/services/barcode.py`
- Test: `backend/tests/test_barcode.py`

- [ ] Tests: EAN-13 grocery code rejected; 978/979 with valid checksum accepted; invalid checksum rejected; ISBN-10 accepted.
- [ ] Implement prefix + checksum filtering using `app.core.isbn`.
- [ ] Commit `fix(backend): accept only real ISBN barcodes`.

### Task 7: Upload limits and config

**Files:**
- Create: `backend/app/core/uploads.py`
- Modify: `backend/app/api/v1/routes/upload.py`, `backend/app/api/v1/routes/barcode.py`, `backend/app/core/config.py`
- Test: `backend/tests/test_upload.py`

- [ ] Tests: oversized body returns 413 without reading past the cap; valid image still 200; debug default is `False`.
- [ ] Implement `async read_limited(file, limit=5MB)` reading 64 KB chunks.
- [ ] Commit `fix(backend): cap uploads before buffering`.

### Task 8: Frontend adapts to the paginated API

**Files:**
- Modify: `frontend/src/services/api.ts`, `frontend/src/hooks/useBooks.ts`, `frontend/src/pages/LibraryPage.tsx`, `frontend/src/pages/SearchPage.tsx`
- Test: `npm run build` + manual smoke

- [ ] Update types (`BookPage`), `fetchBooks(page, q)` and `searchBooks` to the new shape.
- [ ] Library page: page controls + total count; Search page: debounced query against `/books?q=`.
- [ ] Commit `feat(frontend): page and search against the books endpoint`.

### Task 9: Documentation

**Files:**
- Modify: `docs/API.md`, `docs/DATABASE.md`, `docs/SYSTEM_ARCHITECTURE.md`, `backend/README.md`

- [ ] Document the envelope, filters, removed `/search`, 409/422, ISBN canonicalisation, barcode rules, new tables.
- [ ] Commit `docs: describe phase 1 API and schema`.

### Task 10: Phase gate

- [x] `python -m pytest -q` (53 passed)
- [x] `npm run build`
- [x] Migration cycle (upgrade → downgrade → upgrade); SQLite cycle green, PostgreSQL DDL validated offline
- [x] Update status table above to `Complete` and `.ai/state.md`
- [x] Commit `chore: close phase 1`

**Exit criteria:** with 1,000 seeded books, `GET /books?limit=50` issues a
constant number of queries; duplicate ISBN create returns 409; `PUT {"title":
null}` returns 422; a non-book EAN returns 404 from `/barcode`; suite and build
green.

---

## Phase 2 — Bulk import (plan written when phase starts)

Source: spec §8.6 and §11 Phase 2.

## Phase 3 — Catalog workflow (plan written when phase starts)

Source: spec §8.7 and §11 Phase 3.

## Phase 4 — Reading tracking (plan written when phase starts)

Source: spec §8.4 and §11 Phase 4.

## Phase 5 — Tags, notes, filters, dashboard (plan written when phase starts)

Source: spec §8.5, §8.9 and §11 Phase 5.
