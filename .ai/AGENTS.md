# AGENTS.md

# Kakurega

Welcome to the Kakurega project.

This repository contains AI-specific guidance to help maintain consistency across development sessions.

## Startup Procedure

Before making any changes, read the following files in order:

1. `.ai/context.md`
2. `.ai/rules.md`
3. `.ai/memory.md`
4. `.ai/state.md`

These files define:

- project philosophy
- coding workflow
- long-term project knowledge
- current implementation state

## Documentation

The `/docs` directory contains the project's planning documents and is the source of truth for the intended design.

Do **not** read the entire documentation by default.

Instead, determine which documents are relevant to the current task.

Typical mapping:

### Product Behaviour

- `docs/PRD.md`
- `docs/USER_FLOW.md`

### Frontend

- `docs/DESIGN_SYSTEM.md`
- `docs/COMPONENTS.md`
- `docs/WIREFRAMES.md`

### Backend

- `docs/API.md`
- `docs/DATABASE.md`

### Architecture

- `docs/SYSTEM_ARCHITECTURE.md`

### Future Planning

- `docs/FUTURE.md`

Only load the documentation required for the current task.

## After Completing Work

If the implementation introduces stable project knowledge:

- Update `.ai/memory.md`

If the implementation changes the current project structure, architecture, reusable components, APIs, services, or database:

- Update `.ai/state.md`

Do not update AI documentation for temporary work, experiments, debugging, or incomplete features.

## General Expectations

- Keep implementations simple.
- Reuse existing code whenever possible.
- Follow the established project architecture.
- Avoid unnecessary abstractions.
- Ask for clarification instead of making architectural assumptions.

## Priority Order

When making decisions, follow this priority:

1. User instructions
2. Existing implementation
3. AI guidance (.ai/)
4. Project documentation (/docs)

If these sources conflict, explain the conflict before making changes.
