# TASK_079_LOOKUP_OPTIONS_BACKEND_AND_API

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion.

## Goal

Move Intake/Precheck lookup option values out of frontend JSX and provide a backend-managed, database-backed read API for the approved field groups.

## Inputs

- `docs/intake_precheck_field_contract.md`
- User-confirmed lookup groups:
  - Business Unit
  - Mfg. Site
  - Results Format
  - Test Type
  - Sample Status
  - Project Type
  - Disposition

## Scope

Implemented:

- SQLite persistence model for grouped lookup options.
- Repository and application service boundary.
- First-run backend default seed for empty databases.
- Read-only FastAPI endpoint for Intake/Precheck lookup groups.
- Unit and integration tests.

Not implemented:

- Frontend replacement of existing hardcoded arrays.
- Admin UI for editing lookup options.
- Parser fixes for Business Unit, Date, or Phone extraction.
- Sample row edit/copy/delete UI.

## API

`GET /api/lookups/intake-precheck`

Returns:

- `business_unit`
- `manufacturing_site`
- `results_format`
- `test_type`
- `sample_status`
- `project_type`
- `post_testing_disposition`

Each group returns ordered `{ "value": "...", "label": "..." }` options.

## Acceptance Criteria

- Lookup options are not defined only in frontend JSX.
- A fresh SQLite database can serve all required Intake/Precheck groups.
- Existing databases get the table through `init_db()`.
- API route stays thin and calls an application service.
- Tests cover default seeding and database-provided values.

## Validation

- `py -m pytest tests\unit\test_lookup_options_service.py tests\integration\test_lookup_options_api.py -q`
