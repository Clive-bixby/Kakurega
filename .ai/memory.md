# Kakurega — Project Memory

## Purpose

This document stores stable project knowledge that should persist across development sessions.

Its purpose is to prevent repeatedly rediscovering important decisions while avoiding unnecessary context usage.

Keep this document concise.

If information can be easily derived from the codebase, it generally does not belong here.

---

# Update Policy

Update this document only when stable project knowledge changes.

Good examples:

- Architectural decisions
- Established project conventions
- Reusable project patterns
- Important implementation decisions
- New shared abstractions
- Long-term constraints

Do NOT update this document for:

- Temporary work
- Current tasks
- Debugging
- TODOs
- Experimental code
- Feature progress
- Refactoring notes

---

# Project Status

Current Phase

MVP Development

Current Focus

Phased roadmap to daily-use readiness is in progress (plan in `docs/superpowers/plans/`). Phases 1–5 (foundation, bulk import, catalog workflow, reading tracking, tags/filters/dashboard) are complete. OCR and Gemini Vision remain future work.

---

# Core Decisions

This section records important project decisions that future work should respect.

Example format:

Decision:
Reason:
Alternative considered:

Only add decisions that are unlikely to change frequently.

Decision: ISBN-13 is canonical book identity; ISBN-10 is stored alongside it.
Reason: The same book must never be created twice because someone typed the other ISBN form.
Alternative considered: Storing only the form the user entered.

Decision: List endpoints return a page envelope `{items, total, limit, offset}`.
Reason: The household library is expected to reach thousands of books; the client must not fetch them all.
Alternative considered: A flat array with client-side pagination.

Decision: `GET /books` is the only book list/search endpoint; `/search` was removed.
Reason: Search is a filter over the same collection, not a separate resource.
Alternative considered: Keeping `/search` beside a paginated `/books` (two code paths).

Decision: Domain errors live in `app/core/errors.py` and routes translate them to HTTP.
Reason: Keeps repositories free of FastAPI imports while preserving 409/400 semantics.

Decision: Uploads are read in 64 KB chunks and rejected with 413 past 5 MB.
Reason: Never buffer an unbounded request body in memory.
Alternative considered: Trusting `Content-Length` alone.

Decision: Alembic migrations touching SQLite constraints use `batch_alter_table`.
Reason: SQLite cannot ALTER constraints; batch mode is required for the test/migration cycle.
Alternative considered: PostgreSQL-only migrations, which break local verification.

Decision: Import is CSV-only with header inference and never calls metadata APIs.
Reason: Bulk import must be fast, offline, and free of provider rate limits.
Alternative considered: Per-row Open Library/Google Books enrichment during import.

Decision: Import process runs per-row savepoints and commits the file once.
Reason: One bad row must not abort the file or leave half a transaction behind.
Alternative considered: One transaction per row (slow) or one transaction for everything (all-or-nothing).

Decision: A row with no usable ISBN is deduped by case-insensitive title + author.
Reason: Re-importing a file with malformed ISBNs must not keep creating rows.
Alternative considered: ISBN-only dedupe, which duplicates every no-ISBN row on re-import.

Decision: Taxonomy endpoints are idempotent create-or-get, and the editor defers
creating new names until the form is saved.
Reason: Typing a name and cancelling must not leave stray authors or tags.
Alternative considered: Creating entities as the user types.

Decision: Book detail responses embed resolved taxonomy names; list items stay lean.
Reason: Details and edit need names to render and prefill, while the list only
needs ids and must stay cheap for thousands of books.
Alternative considered: Client-side id-to-name resolution with extra requests.

Decision: Household members are lightweight names with no auth, email, or login;
reading state is one row per `(book, member)`.
Reason: The app is a shared home library, so "who is reading this" must work
without account setup while keeping the schema ready for real accounts later.
Alternative considered: A full user table with credentials in v1.

Decision: Reading progress is derived from `current_page / book.pages`, never
stored as a percentage, and `current_page` cannot exceed `pages`.
Reason: Page counts change and two stored representations can disagree.
Alternative considered: Persisting a progress percentage alongside the page.

Decision: Reading entries cascade through the ORM relationship
(`cascade="all, delete-orphan"`) as well as the database `ON DELETE CASCADE`.
Reason: SQLite tests run without foreign-key pragmas, so DB-only cascades would
leave orphaned entries in tests.
Alternative considered: Enabling `PRAGMA foreign_keys` only in tests.

Decision: `GET /books?member_id&status` uses an `IN` subquery over
`reading_entries` rather than a join.
Reason: A book with several matching entries must appear once, and count queries
must stay correct.
Alternative considered: Joining and `DISTINCT`, which complicates pagination.

Decision: The book tag filter is `?tag=<name>` (case-insensitive exact match),
not `?tag_id=`.
Reason: Tags are household labels chosen by name in the UI; a name keeps shareable
filtered URLs readable and survives tag re-creation with a new id.
Alternative considered: Filtering by tag id, which the filter bar would have to
resolve and which breaks when a tag is deleted and re-added.

Decision: Tag `book_count` is derived from `book_tags` in the query; no counter
column exists.
Reason: A stored counter can drift, and tag lists are small enough that a grouped
count is cheap.
Alternative considered: Maintaining a denormalised count on `tags`.

Decision: Deleting a tag explicitly deletes its `book_tags` rows before deleting
the tag.
Reason: SQLite runs without foreign-key pragmas in tests, so `ON DELETE CASCADE`
alone would leave orphaned associations.
Alternative considered: Relying only on the database cascade.

Decision: The interface follows the Literary Noir theme captured in
`design/stitch` (charcoal surfaces, lavender accent, Inter, 260px sidebar,
topbar search, cover-forward grids).
Reason: The visual reference is the product brief, so screens must be judged
against those PNGs rather than an invented palette.
Alternative considered: Keeping the earlier plain utility styling and treating
the mockups as loose inspiration.

Decision: Every design token and component class lives in the single global
`frontend/src/styles.css`; pages compose classes instead of inline styles.
Reason: One token layer keeps screens consistent and makes the theme auditable.
Alternative considered: CSS modules or per-component style files.

Decision: List responses include `author_names` (and insights include
`cover_url`/`author_name`) instead of full taxonomy objects.
Reason: Cover grids need bylines and covers without N+1 detail requests, while
list payloads must stay cheap.
Alternative considered: Fetching `GET /books/{id}` per card.

Decision: Books without cover art render a generated typographic
`BookCover` (gradient, title, Kakurega mark) rather than a blank frame.
Reason: A cover-forward grid collapses visually when most of a personal library
has no artwork.
Alternative considered: A generic placeholder image.

Decision: Below 900px the shell becomes a horizontal header and the grids stack.
Reason: The sidebar consumes the viewport on tablets and phones, and the topbar
search must stay reachable.

Decision: `GET /insights` uses grouped aggregate SQL with fixed limits (top 10
genres/authors, 5 newest books) rather than loading every book into Python.
Reason: Dashboard numbers must stay cheap as the library grows and the two pages
never need the full table.
Alternative considered: Loading all books and aggregating in Python, which was
the earlier implementation.

---

# Established Patterns

Record reusable patterns once they become established.

Examples:

- preferred service pattern
- repository structure
- error handling approach
- API response structure
- frontend state management pattern

Avoid documenting patterns before they are actually used.

Backend

- FastAPI app creation lives in `backend/app/main.py` via `create_app()`.
- Versioned routes are collected under `backend/app/api/v1` and mounted at the configured API prefix.
- Route dependencies use `get_db` from `backend/app/api/deps.py`, which reads `request.app.state.session_factory`.
- Business logic lives in services; database access lives in repositories.
- Repositories raise domain errors; routes map them to status codes.
- Pydantic schemas live under `backend/app/schemas`.
- Pure helpers (ISBN, upload limits) live under `backend/app/core`.

Frontend

- React routing is centralized in `frontend/src/App.tsx`.
- The primary application shell lives in `frontend/src/layouts/AppLayout.tsx`.
- API calls are centralized in `frontend/src/services/api.ts`.
- Data fetching uses small hooks such as `useBooks`.
- Add/edit forms share `BookForm`; taxonomy fields use `TaxonomyPicker` rather
  than free-text names.
- API errors use `ApiError` so callers can branch on `status` and `bookId`.
- Styling is one global stylesheet using CSS variables; new screens reuse the
  existing `.panel`, `.book-grid`, `.chip`, `.btn-primary`, and `PageHeader`
  patterns instead of adding new one-off styles.

---

# Shared Building Blocks

Maintain a high-level index of important reusable parts of the application.

Examples:

Frontend

- `AppLayout` provides the persistent sidebar, topbar search (`Ctrl/Cmd+K`), and
  mobile header.
- `PageHeader` provides the page eyebrow, title, description, and action slot.
- `BookCover` renders a cover image or a deterministic typographic fallback.
- `BookForm` renders every book field for both create and edit.
- `TaxonomyPicker` provides chips, debounced search, and create-on-enter.
- `StatusBadge` maps reading statuses to labels and badge classes.
- `ProgressBar` renders accessible derived page progress with tabular numbers.
- `EmptyState` standardises empty/placeholder panels.
- `BarList` renders accessible horizontal count bars for insights breakdowns.
- `ReadingPanel` records one member's reading state for a book.
- `TagsPage` manages household tags: counts, inline rename, delete, create.
- Library filter bar composes text, genre, tag, year range, member, status, and
  sort into one request and resolves `tag_ids` to names from the loaded tag list.

Common hooks

- `useBooks` fetches and exposes book list state.

Backend

Shared services

- `BookService` handles book CRUD.
- `ReadingService` handles members and reading entries.
- Metadata lookup service queries Open Library and Google Books.
- Barcode decoding service extracts ISBNs.

Repositories

- `BookRepository` manages books and relationships.
- `ReadingRepository` manages members and reading entries with eager loading.

Utilities

- `create_app()` builds the FastAPI application and lifespan.
- `app.core.isbn` canonicalises and validates ISBNs; use it instead of hand-parsing.
- `app.core.uploads.read_limited` enforces chunked upload limits.
- `app.core.csv_import.parse_csv` parses Goodreads/Kakurega CSV headers into rows.
- `ImportService` orchestrates CSV imports; `CatalogRepository` creates named entities case-insensitively.
- `TaxonomyRepository` lists taxonomy entities, performs committed create-or-get,
  and owns tag counts/rename/delete.
- `BookFilters` carries list-query filters into `BookRepository`.

Infrastructure

- Docker Compose provides PostgreSQL, backend, and frontend.

Only list reusable building blocks that future features should discover instead of recreating.

---

# External Integrations

- Open Library: primary metadata source.
- Google Books: secondary metadata source.
- zxing-cpp: local barcode decoding.
- Pillow: image handling for barcode decoding.

---

# Constraints

Long-term constraints that every feature should respect.

Examples:

Desktop-first

Single-user MVP

Backend is the source of truth

Barcode before OCR

OCR before AI Vision

Do not repeat information already documented elsewhere unless it is critical.

---

# Lessons Learned

When a mistake leads to a permanent improvement, record it here.

Examples:

"We no longer expose repositories directly to routes."

"We standardized API responses."

Avoid recording temporary implementation issues.

---

# Maintenance

Whenever completing a feature, ask:

Did this introduce knowledge that future development should remember?

If no:

Do not modify this document.

If yes:

Update only the relevant section.

Keep entries concise.

Replace outdated information instead of appending duplicates.

---

# Guiding Principle

This document should answer:

"What would an experienced maintainer of Kakurega want every future coding session to already know?"

If something does not help answer that question, it probably does not belong here.
