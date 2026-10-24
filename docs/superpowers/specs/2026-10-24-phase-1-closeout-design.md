# Phase 1 Closeout — Household Library Design

**Status:** Draft for approval
**Date:** 2026-10-24
**Author:** Aryan (with agent)
**Scope:** Finish `docs/FUTURE.md` Phase 1 for real household use, in five gated phases.

---

## 1. Intent and why

Kakurega exists to answer three questions about a large home library:

1. **What do we own?** (and where is the record of it)
2. **What is *I* reading, and how far along am I?**
3. **What is everyone else in the family reading?**

Today the API can store books and the UI can list them, but books can only be
added one at a time through a title-only form. There is no way to bring in an
existing collection, no way to record reading progress, and no way to link a
book to the people reading it. The catalog is therefore empty in practice.

This phase closes that gap. Success looks like: the household's existing books
are in the app, each book's metadata is correct enough to find, and every family
member's reading state is visible on the dashboard and on the book page.

## 2. Users and usage

- **Primary user:** the owner (you), on a laptop/desktop browser at home.
- **Secondary users:** family members, occasionally, on phones on the same
  home network, to update their own progress.
- **Scale target:** 500–2,000 books, 2–6 members, one household.
- **Trust model:** the app is on a trusted home network. There is no login.

## 3. Goals

- Enter a whole existing collection in one sitting (CSV/Goodreads import).
- Add a single book from its ISBN or a photo of its barcode, with metadata
  prefilled from OpenLibrary/Google Books and then editable.
- Correct any book's metadata: title, authors, publisher, genres, year, pages,
  language, description, cover.
- Track reading per person: status, current page, start/finish dates, a note.
- Find a book fast: text search plus filters (status, member, genre, year, tag).
- Annotate: tags and notes.
- Never silently create duplicates: ISBN is a first-class identity.
- Keep the whole thing fast with 1,000+ books.

## 4. Non-goals (this phase)

- Authentication, accounts, or per-user permissions. Family members are rows in
  a list, not logins.
- Multiple physical copies of the same title (`book_copies`).
- Series tracking, lending history, wish lists, recommendations, AI, OCR
  fallback, native mobile apps, cloud sync, S3 storage.
- Editing authors/publishers/genres beyond create + list.
- Public deployment hardening (TLS, rate limiting at the edge, backups).
- Goodreads two-way sync; import only.

## 5. Anti-goals

Things that would make this phase a failure even if it "works":

- A phase that leaves `main` unable to boot or migrate.
- Import that loses rows without reporting which ones and why.
- A UI flow that creates a duplicate book when a button is double-clicked.
- Reading progress that cannot be corrected when a page number is mistyped.
- A plan so large it is never finished; each phase must stand alone.

## 6. Constraints

- Stack stays FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL, React + Vite +
  TypeScript. No new backend framework and no frontend UI library.
- Tests run on SQLite; production runs PostgreSQL. Migrations must work on both.
- Every schema change is an Alembic migration, never `create_all` in production.
- Keep the existing layering: route → service → repository; Pydantic schemas at
  the edge.
- API responses stay bare objects (no `{success, data}` envelope).
- No secret or personal data leaves the machine except ISBN/title lookups to
  OpenLibrary/Google Books and remote cover URLs.

## 7. Approaches considered

**A. Vertical slices, entry-first (chosen).** Five independently shippable
phases: foundation → bulk import → catalog workflow → reading tracking →
notes/tags/filters/dashboard. Each phase ends with a working app and a gate.

**B. Schema-first, single frontend pass.** Design all tables and endpoints, then
build the UI once. Cleaner schema on paper, but nothing is usable until the end
and details get guessed without real data.

**C. Reading-first.** Ship members + progress before cataloging. Answers "who is
reading what" soonest, but the library stays nearly empty while you do it.

A wins because the collection is the bottleneck: with books in the app, every
later feature has something to act on, and each phase gives immediate value.

## 8. Decided behaviour

### 8.1 Identity and duplicates

- ISBNs are normalized on write: digits only, plus a trailing `X` for ISBN-10;
  hyphens and spaces stripped; `x` uppercased.
- **Canonical identity is ISBN-13.** When a valid ISBN-10 is supplied without an
  ISBN-13, the ISBN-13 form is derived and stored in both columns. A 979-prefixed
  ISBN-13 has no ISBN-10 and is stored alone. Consequently `isbn13` is unique
  when present, and `isbn10` is unique when present (partial unique indexes);
  a book saved as ISBN-10 and later imported as its ISBN-13 is the same row.
- Create and import check both forms; a match on either returns **409** with
  `{"detail": "...", "book_id": <existing>}`.
- Search normalizes a query that looks like an ISBN: `q=0-14-032872-6` finds the
  row stored as `9780140328721`.
- Import also treats an exact normalized `title` + first-author match as a
  duplicate **when the row has no usable ISBN**. Normalization: Unicode
  casefold, collapse whitespace, strip leading/trailing punctuation. A row with
  no author is never deduped on title alone — distinct books may share a title.
  This fallback applies to import only; the create API dedupes on ISBN alone.
- Duplicates are skipped and reported, never silently merged. `update_existing`
  can explicitly refresh an existing row's empty metadata instead.

### 8.2 Book validation

- `title`: trimmed, 1–500 characters, non-blank.
- `pages`: 1–100,000.
- `published_year`: 1000–current year + 1.
- `language`: ≤ 20 characters. ISBNs must pass length + checksum validation.
- Update payloads may omit fields, but may not set a required field to `null`.
- Any database `IntegrityError` maps to 409 (duplicates) or 422 (bad values),
  never 500.

### 8.3 Lists, search, pagination

- `GET /books` is the single list/search endpoint. `GET /search` is removed;
  the frontend uses `/books?q=`.
- Query parameters: `q`, `status`, `member_id`, `genre_id`, `tag`,
  `year_from`, `year_to`, `sort` (`title|added|year`), `limit` (default 50, max
  200), `offset`.
- Filter semantics: `member_id` alone means "this member has any reading entry";
  `status` alone means "any member has this status"; both together mean "this
  member has this status". A book matching several entries still appears once
  (distinct books, outer join). `status` has no "unfinished" pseudo-value — use
  `status=reading`.
- Response: `{"items": [...], "total": <int>, "limit": <int>, "offset": <int>}`.
- List items omit `description` (detail-only) to keep payloads light.
- Text search covers title, subtitle, ISBNs, description, author names, and
  publisher name. `%`, `_`, and `\` are escaped (literal search).
- Books are eager-loaded with authors and genres (no N+1).
- `books.created_at` is added so `sort=added` and "recently added" work.

### 8.4 Household members and reading

- `members(id, name unique case-insensitive, created_at)`. No auth, no email.
- `reading_entries(id, book_id, member_id, status, current_page,
  started_on, finished_on, note, updated_at)` with
  `unique(book_id, member_id)` and cascade delete with the book or member.
- `status` ∈ `want_to_read | reading | finished | abandoned`; absence of an
  entry means nobody has recorded it.
- One upsert endpoint: `PUT /books/{id}/reading/{member_id}`. Setting
  `status=reading` defaults `started_on` to today; `finished` defaults
  `finished_on` to today and, when `pages` is known and `current_page` is
  omitted, sets `current_page = pages`.
- `current_page` is validated against the book's `pages` when known.
- Progress is derived (`current_page / pages`), never stored as a percentage.

### 8.5 Tags and notes

- `tags(id, name unique case-insensitive)` + `book_tags(book_id, tag_id)`.
- `books.notes` is a free-text household note.
- `reading_entries.note` is a per-person note about their read.
- Tags are a filter facet and are shown on book cards.

### 8.6 Import

- `POST /import/csv?update_existing=false` accepts a CSV file (≤ 10 MB) with a
  header row. Import never calls OpenLibrary/Google Books.
- Recognized headers: Goodreads export names (`Title`, `Author`, `ISBN`,
  `ISBN13`, `Number of Pages`, `Publisher`, `Year Published`, `Bookshelves`,
  `My Review`, `Date Read`, `My Rating`, `Exclusive Shelf`) and the API's own
  field names (`title`, `author(s)`, `isbn`, `isbn13`, `pages`, `publisher`,
  `published_year`, `tags`, `genres`, `notes`).
- `Bookshelves` → tags (comma- or semicolon-separated; the Goodreads default
  shelves `read`, `currently-reading`, `to-read` are dropped). `genres` → genres
  (same separators). Import creates missing authors, publishers, genres, and
  tags by trimmed, case-insensitive name.
- `My Review` → `books.notes`. `My Rating`, `Exclusive Shelf`, and `Date Read`
  are **not** imported this phase (there is no rating column, and members do not
  exist yet); the response reports them under `ignored_columns` so nothing is
  dropped silently. A later phase can backfill reading history from the same
  file because `update_existing` exists.
- Per-row processing in a savepoint: one bad row never aborts the file.
- An invalid or checksum-failing ISBN does **not** fail the row: the book is
  imported without an ISBN and the row number is reported in `warnings`, so a
  good book is not lost. A row with no usable title is `failed`.
- Response:
  `{"created": n, "updated": n, "skipped_duplicates": n,
  "failed": [{"row": n, "reason": "..."}], "warnings": [{"row": n, "reason": "..."}],
  "ignored_columns": ["My Rating", ...]}`. `failed` and `warnings` are capped at
  100 entries each.
- With `update_existing=true`, duplicate rows fill only fields that are empty on
  the existing book (never overwrite non-empty metadata or notes) and are
  counted in `updated`.

### 8.7 Catalog workflow (UI)

- Add Book offers: type/paste ISBN, or take/upload a photo of the barcode.
  Barcode photo decoding uses the existing `/barcode` endpoint; the browser
  uses a file input with `capture="environment"` (no live camera stream).
- ISBN → `/lookup` → prefilled form (title, authors, publisher, year, pages,
  description, cover). Every field remains editable.
- Authors/genres/publisher are chosen from searchable pickers backed by
  idempotent create-or-get endpoints (`POST /authors`, `/publishers`,
  `/genres`).
- If lookup finds an existing ISBN, the UI offers "open the existing book"
  instead of creating a second row.
- Book Details edits all fields, relationships, cover, notes, and tags.

### 8.8 Barcode

- Only EAN-13 `978`/`979` prefixes with a valid checksum, or ISBN-10 with a
  valid checksum, count as an ISBN. Other EAN product codes return 404.
- Decoding remains server-side via zxing-cpp.

### 8.9 Dashboard

Extends `GET /insights` with: totals, by year, by genre (top 10), by author
(top 10), by language, currently reading per member, and recently added.

## 9. Data model changes

| Migration | Adds |
|---|---|
| `0003_identity_and_listing` | partial unique `isbn10`/`isbn13`, unique `lower(name)` on authors/publishers/genres, `books.created_at`, indexes for title/year/publisher, `tags`, `book_tags`, `books.notes` |
| `0004_members_and_reading` | `members`, `reading_entries` (+ unique + cascade + indexes) |

No further migrations are expected this phase; import and dashboard reuse the
tables above. If one turns out to be needed it is added in the owning phase.

Every migration has a working `downgrade()` and is exercised with
`alembic upgrade head` then `alembic downgrade -1` on PostgreSQL.

## 10. API surface after this phase

```
GET    /health
GET    /books?q&status&member_id&genre_id&tag&year_from&year_to&sort&limit&offset
POST   /books
GET    /books/{id}
PUT    /books/{id}
DELETE /books/{id}
GET    /books/{id}/reading
PUT    /books/{id}/reading/{member_id}
DELETE /books/{id}/reading/{member_id}
GET    /reading?member_id&status
GET    /members
POST   /members
PATCH  /members/{id}
DELETE /members/{id}
GET    /authors?q            POST /authors
GET    /publishers?q         POST /publishers
GET    /genres?q             POST /genres
GET    /tags?q               POST /tags
POST   /lookup
POST   /barcode
POST   /upload/image
POST   /import/csv
GET    /insights
```

Removed: `GET /search` (folded into `/books`).

## 11. Phase breakdown and gates

The implementation plan is one document with five phase sections. The executor
**works one phase at a time** and does not begin the next phase until the
current phase's gate is green and ticked. A status table at the top of the plan
is the single source of truth for "where are we"; `.ai/state.md` mirrors it.

**Gate (every phase):**
1. `cd backend && python -m pytest -q` — all green.
2. `cd frontend && npm run build` — green.
3. Any new migration: `alembic upgrade head` then `alembic downgrade -1` then
   `alembic upgrade head` succeeds on PostgreSQL (Docker compose or local).
4. Docs updated if behaviour or endpoints changed.
5. Plan status table updated and committed with the phase.

### Phase 1 — Foundation and correctness
Unique ISBNs, validation, 409/422 semantics, pagination + eager loading,
literal search, `books.created_at`, barcode checksum, chunked uploads, debug
default off.

**Exit:** with 1,000 seeded books, `GET /books?limit=50` issues a constant
number of queries; duplicate ISBN create returns 409; `PUT {"title": null}`
returns 422; any 13-digit non-book EAN returns 404 from `/barcode`; the suite is
green.

### Phase 2 — Bulk import
CSV/Goodreads import with per-row results, duplicate handling, tag/genre
mapping, and warnings; Import page in the UI showing created/updated/skipped/
failed/warnings.

**Exit:** a 500-row Goodreads-style fixture imports with the exact expected
counts; re-importing the same file creates zero rows (and with
`update_existing=true` fills blanks without overwriting); malformed ISBNs are
imported with warnings instead of dropped; the library shows the imported books
paginated.

### Phase 3 — Catalog workflow
ISBN/barcode entry, lookup prefill, relationship pickers, create-or-get
author/publisher/genre/tag endpoints, full Book Details editing, duplicate
interception in the UI.

**Exit:** from a blank library, a book can be added by typing an ISBN, by
photographing a barcode, or fully manually; its authors/genres/publisher/cover
are editable afterwards; adding the same ISBN twice offers the existing book
and creates nothing.

### Phase 4 — Reading tracking
Members, reading entries with status/progress/dates/note, per-book reading
panel, "who is reading what" page, filters by member/status, dashboard in-progress
list.

**Exit:** two members can record different progress on the same book; progress
is capped by `pages`; finishing sets the date; the dashboard and `/reading`
agree with the book page; deleting a member or book removes their entries.

### Phase 5 — Tags, notes, filters, dashboard
Tag management and filtering, book and reading notes, full filter bar with sort,
extended insights, docs refresh.

**Exit:** a 1,000-book library can be narrowed to, say, "reading, read by
Maya, genre Fantasy, 1990–2020" in one request and one screen; notes and tags
round-trip; dashboard numbers match the filtered totals.

## 12. Left to the builder

- Exact component structure and styling; reuse the existing pages and
  `styles.css` conventions.
- Whether import exposes a column-mapping UI or infers headers (headers are
  specified above; inference is enough this phase).
- Exact index names, query-count targets, and test fixtures.
- How the barcode photo input is presented on desktop vs phone (same file
  input is acceptable).

## 13. Risks

- **Google Books rate limits** during bulk lookups: import must not call external
  APIs per row; it imports what the CSV carries only.
- **SQLite vs PostgreSQL differences** in partial unique indexes: both support
  them; migration tests must run on PostgreSQL before the gate passes.
- **No auth on the LAN** means any device on the network can edit the library.
  Accepted for this phase; revisit before any non-home deployment.
- **Scope creep into Volume 2** (copies, lending, series): explicitly deferred.

## 14. Acceptance for the whole phase

Phase 1 (the roadmap phase) is done when all five gates are ticked, the
household's books can be imported and corrected, every member can record reading
progress, and the docs describe exactly what exists.
