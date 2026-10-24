<div align="center">
  <img src="frontend/public/icon.svg" alt="Kakurega emblem" width="128" height="128" />
  <h1>Kakurega</h1>
  <p><strong>A personal home-library catalogue.</strong><br />
  Catalogue your shelves, scan barcodes to add books, track who is reading what,
  and see what your collection says about you.</p>
</div>

---

Kakurega (隠れ家, "a hiding place") is a small, self-hosted library manager: a
FastAPI + PostgreSQL backend, a React + TypeScript frontend, and no accounts,
trackers, or third-party storage. Your catalogue lives on your machine; the only
outbound calls are optional ISBN metadata lookups.

![Dashboard](docs/assets/dashboard.jpg)

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Quick start with Docker](#quick-start-with-docker)
- [Local development](#local-development)
- [Configuration](#configuration)
- [Database and migrations](#database-and-migrations)
- [Using Kakurega](#using-kakurega)
  - [Adding a book](#adding-a-book)
  - [Importing a CSV](#importing-a-csv)
  - [Reading and household members](#reading-and-household-members)
- [Screenshots](#screenshots)
- [Tests](#tests)
- [Project structure](#project-structure)
- [API](#api)
- [App icon and branding](#app-icon-and-branding)
- [Deployment notes](#deployment-notes)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## Features

- **Catalogue** — title, subtitle, authors, publisher, publication year, page
  count, ISBN-10/ISBN-13, description, notes, cover image, genres, and tags.
- **Add by ISBN or barcode** — type an ISBN (10 or 13, hyphens allowed) or upload
  a photo/scan of a barcode. Metadata and covers are looked up from Open Library,
  with Google Books as a fallback. Everything is still editable by hand.
- **Cover art** — upload your own cover (JPEG, PNG, or WebP up to 5 MB). Books
  without a cover get a generated typographic cover using the Kakurega emblem.
- **Search and filter** — free-text search across titles, authors, publishers,
  ISBNs, and descriptions, plus filters for genre, tag, publication year, member,
  and reading status. Sort by title, recently added, or year.
- **Reading tracking** — per-member reading entries with a status
  (`want_to_read`, `reading`, `finished`, `abandoned`), current page, and progress
  bars. A book can be read by several household members at once.
- **Insights** — collection totals, authors on the shelf, reading-now count, and
  breakdowns by decade, genre, author, and language.
- **CSV import** — bring in an export from Goodreads, StoryGraph, a spreadsheet,
  or anything with a title column. Column names are matched leniently, duplicates
  are detected, and per-row problems are reported.
- **One fixed theme** — the "Literary Noir" dark theme: charcoal surfaces, a
  lavender accent, and warm gold book-plate details.

## Tech stack

| Layer | Stack |
| --- | --- |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2 / pydantic-settings |
| Database | PostgreSQL 16 (the default), SQLite for quick local experiments |
| Barcode | `zxing-cpp` + Pillow |
| Frontend | React 19, TypeScript, Vite 6, React Router 7, `lucide-react` |
| Styling | Handwritten CSS with design tokens (`frontend/src/styles.css`) |
| Packaging | Docker, Docker Compose |

## Quick start with Docker

The fastest path: one command starts PostgreSQL, applies migrations, the API, and
the frontend.

**Prerequisites:** Docker Desktop (or Docker Engine + Compose v2).

```bash
git clone https://github.com/Clive-bixby/Kakurega.git
cd Kakurega
docker compose up --build
```

Then open:

| Service | URL |
| --- | --- |
| App | <http://localhost:5173> |
| API | <http://localhost:8000/api/v1/health> |
| Interactive API docs | <http://localhost:8000/docs> |

The first build takes a few minutes (Python and Node base images, `pip install`,
`npm ci`). Later starts are fast:

```bash
docker compose up          # start
docker compose down        # stop, keep data
docker compose down -v     # stop and delete the database + uploaded covers
```

What Compose creates:

| Service | What it does | Port |
| --- | --- | --- |
| `postgres` | PostgreSQL 16 with a named volume `postgres_data` | 5432 |
| `migrate` | One-shot `alembic upgrade head`, then exits | — |
| `backend` | Uvicorn API; uploads in the `backend_storage` volume | 8000 |
| `frontend` | Vite dev server serving the UI and proxying `/api` + `/storage` | 5173 |

Ports are configurable in `.env` (see [Configuration](#configuration)):

```bash
cp .env.example .env   # macOS/Linux
Copy-Item .env.example .env   # Windows PowerShell
```

## Local development

Run the two halves separately so both hot-reload. PostgreSQL is the supported
database; if you do not have it installed, you can either start just the database
with `docker compose up postgres -d` or point the backend at SQLite.

**Prerequisites**

- Python 3.11 or newer
- Node.js 20 or newer (npm 10+)
- PostgreSQL 16 — or Docker, or SQLite

### 1. Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install the backend and its test dependencies:

```bash
pip install -e ".[dev]"
```

Create the database (skip if you are using SQLite or the Docker database):

```bash
createdb kakurega     # or: psql -U postgres -c "CREATE DATABASE kakurega;"
```

The URL used below assumes a `kakurega` role with password `kakurega_password`.
Substitute your own credentials if your database was created differently.

Point the app at the database and migrate:

```powershell
# Windows PowerShell
$env:KAKUREGA_DATABASE_URL = "postgresql+psycopg://kakurega:kakurega_password@localhost:5432/kakurega"
alembic upgrade head
uvicorn app.main:app --reload
```

```bash
# macOS / Linux
export KAKUREGA_DATABASE_URL="postgresql+psycopg://kakurega:kakurega_password@localhost:5432/kakurega"
alembic upgrade head
uvicorn app.main:app --reload
```

The API is now at <http://127.0.0.1:8000>. Confirm it is alive:

```bash
curl http://127.0.0.1:8000/api/v1/health
# {"status":"ok","app_name":"Kakurega API","environment":"development"}
```

**Prefer SQLite?** Skip database creation and use:

```powershell
$env:KAKUREGA_DATABASE_URL = "sqlite:///./kakurega.db"
alembic upgrade head
```

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` and `/storage` to
`http://localhost:8000`, so the UI talks to your local API without any CORS setup.

If your API runs somewhere else, set the proxy target before starting Vite:

```powershell
$env:VITE_API_PROXY_TARGET = "http://127.0.0.1:9000"
npm run dev
```

> The frontend calls `/api/v1/...` directly. Only the proxy target is
> configurable — there is no separate API base-URL variable in the client.

### 3. Production build (frontend check)

```bash
cd frontend
npm run build     # type-checks with tsc and bundles into frontend/dist
npm run preview   # serve the built bundle locally
```

## Configuration

The backend reads environment variables with the `KAKUREGA_` prefix, and also
reads `backend/.env` if present. Defaults are shown below.

| Variable | Default | Purpose |
| --- | --- | --- |
| `KAKUREGA_APP_NAME` | `Kakurega API` | Shown in the API docs and `/health` |
| `KAKUREGA_ENVIRONMENT` | `development` | Free-form label, echoed by `/health` |
| `KAKUREGA_DEBUG` | `false` | Enables FastAPI debug mode |
| `KAKUREGA_API_V1_PREFIX` | `/api/v1` | Prefix for every API route |
| `KAKUREGA_DATABASE_URL` | `postgresql+psycopg://kakurega:kakurega_password@localhost:5432/kakurega` | SQLAlchemy URL; SQLite is also supported |
| `KAKUREGA_CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated origins allowed to call the API |
| `KAKUREGA_GOOGLE_BOOKS_API_KEY` | *(empty)* | Optional Google Books key; without one, Google's shared anonymous project is used and is often rate-limited |

Compose-only variables (root `.env`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | `kakurega` / `kakurega` / `kakurega_password` | Database credentials |
| `POSTGRES_PORT` | `5432` | Host port for PostgreSQL |
| `BACKEND_PORT` | `8000` | Host port for the API |
| `FRONTEND_PORT` | `5173` | Host port for the UI |

Frontend:

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_PROXY_TARGET` | `http://localhost:8000` (`http://backend:8000` in Compose) | Where Vite forwards `/api` and `/storage` |

**No authentication is built in.** Kakurega assumes it runs on your own machine or
a trusted private network. Do not expose it to the public internet as-is — put it
behind a reverse proxy with authentication if you need remote access.

## Database and migrations

Alembic migrations live in `backend/alembic/versions/` and are applied with:

```bash
cd backend
alembic upgrade head
```

| Revision | Adds |
| --- | --- |
| `0001_create_books` | The initial `books` table |
| `0002_relationships` | Authors, publishers, genres, tags, and join tables |
| `0003_identity_and_listing` | ISBN uniqueness, indexes, and listing fields |
| `0004_members_and_reading` | Household members and reading entries |

Handy commands:

```bash
alembic current                                  # what is applied
alembic history                                  # all revisions
alembic downgrade -1                             # step back one revision
alembic revision --autogenerate -m "add field"   # new migration from model changes
```

Migrations read `KAKUREGA_DATABASE_URL` (not `alembic.ini`), so make sure the
variable or `backend/.env` is set in the same shell before running Alembic.

Uploaded covers are written to `backend/storage/images/` and served at
`/storage/images/<file>`. The directory is git-ignored — back it up alongside the
database, and keep it on a volume in Docker (Compose already does).

## Using Kakurega

### Adding a book

1. **Add book** in the sidebar.
2. Type an ISBN or point at a barcode. Kakurega fills in the metadata it can find.
3. Adjust anything you like, add genres and tags, upload a cover.
4. Save. The book appears in **Library**.

Try these valid ISBNs:

| ISBN-13 | Book |
| --- | --- |
| `9780061054884` | *The Hobbit* |
| `9780140328721` | *Matilda* |
| `9780441172719` | *Dune* |
| `9780553380163` | *A Brief History of Time* |

ISBN lookups are the only feature that talks to the outside world. Kakurega
normalizes and checksum-validates the ISBN, queries Open Library first, and falls
back to Google Books when Open Library has no edition or returns unusable data.
Successful lookups are cached in the API process for a day.

Google Books works without a key, but anonymous traffic uses Google's shared
project, which is frequently rate-limited (HTTP 429). To use your own quota, set
`KAKUREGA_GOOGLE_BOOKS_API_KEY` and restart the API. If both providers are down or
Google's quota is exhausted, the lookup reports why and opens the blank form with
the ISBN filled in, so you can still save the book manually.

### Importing a CSV

Go to **Import**, choose a `.csv` file (up to 10 MB), and review the result:
created, updated, skipped duplicates, per-row failures, warnings, and any columns
Kakurega ignored.

Only **Title** is required. Headers are matched case-insensitively and common
aliases are accepted:

| Field | Accepted headers |
| --- | --- |
| Title (required) | `title` |
| Authors | `author`, `authors`, `author(s)` |
| ISBN-10 | `isbn`, `isbn10` |
| ISBN-13 | `isbn13` |
| Pages | `pages`, `number of pages`, `page count` |
| Publisher | `publisher` |
| Publication year | `published_year`, `published year`, `year published`, `year`, `publication year` |
| Tags | `tags`, `bookshelves` |
| Genres | `genre`, `genres` |
| Notes | `notes`, `my review`, `review` |

Rows are matched against existing books by ISBN first, then by title + authors
when no ISBN is present. By default duplicates are skipped; when the API is
called with `update_existing=true`, blank fields on the existing book are filled
in instead.

A minimal file:

```csv
Title,Author,ISBN13,Pages,Publisher,Year,Tags,Genre
Dune,Frank Herbert,9780441172719,688,Ace,1965,Sci-Fi Favourites,Science Fiction
```

### Reading and household members

- **Reading** in the sidebar has two panels: **Members** (add, rename, remove
  household readers) and **Reading activity** (every entry, filterable by member
  and status).
- On a book's page (**Library → a book**), add or update a reading entry: pick the
  member, set the status, and record the current page. Progress is calculated
  against the book's page count.
- Removing a reader removes their reading entries, not the books.
- **Tags** has its own workspace for creating, renaming, and deleting tags.
  Deleting a tag detaches it from its books (after a confirmation prompt) — the
  books themselves are untouched.

## Screenshots

| Library | Book details |
| --- | --- |
| ![Library](docs/assets/library.jpg) | ![Book details](docs/assets/details.jpg) |

## Tests

Backend (112 tests, temporary SQLite databases — no running Postgres needed):

```bash
cd backend
python -m pytest -q
```

Frontend type-check and production build:

```bash
cd frontend
npm run build
```

## Project structure

```text
Kakurega/
├── backend/
│   ├── alembic/versions/        # 0001–0004 migrations
│   ├── app/
│   │   ├── api/v1/routes/       # books, reading, members, tags, taxonomy,
│   │   │                        # import, lookup, barcode, upload, insights, health
│   │   ├── core/                # settings, database, storage, CSV parsing, ISBN
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # book, reading, importer, metadata, barcode
│   │   └── main.py              # FastAPI app factory
│   ├── storage/images/          # uploaded covers (git-ignored)
│   ├── tests/
│   ├── alembic.ini
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── public/                  # icons, manifest, logo
│   ├── src/
│   │   ├── components/          # BookForm, ReadingPanel, ProgressBar, …
│   │   ├── hooks/
│   │   ├── layouts/AppLayout.tsx
│   │   ├── pages/               # Dashboard, Library, Details, Tags, Reading,
│   │   │                        # Add book, Import, Search, Insights, Settings
│   │   ├── services/api.ts
│   │   ├── shared/              # BookCover, PageHeader, BarList, format helpers
│   │   └── styles.css           # design tokens + all component styles
│   ├── index.html
│   ├── Dockerfile
│   └── vite.config.ts
├── design/                      # original design references ("Literary Noir")
├── docs/                        # API, database, architecture, design docs
│   └── assets/                  # README screenshots
├── docker-compose.yml
└── .env.example
```

## API

Base URL: `/api/v1`. No authentication. Full reference:
[docs/API.md](docs/API.md); interactive docs: <http://localhost:8000/docs>.

| Area | Endpoints |
| --- | --- |
| Health | `GET /health` |
| Books | `GET /books`, `GET /books/{id}`, `GET /books/isbn/{isbn}`, `POST /books`, `PUT /books/{id}`, `DELETE /books/{id}` |
| Reading | `GET /reading`, `GET /books/{id}/reading`, `PUT /books/{id}/reading/{member_id}`, `DELETE /books/{id}/reading/{member_id}` |
| Members | `GET /members`, `POST /members`, `PATCH /members/{id}`, `DELETE /members/{id}` |
| Taxonomy | `GET` and `POST /authors`, `/publishers`, `/genres`, `/tags`; `PATCH` and `DELETE /tags/{id}` |
| Import | `POST /import/csv` (`?update_existing=true`) |
| Lookup | `POST /lookup` (ISBN or title/author metadata) |
| Barcode | `POST /barcode` (multipart image) |
| Upload | `POST /upload/image` (multipart image, ≤ 5 MB) |
| Insights | `GET /insights` |

`GET /books` is also the search endpoint: `q`, `genre_id`, `tag`, `year_from`,
`year_to`, `member_id`, `status`, `sort` (`title` | `added` | `year`), `limit`
(1–200), `offset`.

## App icon and branding

All brand assets live in `frontend/public/`:

| File | Used for |
| --- | --- |
| `icon.svg` | Detailed emblem — install/app icon, manifests |
| `icon-512.png`, `icon-192.png` | PWA and Android install icons |
| `apple-touch-icon.png` | iOS home-screen icon (180 px) |
| `favicon.svg` | Simplified bold mark — browser tab and sidebar brand |
| `favicon-32.png`, `favicon-48.png` | Legacy favicon fallbacks |
| `logo.svg` | Full lockup: emblem, `KAKUREGA` wordmark, `PERSONAL LIBRARY CATALOG` |
| `site.webmanifest` | Install metadata (name, theme colour, start URL) |

`frontend/index.html` links the icons and the manifest; the sidebar, generated
book covers, and README all reuse the same mark. Regenerate PNGs from the SVGs at
512 px and downscale with a good resampler (LANCZOS) rather than screenshotting at
small sizes — the thin gold lines disappear otherwise.

## Deployment notes

- Compose runs the **Vite dev server** for the frontend. It is fine for a home
  server, but for anything more exposed build the static bundle
  (`cd frontend && npm run build`) and serve `frontend/dist` from nginx, Caddy, or
  any static host, proxying `/api` and `/storage` to the backend.
- Persist `postgres_data` and `backend_storage` (or the Postgres database and
  `backend/storage/images/`) — they hold all your data.
- Back up both together: the database stores relative cover paths, not the image
  bytes.
- Set `KAKUREGA_ENVIRONMENT=production` and `KAKUREGA_DEBUG=false`, and narrow
  `KAKUREGA_CORS_ALLOWED_ORIGINS` to your real origin(s).
- Put authentication in front of the app if it is reachable by anyone else.

## Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `psycopg.OperationalError: connection refused` | PostgreSQL is not running, or the host/port in `KAKUREGA_DATABASE_URL` is wrong. Start it (`docker compose up postgres -d`) or switch to SQLite for a quick test. |
| `ModuleNotFoundError: app` when running `alembic` or `uvicorn` | Run from `backend/` with the virtual environment activated, or reinstall with `pip install -e ".[dev]"`. |
| Frontend loads but every request fails | The API is not on port 8000, or `VITE_API_PROXY_TARGET` points elsewhere. Start the backend first; restart Vite after changing the target. |
| CORS error when the frontend calls the API directly | Add the browser origin to `KAKUREGA_CORS_ALLOWED_ORIGINS` (comma-separated) and restart the API. |
| `alembic upgrade head` hits the wrong database | Alembic ignores `alembic.ini`'s URL and reads `KAKUREGA_DATABASE_URL`; export it in the same shell. Check with `alembic current`. |
| Covers upload but show as broken images | `backend/storage/images/` is missing or not mounted, or the reverse proxy is not forwarding `/storage`. |
| ISBN lookup says the Google Books quota is exhausted (HTTP 503) | Anonymous Google Books traffic uses a shared project with no guaranteed quota. Set `KAKUREGA_GOOGLE_BOOKS_API_KEY` to a key from a project with the Books API enabled and a non-zero daily quota, then restart the API. Billing alone does not raise a quota that is set to zero. Until then, add the book manually. |
| ISBN lookup returns 422 "Invalid ISBN" | The number failed its checksum or is not 10/13 digits. Re-check the printed ISBN; do not add check digits yourself. |
| ISBN lookup returns nothing (HTTP 404) | Both providers had no record. Check the ISBN, or type the details manually. |
| CSV import reports "Missing title" | The file has no `title` column (or the header row is not first). |
| Docker build fails on Windows with path errors | Ensure the repository is on the Linux filesystem or inside WSL if you use WSL-based Docker, and that Docker Desktop has the drive shared. |

## Documentation

| Doc | Contents |
| --- | --- |
| [docs/API.md](docs/API.md) | Endpoint-by-endpoint reference |
| [docs/DATABASE.md](docs/DATABASE.md) | Schema and relationships |
| [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | How the pieces fit together |
| [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) | Literary Noir tokens and components |
| [backend/README.md](backend/README.md) | Backend-specific notes |
| [frontend/README.md](frontend/README.md) | Frontend-specific notes |

---

Kakurega is a personal project; there is no license file in the repository — ask
before redistributing.
