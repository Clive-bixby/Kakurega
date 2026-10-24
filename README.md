# Kakurega

A personal home-library manager: catalog your books, scan barcodes to add them, and
browse insights about your collection.

- `backend/` — FastAPI + SQLAlchemy + Alembic + PostgreSQL
- `frontend/` — React + TypeScript + Vite

## Run with Docker

``` bash
docker compose up --build
```

This starts PostgreSQL, applies migrations (`alembic upgrade head`), the API on
<http://localhost:8000>, and the frontend on <http://localhost:5173>.

## Run locally

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md).

## Docs

- [API](docs/API.md)
- [Database](docs/DATABASE.md)
- [System architecture](docs/SYSTEM_ARCHITECTURE.md)
