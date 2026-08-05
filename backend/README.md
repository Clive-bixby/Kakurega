# Kakurega Backend

FastAPI backend scaffold for Kakurega.

## Run locally

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Health check:

``` text
GET /api/v1/health
```
