# Kakurega — AI Context

## Purpose

Kakurega is a personal library management application built as a long-term learning project.

The primary objective is not only to build a useful application, but also to learn modern software engineering practices by designing and implementing the system from scratch.

The application should remain simple, maintainable, and enjoyable to work on as it grows.

---

# Project Philosophy

Every implementation should optimize for:

1. Simplicity
2. Readability
3. Maintainability
4. Reusability
5. Incremental learning

Prefer straightforward solutions over clever ones.

Avoid introducing complexity unless it solves an actual problem.

---

# Development Philosophy

This project is developed incrementally.

Features should be implemented one at a time.

Do not build infrastructure for future features unless it provides immediate value.

Prefer evolving the architecture through refactoring rather than premature abstraction.

---

# Source of Truth

The `/docs` directory contains the project's planning and design documents.

These documents describe the intended behaviour of the application.

The implementation may temporarily differ while development is in progress.

If implementation and documentation disagree:

- Never assume which one is correct.
- Ask for clarification before making architectural changes.
- Do not silently rewrite code or documentation.

---

# Documentation Usage

Do not read every document for every task.

Read only the documentation relevant to the current request.

Examples:

Backend work
→ API
→ Database

Frontend work
→ Design System
→ Components
→ Wireframes

Feature behaviour
→ PRD
→ User Flow

Architecture changes
→ System Architecture

Future planning
→ Future

Avoid loading unrelated documentation.

---

# Scope

Current focus:

Build a complete MVP.

Current priorities include:

- clean architecture
- reusable components
- reliable backend
- learning best practices

Out of scope until explicitly requested:

- authentication
- cloud deployment
- mobile application
- family accounts
- AI recommendations
- performance optimization
- microservices

---

# Expectations

Before implementing anything:

Understand the request.

Determine which documentation is required.

Reuse existing code whenever possible.

Keep implementations consistent with the existing architecture.

Avoid unnecessary dependencies.

Avoid unnecessary abstractions.

---

# Communication

If requirements are ambiguous:

Ask before making assumptions.

If an implementation requires deviating from the documented architecture:

Explain why before making the change.

If a better design is discovered:

Recommend it, but do not implement it without approval.

---

# Long-Term Goal

Kakurega should gradually evolve into a polished, maintainable, production-quality application while remaining understandable to a single developer.

Every completed feature should leave the project cleaner than before.
