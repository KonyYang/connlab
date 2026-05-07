# TASK_127_LOOKUP_OPTIONS_SAFE_UPDATE_AND_IMPORT

## Status

done

## Purpose

Move New Project setup confirmation lookup values into the existing database-backed lookup option mechanism, and add a safe operator-controlled import path for local lookup configuration.

## Scope

- Add lookup groups for New Project setup confirmation:
  - `project_setup_location`
  - `project_setup_test_type_in_sheet`
- Keep built-in default values for first-run databases and existing databases.
- Return setup confirmation options from the backend lookup service instead of route-level constants.
- Keep the frontend loading setup options through the existing API.
- Support importing lookup options from a local TOML configuration file.
- Automatically back up the SQLite database before importing lookup options.
- Do not delete old options during import. Existing options may only be active or disabled.

## Out Of Scope

- No full lookup management UI.
- No copied/external LTR workbook write.
- No Matrix, Report, AI review, Outlook auto-scan, email sending, LAN, or permissions.

## Configuration Format

```toml
[lookup_options]
project_setup_location = [
  "AIPG Guangzhou",
  { value = "Nantong Lab", label = "Nantong Lab", active = true, sort_order = 20 },
]
project_setup_test_type_in_sheet = [
  "Qualification",
  { value = "ORT", active = false },
]
```

## Validation

Required:

```powershell
py -m pytest tests\unit\test_lookup_options_service.py tests\integration\test_lookup_options_api.py tests\integration\test_new_project_completion_api.py -q
npm run build
```

Completed:

- `py -m pytest tests\unit\test_lookup_options_service.py tests\integration\test_lookup_options_api.py tests\integration\test_new_project_completion_api.py -q`, result `9 passed`.
- `py -m pytest tests\unit tests\integration -q`, result `350 passed`.
- `npm run build`, result passed from `frontend`.

## Stop Rule

Stop after implementation and update `docs/task_board.md`.
