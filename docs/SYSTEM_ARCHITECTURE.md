# SYSTEM_ARCHITECTURE.md

# Book Catalog --- System Architecture

**Version:** 1.0\
**Status:** Draft

------------------------------------------------------------------------

## 1. Overview

Book Catalog is a full-stack web application for cataloging and managing
physical book collections with minimal manual effort.

The application identifies books using barcode detection, OCR, public
book metadata APIs, and AI vision as a fallback.

The first release targets a single user but is designed to support
future family accounts without major architectural changes.

------------------------------------------------------------------------

## 2. Goals

-   Modular
-   Maintainable
-   Docker-friendly
-   Cloud-ready
-   Low-cost
-   API-first
-   Scalable
-   Easy to understand

------------------------------------------------------------------------

## 3. High-Level Architecture

``` text
React Frontend
      │
 REST API
      ▼
FastAPI Backend
      │
 ┌────┼───────────────┐
 │    │               │
 ▼    ▼               ▼
PostgreSQL      Local Storage    External Services
 Database        Images                │
                                       ├── Open Library
                                       ├── Google Books
                                       └── Gemini Vision
```

------------------------------------------------------------------------

## 4. Technology Stack

### Frontend

-   React
-   Vite
-   TypeScript
-   Plain CSS (`styles.css`), not Tailwind
-   React Router

### Backend

-   FastAPI
-   SQLAlchemy
-   Alembic
-   Pydantic
-   httpx
-   python-multipart
-   zxing-cpp
-   Pillow

### Database

-   PostgreSQL
-   SQLite for tests

### Containerization

-   Docker
-   Docker Compose

### Image Storage

Initially local filesystem:

``` text
backend/storage/images/
```

Served by the API at `/storage/images/<file>` (`StaticFiles` mount). Docker
Compose keeps it in the `backend_storage` named volume.

Future: - AWS S3 - Google Cloud Storage

------------------------------------------------------------------------

## 5. Backend Architecture

``` text
backend/
└── app/
    ├── api/
    ├── core/
    ├── models/
    ├── repositories/
    ├── schemas/
    ├── services/
    ├── utils/
    ├── workers/
    └── tests/
```

### Responsibilities

-   **api/** → Request/response handling
-   **services/** → Business logic
-   **repositories/** → Database access
-   **models/** → SQLAlchemy models
-   **schemas/** → Pydantic DTOs
-   **workers/** → Background tasks

------------------------------------------------------------------------

## 6. Frontend Architecture

``` text
frontend/
├── assets/
├── components/
├── contexts/
├── hooks/
├── layouts/
├── pages/
├── services/
├── types/
└── utils/
```

Main pages: - Dashboard - Library - Book Details - Add Book - Insights -
Search - Settings

------------------------------------------------------------------------

## 7. Book Identification Pipeline

``` text
Upload Image
      │
      ▼
Barcode Detection
      │
      ├── Found
      │      ▼
      │ Metadata Lookup
      │      ▼
      │ Save Book
      │
      └── Not Found
             ▼
            OCR
             ▼
      Metadata Lookup
             │
      ├── Found
      │      ▼
      │ Save Book
      │
      └── Not Found
             ▼
        Gemini Vision
             ▼
      Review Metadata
             ▼
          Save Book
```

------------------------------------------------------------------------

## 8. External Services

### Open Library

Primary metadata source.

### Google Books

Secondary metadata source.

### Gemini Vision

Fallback when metadata cannot be identified.

### Barcode Decoding

Uses zxing-cpp with Pillow for local image decoding.

------------------------------------------------------------------------

## 9. Search

Current: - Case-insensitive `ILIKE` matching in `GET /books?q=...`

Fields: - Title - Subtitle - ISBN - Description - Author - Publisher

`Genres` and `Notes` are not searched yet; genre is a filter
(`?genre_id=`). `%`, `_`, and `\` are treated literally. Paginated 50 rows at a
time by default.

Future: - Vector embeddings - Semantic search

------------------------------------------------------------------------

## 10. Recommendations

### Version 1

-   Same author
-   Same genre
-   Same series

### Future

-   Embedding-based similarity
-   Hybrid recommendation engine

------------------------------------------------------------------------

## 11. Analytics

Generated entirely from local database data.

Examples: - Books read - Reading trends - Favorite genres - Publication
timeline - Books added

------------------------------------------------------------------------

## 12. Deployment

Development:

``` text
Docker Compose

Frontend
Backend
PostgreSQL
```

Future:

``` text
React
  │
Cloud CDN
  │
FastAPI Container
  │
PostgreSQL
  │
Object Storage
```

------------------------------------------------------------------------

## 13. Security

Current: - No authentication

Future: - JWT authentication - Private image storage - Environment
variables for secrets

------------------------------------------------------------------------

## 14. Design Principles

-   Backend is the single source of truth.
-   Frontend never calls external metadata APIs directly.
-   Business logic belongs in services.
-   Database access belongs in repositories.
-   Keep AI usage minimal by using barcode and OCR first.
-   Build for extensibility without unnecessary complexity.

------------------------------------------------------------------------

## 15. Future Evolution

-   Family accounts
-   Mobile application
-   Redis cache
-   Background workers
-   AI recommendations
-   Vector search
-   Cloud deployment
-   Book lending
-   Notifications
