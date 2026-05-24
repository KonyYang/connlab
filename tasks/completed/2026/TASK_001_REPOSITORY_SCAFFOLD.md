# TASK 001 — Repository Scaffold

## Goal

Create the initial ConnLab repository structure and minimal backend package skeleton.

## Scope

Create directories and placeholder files only. Do not implement business features.

## Required Structure

```text
backend/
  domain/
  application/
  infrastructure/
    storage/
    office/
    files/
  modules/
    intake/
    precheck/
    ltr/
    folder/
  api/
  shared/
frontend/
apps/desktop/
tests/
  unit/
  integration/
config/
data/
templates/
logs/
```

## Required Files

- `pyproject.toml` or `requirements.txt` with minimal backend dependencies.
- `backend/__init__.py` and package init files.
- `backend/api/main.py` with a minimal FastAPI app and `/health` route.
- `tests/unit/test_health.py` or equivalent API smoke test.
- `.gitignore` for Python, Node, SQLite, logs, generated projects.

## Out of Scope

- No database schema.
- No project creation logic.
- No UI implementation beyond placeholder.
- No Office handling.

## Acceptance Criteria

- FastAPI app can be imported.
- `/health` returns status OK.
- Tests pass.
- Directory layout matches architecture.
