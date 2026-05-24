# TASK 005 — Database Models and Repositories

## Goal

Persist MVP domain objects to SQLite.

## Scope

Create SQLAlchemy models and repository classes for:

- Project
- ApplicationForm
- SampleInfo
- PrecheckResult
- PrecheckIssue
- LtrRecord
- ProjectFolderRecord
- FileAsset

## Requirements

- Add database models under `backend/infrastructure/storage/models.py` or split files.
- Add repositories under `backend/infrastructure/storage/repositories/`.
- Repositories must return domain objects or DTOs, not raw SQLAlchemy models.
- Include create/get/list/update operations where needed for MVP.

## Tests

- Repository tests using temp SQLite.
- Create and retrieve Project.
- Store ApplicationForm with SampleInfo rows.
- Store PrecheckResult with issues.

## Out of Scope

- No API routes.
- No UI.
- No application form parser.

## Acceptance Criteria

- `init_db()` creates required tables.
- Basic persistence tests pass.
