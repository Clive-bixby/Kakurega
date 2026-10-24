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
| 3 | Catalog workflow | **Complete** |
| 4 | Reading tracking | **Complete** |
| 5 | Tags, notes, filters, dashboard | **Complete** |

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

## Phase 3 — Catalog workflow

**Goal:** a book can be added by typing an ISBN, photographing a barcode, or
entering it by hand; lookup prefills the form; authors, publishers, genres, and
tags are chosen from searchable pickers backed by idempotent create-or-get
endpoints; duplicates are intercepted before a second row exists; Book Details
edits everything.

**Design:**

- Add `tag_ids` to book create/update/read schemas, repository handling, and
  validation (invalid tag → 400). `BookRead` and `BookListItem` expose
  `tag_ids` alongside `author_ids`/`genre_ids`.
- Add `GET /books/isbn/{isbn}` returning an existing book or 404. It accepts
  either ISBN form with hyphens/spaces, so the Add Book UI can offer the
  existing book after lookup. `POST /books` already returns 409 with
  `detail.book_id`; the UI uses both.
- Add taxonomy endpoints, all idempotent create-or-get keyed on
  case-insensitive name:
  - `GET /authors?q=&limit=` / `POST /authors {name}`
  - `GET /publishers?q=&limit=` / `POST /publishers {name, country?}`
  - `GET /genres?q=&limit=` / `POST /genres {name}`
  - `GET /tags?q=&limit=` / `POST /tags {name}`
  Return `{id, name}` (publisher also `country`). Tag management/filtering UI
  remains Phase 5; the endpoint exists now because Book Details edits tags.
- Frontend gets one reusable `BookForm` and a `TaxonomyPicker`:
  - pickers debounce a server search, show matches, allow multi-select with
    removable chips, and offer "Add <name>" when there is no exact match;
  - prefill from lookup keeps authors as name-only selections and resolves them
    with create-or-get only on save, so cancelling does not pollute the catalog.
- Add Book: ISBN input + Lookup, barcode file input with `capture="environment"`
  calling `/barcode` then `/lookup`, prefilled editable form, and a prominent
  "Already in library — open it" link when `/books/isbn/{isbn}` or a 409 finds
  a match.
- Book Details: display all fields, then edit title/subtitle/ISBNs/pages/
  language/year/publisher/authors/genres/tags/description/notes/cover; upload
  or replace the cover; delete stays.
- No migration.

### Task 1: Tags on books (schemas, repository, routes)

**Files:** `backend/app/schemas/book.py`, `backend/app/repositories/book.py`,
`backend/app/api/v1/routes/books.py`, `backend/tests/test_books.py`

- `tag_ids` on `BookCreate`/`BookUpdate` (default empty/None), `BookRead` and
  `BookListItem`.
- Validate tag ids; attach/detach tags in create/update; eager-load tags.
- Tests: create with tags, update replaces tags, invalid tag id → 400, list
  item includes `tag_ids`.

### Task 2: Existing-book lookup by ISBN

**Files:** `backend/app/api/v1/routes/books.py`,
`backend/app/repositories/book.py`, `backend/tests/test_books.py`

- `GET /books/isbn/{isbn}` — normalize and canonicalize either form, return
  `BookRead`; 404 for invalid or unknown.
- Tests: find by ISBN-10, by ISBN-13, with hyphens; unknown/invalid → 404.

### Task 3: Taxonomy endpoints

**Files:** `backend/app/schemas/taxonomy.py` (new),
`backend/app/repositories/taxonomy.py` (new),
`backend/app/api/v1/routes/taxonomy.py` (new),
`backend/app/api/v1/router.py`, `backend/tests/test_taxonomy.py` (new)

- List with `q` (case-insensitive contains) and `limit` (1–500, default 50),
  ordered by name.
- Create-or-get: trimmed, non-blank, max length; returns the existing row with
  the same case-insensitive name (200) or creates it.
- Publisher create accepts optional `country`.
- Tests: create then re-create with different case returns the same id; blank
  name → 422; list filters and orders; publisher country round-trips.

### Task 4: Frontend API client and reusable form

**Files:** `frontend/src/services/api.ts`,
`frontend/src/components/TaxonomyPicker.tsx` (new),
`frontend/src/components/BookForm.tsx` (new),
`frontend/src/pages/AddBookPage.tsx`, `frontend/src/pages/BookDetailsPage.tsx`

- Client: `lookupMetadata`, `decodeBarcode`, `fetchBookByIsbn`,
  `searchTaxonomy`, `createTaxonomy`, typed `ApiError` carrying `status` and
  `bookId` (from 409 `detail.book_id`).
- `TaxonomyPicker`: chips, debounced search, add-on-enter, optional create.
- `BookForm`: all book fields, publisher single-select, authors/genres/tags
  multi-select, cover upload/preview, save/cancel, duplicate link.
- Add Book: ISBN lookup + barcode capture + prefilled form.
- Book Details: full display and edit; `GET /books/{id}` returns resolved
  `authors`, `genres`, `tags`, and `publisher` names, so no extra requests are
  needed to resolve ids.

### Task 5: Documentation and gate

**Files:** `docs/API.md`, `docs/SYSTEM_ARCHITECTURE.md`,
`docs/superpowers/plans/2026-10-24-phase-1-closeout.md`, `.ai/state.md`

- Document taxonomy endpoints, by-ISBN lookup, `tag_ids`, and the add/edit flow.
- Tick the gate and mark the status row `Complete`.

**Exit criteria:** from a blank library, a book can be added by ISBN, by barcode
photo, or manually; its authors/genres/publisher/tags/cover are editable; a
second attempt with the same ISBN offers the existing book and creates nothing;
suite and build green.

**Gate:**

- [x] `cd backend && python -m pytest -q` — 88 passed
- [x] `cd frontend && npm run build` — green
- [x] No new migration in this phase
- [x] Docs updated (`API.md`, `SYSTEM_ARCHITECTURE.md`)
- [x] Status table and `.ai/state.md` updated; phase committed

---

## Phase 4 — Reading tracking

Source: spec §8.4 and §11 Phase 4.

**Goal:** every household member can record what they are reading and how far
along they are. A book page shows who is reading it, a Reading page shows who is
reading what, the library can be narrowed by member/status, and the dashboard
lists what is in progress right now.

**Design:**

- Migration `0004_members_and_reading`:
  - `members(id, name varchar(100) not null, created_at)` with unique
    `lower(name)`.
  - `reading_entries(id, book_id, member_id, status varchar(20) not null,
    current_page, started_on date, finished_on date, note text, updated_at)`.
  - `unique(book_id, member_id)`, FKs with `ON DELETE CASCADE`, indexes on
    `member_id` and `status`, and a check constraint limiting status to
    `want_to_read | reading | finished | abandoned`.
  - Working `downgrade()`.
- ORM models `Member` and `ReadingEntry`; both sides of the relationship use
  `cascade="all, delete-orphan"` so SQLite tests (no FK pragma) and PostgreSQL
  both remove entries with the book or member. `Book.reading_entries` added.
- `ReadingRepository` + `ReadingService`:
  - members: list (name order), create, rename, delete.
  - entries: list for a book, list filtered by member/status, upsert, delete.
  - progress is derived, never stored.
- Endpoints:
  - `GET /members`, `POST /members`, `PATCH /members/{id}`,
    `DELETE /members/{id}`. Duplicate name → 409, blank → 422.
  - `GET /books/{id}/reading` — entries with member name, book title/pages.
  - `PUT /books/{id}/reading/{member_id}` — upsert. `status=reading` defaults
    `started_on` to today when absent; `finished` defaults `finished_on` to
    today and, when the book has pages and `current_page` is omitted, sets
    `current_page = pages`. Explicit `null` clears optional fields. Page above
    `pages` → 422; finished before started → 422.
  - `DELETE /books/{id}/reading/{member_id}` — 204/404.
  - `GET /reading?member_id&status` — household entries ordered by most
    recently updated, each with book title/pages and member name.
- `GET /books` gains `member_id` and `status` filters using an `IN` subquery, so
  a book with several matching entries appears once. `member_id` alone means
  any entry; `status` alone means any member; both mean that member/status.
- `GET /insights` adds `currently_reading`: member, book, current page, and
  page count for entries with status `reading` (Phase 5 extends the rest).
- Frontend:
  - API client types/functions for members, reading entries, filters; add
    `member_id`/`status` to book-list params and `currently_reading` to
    insights.
  - New Reading page (`/reading`) with member management (add, rename, delete),
    member/status filters, and entry cards showing status, progress bar, dates,
    note, and a book link. Empty states and member-delete confirmation.
  - Book Details reading panel: entries per member with progress, dates, note,
    edit/remove; one form (member + status + page + dates + note) to upsert.
  - Library filters for member and status.
  - Dashboard "Currently reading" section linking to books.
  - Navigation entry for Reading.
  - Shared `StatusBadge` and `ProgressBar` components; accessible labels,
    44px hit targets, tabular numerals, and reduced-motion-safe styles.

### Task 1: Migration, models, schemas

**Files:** `backend/alembic/versions/0004_members_and_reading.py` (new),
`backend/app/models/member.py` (new), `backend/app/models/reading.py` (new),
`backend/app/models/book.py`, `backend/app/models/__init__.py`,
`backend/app/schemas/reading.py` (new), `backend/app/core/errors.py`

- Add the tables, relationship cascades, and Pydantic schemas described above.
- `DuplicateMemberError` for the 409 path.

### Task 2: Repository and service

**Files:** `backend/app/repositories/reading.py` (new),
`backend/app/services/reading.py` (new)

- `ReadingRepository`: member CRUD with case-insensitive uniqueness, eager
  entry queries, upsert (create or mutate), delete.
- `ReadingService`: defaults, page/date validation, filtering, member deletion.

### Task 3: Routes, filters, insights

**Files:** `backend/app/api/v1/routes/members.py` (new),
`backend/app/api/v1/routes/reading.py` (new), `backend/app/api/v1/router.py`,
`backend/app/api/v1/routes/books.py`, `backend/app/repositories/book.py`,
`backend/app/api/v1/routes/insights.py`, `backend/app/schemas/insights.py`

- Mount member and reading routes.
- Add `member_id`/`status` to `BookFilters` and the books list query.
- Add `currently_reading` to insights.
- Tests: `backend/tests/test_reading.py` (new) plus insights coverage.

### Task 4: Frontend API, Reading page, book panel

**Files:** `frontend/src/services/api.ts`,
`frontend/src/components/StatusBadge.tsx` (new),
`frontend/src/components/ProgressBar.tsx` (new),
`frontend/src/pages/ReadingPage.tsx` (new),
`frontend/src/pages/BookDetailsPage.tsx`, `frontend/src/App.tsx`,
`frontend/src/layouts/AppLayout.tsx`, `frontend/src/hooks/useBooks.ts`

- Client types and functions for members/entries.
- Reading page with member management, filters, and entry cards.
- Book Details reading panel with upsert/delete.
- Reading navigation entry.

### Task 5: Library filters, dashboard, styles, docs, gate

**Files:** `frontend/src/pages/LibraryPage.tsx`,
`frontend/src/pages/DashboardPage.tsx`, `frontend/src/styles.css`,
`docs/API.md`, `docs/DATABASE.md`, `docs/SYSTEM_ARCHITECTURE.md`,
`docs/superpowers/plans/2026-10-24-phase-1-closeout.md`, `.ai/state.md`

- Library member/status filters; dashboard in-progress list.
- Reading styles (cards, badges, progress, member rows, filters).
- Document members/reading endpoints, filters, and tables.
- Migration cycle, suite, build, and docs gate.

**Exit criteria:** two members can record different progress on the same book;
progress cannot exceed `pages`; finishing sets the finish date and page;
`/reading`, the book page, and the dashboard agree; deleting a member or book
removes their entries; suite and build green.

**Gate:**

- [x] `cd backend && python -m pytest -q` - 103 passed
- [x] `cd frontend && npm run build` - green
- [x] `0004_members_and_reading` upgrade → downgrade → upgrade on SQLite (and
      PostgreSQL when available)
- [x] Docs updated (`API.md`, `DATABASE.md`, `SYSTEM_ARCHITECTURE.md`)
- [x] Status table and `.ai/state.md` updated; phase committed

## Phase 5 — Tags, notes, filters, dashboard

Source: spec §8.5, §8.9 and §11 Phase 5.

**Goal:** a 1,000-book library can be narrowed to "reading, read by Maya, genre
Fantasy, 1990–2020" in one request and one screen; tags and notes round-trip;
the dashboard and insights pages describe the collection accurately.

**Design:**

- No migration. `tags`, `book_tags`, `books.notes`, and
  `reading_entries.note` already exist.
- Backend:
  - `BookFilters.tag` (case-insensitive exact tag name) joins `book_tags`, so
    `GET /books?tag=Fantasy` filters without changing list-item shape.
  - `GET /tags` gains `book_count` per tag, ordered by name. `q` and `limit`
    stay. `POST /tags` returns the same shape. New `PATCH /tags/{id}` (rename,
    duplicate → 409, blank → 422) and `DELETE /tags/{id}` (204, removes the
    association rows first so SQLite without FK pragmas stays clean).
  - `DuplicateTagError` in `app/core/errors.py`.
  - `GET /insights` becomes aggregate SQL instead of loading every book:
    `total_books`, `total_members`, `by_published_year`, `by_genre` (top 10),
    `by_author` (top 10), `by_language`, `currently_reading`, and
    `recently_added` (5 newest books with title, cover, created_at).
- Frontend:
  - API client: `TagSummary`, `book_count`, `fetchTags`, `renameTag`,
    `deleteTag`, `tag` in `BookListParams`; extended `Insights`.
  - Library filter bar: debounced search, genre, tag, year from/to, member,
    status, sort, and a Clear filters action. Any change resets the page
    offset. Book rows show tag chips resolved from the tag list.
  - New Tags page (`/tags`, navigation entry): tag counts, inline rename,
    delete with confirmation, empty state. Library links to it from the filter
    bar.
  - Dashboard: total books/members, currently reading, recently added.
  - Insights page: by-year, top genres, top authors, and language breakdowns
    using accessible horizontal bars.
  - Notes remain on Book Details (household note) and Reading (per-person
    note); tests cover the round-trip.
- Tests: tag list/rename/delete and tag filtering; extended insights totals,
  top-10 ordering, languages, recently added; notes round-trip.

### Task 1: Tag filtering and tag management API

**Files:** `backend/app/repositories/book.py`,
`backend/app/api/v1/routes/books.py`, `backend/app/repositories/taxonomy.py`,
`backend/app/api/v1/routes/taxonomy.py`, `backend/app/schemas/taxonomy.py`,
`backend/app/core/errors.py`, `backend/tests/test_tags.py` (new),
`backend/tests/test_books.py`

- Add `tag` to `BookFilters` and the list route; join `Book.tags` and compare
  `lower(Tag.name)`.
- Add `book_count`, rename, and delete to the tag API.
- Cover duplicate/blank/404 behaviour and association cleanup.

### Task 2: Extended insights

**Files:** `backend/app/api/v1/routes/insights.py`,
`backend/app/schemas/insights.py`, `backend/tests/test_insights.py`

- Replace full-table loading with grouped queries and limits.
- Add `total_members`, `by_genre`, `by_author`, `by_language`, and
  `recently_added`.

### Task 3: Frontend filters and tag management

**Files:** `frontend/src/services/api.ts`, `frontend/src/hooks/useBooks.ts`,
`frontend/src/pages/LibraryPage.tsx`, `frontend/src/pages/TagsPage.tsx` (new),
`frontend/src/App.tsx`, `frontend/src/layouts/AppLayout.tsx`,
`frontend/src/shared/BarList.tsx` (new), `frontend/src/styles.css`

- Full filter bar with debounced text, selects, year range, and clear.
- Tag chips on each library row.
- Tags page with counts, rename, delete, and empty state.

### Task 4: Dashboard and insights pages

**Files:** `frontend/src/pages/DashboardPage.tsx`,
`frontend/src/pages/InsightsPage.tsx`, `frontend/src/shared/BarList.tsx`,
`frontend/src/styles.css`

- Dashboard: totals, currently reading, recently added.
- Insights: year, genre, author, and language breakdowns with accessible bars.

### Task 5: Docs and gate

**Files:** `docs/API.md`, `docs/DATABASE.md` (tag count note),
`docs/SYSTEM_ARCHITECTURE.md`, plan status table, `.ai/state.md`,
`.ai/memory.md`

- Document `tag`, tag rename/delete, and the extended insights payload.
- Run the suite, build, and migration cycle; commit.

**Exit criteria:** combining status, member, genre, tag, and year filters returns
the right books in one request; tags can be renamed and deleted without leaving
orphans; book/reading notes round-trip; dashboard and insights numbers match the
catalog; suite and build green.

**Gate:**

- [x] `cd backend && python -m pytest -q` - 112 passed
- [x] `cd frontend && npm run build` - green
- [x] No new migration this phase (existing cycle remains green)
- [x] Docs updated (`API.md`, `DATABASE.md`, `SYSTEM_ARCHITECTURE.md`)
- [x] Status table and `.ai/state.md` updated; phase committed
