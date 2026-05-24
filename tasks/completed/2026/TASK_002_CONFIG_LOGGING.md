# TASK 002 — Configuration and Logging

## Goal

Add basic configuration and logging infrastructure.

## Scope

Implement app settings and logger setup.

## Requirements

- Add `backend/shared/config.py`.
- Add `backend/shared/logging.py`.
- Read settings from environment variables with sensible defaults:
  - `CONNLAB_DATA_DIR`
  - `CONNLAB_PROJECTS_DIR`
  - `CONNLAB_TEMPLATES_DIR`
  - `CONNLAB_LOG_LEVEL`
- Default to local folders: `data/`, `projects/`, `templates/`.
- Ensure folders can be created if missing.
- Add tests for default settings.

## Out of Scope

- No GUI settings page.
- No advanced config file editor.

## Acceptance Criteria

- Settings object loads defaults.
- Logger can be initialized without side effects.
- Tests cover default paths.
