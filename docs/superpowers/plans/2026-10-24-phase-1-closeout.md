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
| 2 | Bulk import | **Complete** |
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

## Phase 2 — Bulk import

**Goal:** a Goodreads CSV export (or the app's own column names) can be
imported in one upload, with per-row outcomes, duplicate handling, and no
external API calls. The library shows the imported books paginated.

**Design:**

- Parsing is pure and lives in `backend/app/core/csv_import.py`: decode bytes,
  normalize headers, return `ParsedRow` objects plus the list of ignored
  columns. No database, no network.
- Persistence lives in `backend/app/services/importer.py`, using
  `CatalogRepository` (case-insensitive get-or-create for authors, publishers,
  genres, tags) and non-committing `BookRepository` calls. Each CSV row runs in
  its own savepoint; the whole file commits once at the end.
- Header aliases (case/space-insensitive, BOM stripped):

  | Field | Headers |
  |---|---|
  | title | `title` |
  | authors | `author`, `authors`, `author(s)` |
  | isbn10 | `isbn`, `isbn10` |
  | isbn13 | `isbn13` |
  | pages | `pages`, `number of pages`, `page count` |
  | publisher | `publisher` |
  | published_year | `published_year`, `published year`, `year published`, `year`, `publication year` |
  | tags | `tags`, `bookshelves` |
  | genres | `genre`, `genres` |
  | notes | `notes`, `my review`, `review` |

- Goodreads `ISBN` cells wrapped as `="0140328726"` are unwrapped. Goodreads
  default shelves `read`, `currently-reading`, `to-read` are dropped from tags.
- Tags and genres split on comma/semicolon, trimmed, deduped case-insensitively.
  Authors split on `;` only (Goodreads writes `Last, First`).
- Unknown headers and the deliberately ignored `My Rating`, `Exclusive Shelf`,
  `Date Read` go into `ignored_columns` (capped at 50) so nothing is dropped
  silently.
- Row numbers are 1-based file rows (header is row 1). Blank lines are skipped
  without an outcome.
- Invalid/mismatched ISBN: import the row without an ISBN, add a warning. If one
  half of a mismatched pair is valid, use that half and warn.
- Empty title → `failed`. The field is capped at 500 chars with a warning.
- Invalid pages/year (non-numeric, out of 1–100,000 / 1000–next-year) become
  `null` with a warning.
- Duplicate ISBN (either form):
  - `update_existing=false` → `skipped_duplicates += 1`.
  - `update_existing=true` → fill only blank fields/relationships on the
    existing book, never overwrite, count in `updated`.
- Rows with no usable ISBN fall back to a case-insensitive title + author match,
  so re-importing a file containing malformed ISBNs stays idempotent.
- `failed`/`warnings` capped at 100 entries each.
- Upload limit 10 MB, read with `read_limited`; 413 when exceeded.

**API:** `POST /import/csv?update_existing=false`, multipart field `file`.
Response schema `ImportResult`:

```json
{
  "created": 0, "updated": 0, "skipped_duplicates": 0,
  "failed": [{"row": 2, "reason": "Missing title"}],
  "warnings": [{"row": 3, "reason": "Invalid ISBN; imported without ISBN"}],
  "ignored_columns": ["My Rating", "Exclusive Shelf", "Date Read"]
}
```

### Task 1: Tag relationship and non-committing repository writes

**Files:** `backend/app/models/book.py`, `backend/app/repositories/book.py`,
`backend/app/repositories/catalog.py` (new)

- Add `Book.tags` (`secondary=book_tags`, cascade-safe read/write).
- `BookRepository.create(data, commit=True)` and
  `BookRepository.update(book, data, commit=True)` so import can batch commits.
- `BookRepository.fill_blanks(book, values)` fills only `None`/empty fields and
  only empty relationship collections. Returns whether anything changed.
- `CatalogRepository.get_or_create_author/publisher/genre/tag(name)` with an
  in-request lowercase cache; flushes but never commits.

### Task 2: Pure CSV parsing

**Files:** `backend/app/core/csv_import.py` (new),
`backend/tests/test_import_parser.py` (new)

- `parse_csv(data: bytes) -> ParsedCsv` with `rows`, `ignored_columns`.
- `ParsedRow` dataclass: `row_number`, `title`, `authors`, `isbn10`, `isbn13`,
  `pages`, `publisher`, `published_year`, `tags`, `genres`, `notes`, `warnings`.
- Decode `utf-8-sig`, then `utf-8`, then `cp1252`.
- Tests: aliases, BOM, `="..."` ISBN unwrap, semicolon/comma splitting, default
  shelf drop, dedupe, ignored columns, row numbering, bad pages/year warnings,
  missing title header → `ValueError`, blank line skipped.

### Task 3: Import service and schemas

**Files:** `backend/app/services/importer.py` (new),
`backend/app/schemas/importing.py` (new),
`backend/tests/test_import.py` (new)

- `ImportService(db).import_csv(data: bytes, update_existing: bool) -> ImportResult`.
- Per row: `db.begin_nested()`; resolve ISBNs via `canonicalize_isbns`; look up
  duplicates; create or fill blanks; count; catch any exception as `failed`
  without aborting the file; commit once at the end.
- Tests: creates books/relationships/notes/tags; default shelves absent; re-import
  creates zero rows; `update_existing` fills blanks without overwriting;
  bad ISBN imports with warning; missing title fails one row only; ignored
  columns reported.

### Task 4: Route

**Files:** `backend/app/api/v1/routes/importing.py` (new),
`backend/app/api/v1/router.py`

- `POST /import/csv`, `UploadFile = File(...)`, `update_existing: bool = False`.
- 400 for a file without a title column, 413 past 10 MB, 400 for unreadable CSV.
- Tests in `test_import.py` for 413, missing title header, and response shape.

### Task 5: 500-row fixture test (phase exit)

**Files:** `backend/tests/test_import.py`

- Generate 500 Goodreads-style rows: 490 valid unique ISBN-13s, 5 repeats of
  earlier ISBNs, 3 invalid checksums, 2 missing titles.
- Expected: `created == 493`, `skipped_duplicates == 5`, `failed == 2`,
  `warnings == 3`; `GET /books?limit=50` reports `total == 493` and returns 50
  items in a constant number of queries.
- Re-import with `update_existing=false` → `created == 0`,
  `skipped_duplicates == 498` (495 ISBN matches + 3 no-ISBN title matches);
  `total` stays 493.

### Task 6: Import UI

**Files:** `frontend/src/pages/ImportPage.tsx` (new),
`frontend/src/services/api.ts`, `frontend/src/App.tsx`,
`frontend/src/layouts/AppLayout.tsx`

- File input (`accept=".csv,text/csv"`), `update_existing` checkbox, submit, and
  a result panel with created/updated/skipped counts plus failed/warnings lists.
- Link to `/library` after a successful import.
- Nav entry "Import" with the `Upload` icon.

### Task 7: Documentation and gate

**Files:** `docs/API.md`, `docs/SYSTEM_ARCHITECTURE.md`,
`docs/superpowers/plans/2026-10-24-phase-1-closeout.md`, `.ai/state.md`

- Document the endpoint, headers, counts, warnings, and ignored columns.
- Tick the phase gate and mark the status row `Complete`.
- No migration is added in this phase.

**Exit criteria:** the 500-row fixture yields exactly `created 493,
skipped_duplicates 5, failed 2, warnings 3`; re-import creates nothing; a
malformed ISBN survives as a warning; imported books appear paginated in the
library; suite and build green.

**Gate:**

- [x] `cd backend && python -m pytest -q` — 77 passed
- [x] `cd frontend && npm run build` — green
- [x] No new migration in this phase
- [x] Docs updated (`API.md`, `SYSTEM_ARCHITECTURE.md`)
- [x] Status table and `.ai/state.md` updated; phase committed

---

## Phase 3 — Catalog workflow (plan written when phase starts)

Source: spec §8.7 and §11 Phase 3.

## Phase 4 — Reading tracking (plan written when phase starts)

Source: spec §8.4 and §11 Phase 4.

## Phase 5 — Tags, notes, filters, dashboard (plan written when phase starts)

Source: spec §8.5, §8.9 and §11 Phase 5.
