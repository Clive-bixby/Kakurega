# Kakurega — AI Rules

## Purpose

This document defines how AI coding agents should work on the Kakurega project.

These rules exist to keep the codebase consistent, maintainable, and predictable as the project grows.

Follow these rules unless explicitly instructed otherwise.

---

# General Principles

- Prioritize simplicity over cleverness.
- Prioritize readability over brevity.
- Write code that is easy to understand six months later.
- Prefer consistency over personal preference.
- Build only what is required for the current task.
- Avoid premature optimization.
- Avoid premature abstraction.

---

# Before Starting Any Task

Before writing code:

1. Understand the user's request.
2. Determine whether the task affects:
   - Frontend
   - Backend
   - Database
   - Architecture
   - Documentation
3. Read only the documentation relevant to that task.
4. Inspect the existing implementation before creating new files or abstractions.
5. Reuse existing code whenever possible.

Never scan the entire project unless explicitly requested.

---

# Documentation Selection

Choose documentation based on the task.

## Product Behaviour

Read:

- PRD.md
- USER_FLOW.md

---

## Frontend

Read:

- DESIGN_SYSTEM.md
- COMPONENTS.md
- WIREFRAMES.md

---

## Backend

Read:

- API.md
- DATABASE.md

---

## Architecture

Read:

- SYSTEM_ARCHITECTURE.md

---

## Future Planning

Read:

- FUTURE.md

Do not read unrelated documentation.

---

# Coding Style

## General

- Keep functions focused on one responsibility.
- Prefer explicit code over hidden behaviour.
- Use meaningful names.
- Keep files reasonably small.
- Remove dead code.
- Avoid unnecessary comments.
- Let code be self-explanatory where possible.

---

## Reuse

Before creating:

- component
- service
- utility
- hook
- repository

always check whether an equivalent already exists.

Avoid duplicate implementations.

---

# Backend Rules

- Routes should remain thin.
- Business logic belongs in services.
- Database access belongs in repositories.
- Validate input before processing.
- Handle errors explicitly.
- Never expose internal implementation details through the API.
- Keep endpoints RESTful unless instructed otherwise.

---

# Frontend Rules

- Build reusable components.
- Keep components focused.
- Separate presentation from business logic.
- Avoid deeply nested component trees.
- Prefer composition over inheritance.
- Avoid unnecessary prop drilling.
- Keep UI responsive and accessible.

---

# Database Rules

- Follow the documented schema.
- Do not duplicate data unnecessarily.
- Preserve referential integrity.
- Prefer migrations over manual schema changes.
- Never modify historical migrations.

---

# Documentation Rules

Documentation is the project's source of truth.

If implementation requires changing documentation:

Do not silently modify it.

Instead:

- explain why
- recommend the change
- update documentation only after approval

---

# Finishing a Task

Before considering work complete:

- Ensure the implementation matches the requested scope.
- Remove temporary or unused code.
- Verify consistency with the existing codebase.
- Update memory.md if stable project knowledge has changed.
- Update architecture.md if the implemented architecture has changed.

Do not update memory.md for temporary information.

---

# What Belongs in memory.md

Update memory.md only when stable project knowledge changes.

Examples:

✓ New reusable component

✓ New service

✓ New API endpoint

✓ New database table

✓ New architectural decision

Do not store:

✗ Temporary TODOs

✗ Debug notes

✗ One-time implementation details

✗ Task progress

---

# Communication

If requirements are unclear:

Ask before implementing.

If documentation conflicts with implementation:

Explain the conflict.

Do not guess.

If a significantly better solution exists:

Recommend it first.

Do not replace the requested solution without approval.

---

# Final Principle

The goal is not simply to make the current feature work.

The goal is to leave Kakurega cleaner, more maintainable, and easier to extend after every completed task.
