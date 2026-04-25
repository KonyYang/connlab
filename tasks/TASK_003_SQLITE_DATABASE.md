# TASK 003 — SQLite Database Foundation

## Goal

Create the SQLite persistence foundation.

## Scope

Set up SQLAlchemy engine/session and initial migrations or table creation helper.

## Requirements

- Add `backend/infrastructure/storage/database.py`.
- Use SQLite path from settings.
- Provide session factory.
- Provide `init_db()` function.
- Add base model definition.
- Add tests using temporary SQLite file or in-memory database.

## Out of Scope

- Do not define all tables yet except a minimal placeholder if required.
- Do not implement repositories yet.

## Acceptance Criteria

- Tests can create and dispose a database.
- Database location is configurable.
