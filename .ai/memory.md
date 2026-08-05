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

Building a clean and maintainable foundation before adding advanced features.

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

Frontend

- React routing is centralized in `frontend/src/App.tsx`.
- The primary application shell lives in `frontend/src/layouts/AppLayout.tsx`.

---

# Shared Building Blocks

Maintain a high-level index of important reusable parts of the application.

Examples:

Frontend

- `AppLayout` provides the persistent app navigation.
- `PageHeader` provides the basic page title header.

Common hooks

Backend

Shared services

Repositories

Utilities

Infrastructure

Do not list every file.

Only list reusable building blocks that future features should discover instead of recreating.

---

# External Integrations

Track important third-party integrations.

For each integration record:

Purpose

Current usage

Known limitations

This prevents duplicate integrations being introduced later.

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
