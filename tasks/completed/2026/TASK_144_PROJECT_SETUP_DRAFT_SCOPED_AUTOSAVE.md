# TASK_144 Project Setup Draft-Scoped Autosave

## Current Phase

Phase 10C - New Project intake flow friction cleanup

## Why This Task Is Allowed

User-approved manual smoke review of `TASK_143` found that `Project setup confirmation`
is currently page-local state. It can leak across application-form switches and cannot be
restored when an existing draft is loaded.

## Scope

- Persist New Project setup confirmation values per intake case draft.
- Restore those values when switching application forms or loading an existing draft.
- Keep the final completion action using the current case-scoped setup values.
- Do not add Matrix, report, AI, permissions, or non-MVP workflow scope.

## Design

- Store setup confirmation data in `IntakeDraft.manual_overrides_json` under
  `project_setup`.
- Extend case review API responses with `project_setup`.
- Extend PATCH `/api/intake-cases/{case_id}/review-fields` to accept optional
  `project_setup`.
- Frontend New Project page will:
  - initialize setup values from `activeCase.project_setup` on case switch
  - fall back to defaults when a case has no stored setup
  - include setup values in autosave payload
  - clear stale setup values when switching to a different case

## File-Level Changes

- `backend/application/intake_case_review_service.py`
- `backend/api/routes_intake_review.py`
- `frontend/src/api/client.ts`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `tests/unit/test_frontend_shell_files.py`
- targeted backend integration/unit tests if an existing review-fields test is suitable

## Risks

- Autosave could overwrite setup values if reset and save effects race.
  - Mitigation: reset setup only on `case_id`/import reset, not on every review update.
- Existing drafts have no `project_setup`.
  - Mitigation: return `{}` and let frontend initialize defaults.
- Frozen base fields should not block pre-completion setup edits unexpectedly.
  - Mitigation: setup values are not base application fields; UI already disables after confirmed/frozen states.

## Validation

- Targeted frontend shell tests.
- Targeted review-fields API/service tests for `project_setup` persistence.
- `npm run build`.
- `git diff --check`.

## Implementation Summary

- Added `project_setup` to intake case review read models and API responses.
- Extended PATCH `/api/intake-cases/{case_id}/review-fields` to persist optional
  `project_setup` into `IntakeDraft.manual_overrides_json`.
- New Project setup values now initialize from `activeCase.project_setup` when the
  selected case changes.
- Existing autosave now includes case-scoped setup values.
- Final completion still uses the currently loaded setup values, now scoped to the
  selected draft.
- Email source display now shows only the original source filename from the
  intake package response; this stays display-only and does not expose the
  ConnLab storage path.
- Uploaded `.msg` display names now preserve the original Unicode filename
  instead of the sanitized storage filename.
- Long source filenames wrap in the Email source panel so suffixes like
  `副本` remain visible instead of being visually clipped.

## Validation Results

```powershell
py -m pytest tests\unit\test_intake_case_review_service.py::test_review_service_persists_project_setup_per_draft tests\integration\test_manual_intake_api.py::test_review_fields_persists_requested_testing_rows tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell -q
```

Result: `3 passed`.

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\integration\test_msg_package_intake_api.py::test_msg_package_import_api_persists_package_and_assets tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell -q
```

Result: `3 passed`.
