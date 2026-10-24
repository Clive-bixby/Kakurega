# Kakurega — Project State

## Purpose

This document provides a concise snapshot of the current implementation of Kakurega.

It exists so AI coding agents can quickly understand what has already been built without scanning the entire repository.

Unlike the documentation in `/docs`, this file reflects the **current implementation**, not the planned design.

Keep this document concise and up to date.

---

# Update Policy

Update this document whenever the implementation changes in a meaningful way.

Examples:

- New module
- New service
- New API
- New reusable component
- New database entity
- New infrastructure
- Major refactor

Do not update this file for:

- Bug fixes
- Small refactors
- Formatting changes
- Documentation changes
- Temporary experiments

Replace outdated information instead of appending duplicates.

---

# Technology Stack

Frontend

React + Vite + TypeScript scaffold implemented.

Backend

FastAPI scaffold implemented.

Database

PostgreSQL in Docker Compose; SQLite for tests.

Infrastructure

Docker Compose for PostgreSQL, backend, and frontend. Local image storage under `backend/storage/images`.

---

# Current Modules

Frontend

- React frontend in `frontend`
- Routing configured with pages for Dashboard, Library, Add Book, Book Details, Search, Insights, and Settings
- API client in `frontend/src/services/api.ts`
- Data fetching hook in `frontend/src/hooks/useBooks.ts`

Backend

- FastAPI application package in `backend/app`
- Versioned API router under `backend/app/api/v1`
- Core settings and database session factory under `backend/app/core`
- SQLAlchemy models and associations under `backend/app/models`
- Book repository under `backend/app/repositories`
- Book, metadata, and barcode services under `backend/app/services`
- Alembic migrations under `backend/alembic/versions`

---

# Reusable Components

Frontend

- App layout with persistent navigation
- Shared page header
- `useBooks` hook

Backend

- `create_app()` in `backend/app/main.py`
- `BookRepository`
- `BookService`
- Metadata lookup service
- Barcode decoding service

---

# Shared Services

Backend

- `BookService` handles book CRUD.
- Metadata lookup queries Open Library, then Google Books.
- Barcode decoding uses `zxing-cpp`.

Frontend

- `api.ts` contains typed API client functions.

---

# API Surface

- `GET /api/v1/health`
- `GET /api/v1/books`
- `GET /api/v1/books/{id}`
- `POST /api/v1/books`
- `PUT /api/v1/books/{id}`
- `DELETE /api/v1/books/{id}`
- `GET /api/v1/search?q=...`
- `GET /api/v1/insights`
- `POST /api/v1/upload/image`
- `POST /api/v1/lookup`
- `POST /api/v1/barcode`

---

# Database

Tables

- `authors`
- `books`
- `publishers`
- `genres`
- `book_authors`
- `book_genres`

Relationships

- `books.publisher_id` -> `publishers.id`
- `book_authors` links books and authors
- `book_genres` links books and genres

Migrations

- `0001_create_books`
- `0002_relationships`

---

# External Integrations

- Open Library for metadata lookup
- Google Books for metadata fallback
- `zxing-cpp` for barcode decoding
- Local filesystem for uploaded images

---

# Project Structure

Current top-level modules

frontend/

backend/

docs/

.ai/

---

# Current Architecture

Backend follows the planned FastAPI architecture and implements models, repositories, services, schemas, migrations, and tests.

Frontend implements routing, layout, API client, and wired pages for Dashboard, Library, Add Book, Book Details, and Search.

---

# Feature Status

## Foundation

- [x] Repository setup
- [x] Backend scaffold
- [x] Frontend scaffold
- [x] Docker

## Backend

- [x] Book CRUD
- [x] Author, Publisher, and Genre relationships
- [x] Search
- [x] Upload
- [x] Barcode
- [x] Metadata Lookup
- [ ] OCR
- [ ] Gemini Vision

## Frontend

- [x] Dashboard
- [x] Library
- [x] Book Details
- [x] Search
- [x] Add Book
- [ ] Insights
- [ ] Settings

## Identification Pipeline

- [x] Barcode
- [ ] OCR
- [x] Metadata Lookup
- [ ] Gemini Vision

---

# Development Notes

Backend tests use a temporary SQLite database and `Base.metadata.create_all`.

Frontend build uses TypeScript and Vite.
