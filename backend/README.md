# Kakurega Backend

FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL API for Kakurega.

## Run locally

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Create the database, point the app at it, and apply migrations:

``` powershell
$env:KAKUREGA_DATABASE_URL = "postgresql+psycopg://kakurega:kakurega_password@localhost:5432/kakurega"
alembic upgrade head
uvicorn app.main:app --reload
```

Health check:

``` text
GET /api/v1/health
```

Uploaded covers are stored in `storage/images/` and served at `/storage/images/<file>`.
In production, mount that directory as a volume so images survive container rebuilds.

## Tests

``` powershell
python -m pytest -q
```
