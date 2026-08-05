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

Not implemented.

Infrastructure

Not implemented.

---

# Current Modules

Frontend

- React frontend in `frontend`
- Routing configured with pages for Dashboard, Library, Add Book, Search, Insights, and Settings

Backend

- FastAPI application package in `backend/app`
- Versioned API router under `backend/app/api/v1`
- Core settings under `backend/app/core`

---

# Reusable Components

Frontend

- App layout with persistent navigation
- Shared page header

---

# Shared Services

None

---

# API Surface

- `GET /api/v1/health`

---

# Database

Tables

None

Relationships

None

---

# External Integrations

None

---

# Project Structure

Current top-level modules

frontend/

backend/

docs/

.ai/

---

# Current Architecture

Backend scaffold follows the planned FastAPI architecture from SYSTEM_ARCHITECTURE.md.

Business logic, database models, repositories, and services are not implemented yet.

Refer to SYSTEM_ARCHITECTURE.md for the planned full architecture.

---

# Feature Status

## Foundation

- [ ] Repository setup
- [x] Backend scaffold
- [x] Frontend scaffold
- [ ] Docker

## Backend

- [ ] Book CRUD
- [ ] Search
- [ ] Upload

## Frontend

- [ ] Dashboard
- [ ] Library
- [ ] Book Details
- [ ] Search

## Identification Pipeline

- [ ] Barcode
- [ ] OCR
- [ ] Metadata Lookup
- [ ] Gemini Vision

---

# Development Notes

As the project grows this file should answer questions like:

- What APIs already exist?
- Which services can be reused?
- Which components already exist?
- Which database entities exist?
- Which infrastructure is already implemented?

If the answer can be found here, the AI should not need to search the repository first.
