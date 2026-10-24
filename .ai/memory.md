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

Backend and frontend MVP flows are implemented. Identification pipeline has upload, barcode detection, and metadata lookup; OCR and Gemini Vision remain.

---

# Core Decisions

This section records important project decisions that future work should respect.

Example format:

Decision:
Reason:
Alternative considered:

Only add decisions that are unlikely to change frequently.

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
- Route dependencies use `request.app.state.session_factory` for database sessions.
- Business logic lives in services; database access lives in repositories.
- Pydantic schemas live under `backend/app/schemas`.

Frontend

- React routing is centralized in `frontend/src/App.tsx`.
- The primary application shell lives in `frontend/src/layouts/AppLayout.tsx`.
- API calls are centralized in `frontend/src/services/api.ts`.
- Data fetching uses small hooks such as `useBooks`.

---

# Shared Building Blocks

Maintain a high-level index of important reusable parts of the application.

Examples:

Frontend

- `AppLayout` provides the persistent app navigation.
- `PageHeader` provides the basic page title header.

Common hooks

- `useBooks` fetches and exposes book list state.

Backend

Shared services

- `BookService` handles book CRUD.
- Metadata lookup service queries Open Library and Google Books.
- Barcode decoding service extracts ISBNs.

Repositories

- `BookRepository` manages books and relationships.

Utilities

- `create_app()` builds the FastAPI application and lifespan.

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
