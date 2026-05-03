# TASK_086_DIRECT_WORD_APPLICATION_FORM_UPLOAD_WIRING

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion follow-up.

## Goal

Wire the New Project Intake `Upload application form` action to the existing direct Word intake backend path so a `.docx` or `.doc` file can create an intake package, asset, and review draft without email.

## Scope

Allowed:

- Add a direct Word upload API endpoint backed by `DirectWordIntakeService`.
- Add a frontend API client function for direct Word upload.
- Update `IntakeInboxPage` so `Upload application form` calls the backend and updates the current Intake session.
- Keep the existing selected-form to Precheck flow.
- Add/update API and frontend static tests.

Not allowed:

- Intake information density redesign.
- Attachment list redesign.
- Attachment preview expansion.
- Workflow shell redesign.
- Backend parser changes.
- LTR workbook write hardening.
- Matrix, Report, AI review, LAN, permissions, Outlook inbox automation, or email sending.

## Acceptance Criteria

- Direct `.docx` upload creates a package and application-form candidate asset.
- Frontend direct Word action no longer shows the "not wired" placeholder error.
- Imported direct Word package can continue through the existing selected form path.
- `npm run build` and relevant tests pass.

## Completion Notes

- Added `POST /api/intake-packages/import-docx`, returning the shared `IntakePackageImportResponse`.
- The API preserves the uploaded file name while using a temporary file boundary before controlled intake storage copies the source.
- Added `importDirectWordApplicationForm(file)` to the frontend API client.
- `Upload application form` now imports direct Word files, updates Intake session state, and selects the returned Word asset.

## Validation

- `py -m pytest tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- Result: `32 passed`
- `npm run build`
- Result: passed
- `py -m pytest -q`
- Result: `278 passed`
- `git diff --check`
- Result: passed with CRLF working-copy warnings only
