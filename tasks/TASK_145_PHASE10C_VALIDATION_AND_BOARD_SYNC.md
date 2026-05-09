# TASK_145 Phase 10C Validation and Board Sync

## Status

done

## Current Phase

Phase 10C - New Project intake flow friction cleanup

## Why This Task Is Allowed

`TASK_144_PROJECT_SETUP_DRAFT_SCOPED_AUTOSAVE` is complete, and the user has
completed manual smoke testing for the Phase 10C New Project intake flow.
The task board currently has no active implementation task and requires the
next controlled task to be explicitly approved before moving on.

This task is a validation and documentation closeout task. It does not add
new product behavior.

## Goal

Close Phase 10C by recording the tested New Project intake behavior, syncing
the task board, and making the next phase decision explicit.

## Scope

- Summarize Phase 10C completed tasks from `TASK_140` through `TASK_144`.
- Record the user-completed manual smoke result as the Phase 10C manual
  validation outcome.
- Run targeted automated validation for the current intake and New Project
  creation surface.
- Update `docs/task_board.md` with:
  - Phase 10C completion status
  - validation summary
  - current active task status
  - next recommended phase or task
- Keep all changes limited to validation, documentation, and task-board sync
  unless validation reveals a blocking regression.

## Out Of Scope

- No new product behavior.
- No Outlook inbox auto-scan.
- No email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or future-scope
  workflow.
- No refactor outside validation/documentation unless a blocking regression
  is found and explicitly approved.

## Proposed Validation

Run:

```powershell
py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py tests\unit\test_frontend_shell_files.py -q -k "msg or intake or task102 or task103 or task142 or task143 or task144 or project_setup"
```

Run:

```powershell
cd frontend
npm run build
```

Run:

```powershell
git diff --check
```

If the targeted pytest selector is too broad or includes unrelated historical
failures, narrow to the directly relevant tests and record the reason in the
task board.

## Stop Rule

Stop after the Phase 10C validation and board sync are complete. Do not start
the next phase or any later task in the same turn.

## Implementation Summary

- Recorded Phase 10C manual smoke testing as user-completed validation.
- Ran targeted automated validation for `.msg` intake, package detail,
  manual intake, case review, project setup persistence, duplicate draft
  resolution, and New Project frontend shell checks.
- Confirmed frontend production build still passes.
- Confirmed `git diff --check` passes with LF/CRLF working-copy warnings only.
- Updated `docs/task_board.md` to close Phase 10C and return the active task
  to none pending the next explicit phase/task approval.

## Validation Results

Initial broad selector:

```powershell
py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py tests\unit\test_frontend_shell_files.py -q -k "msg or intake or task102 or task103 or task142 or task143 or task144 or project_setup"
```

Result: `68 passed, 34 deselected, 3 failed`.

The 3 failures were historical frontend shell expectations from older
TASK_069/TASK_087/TASK_091 checks pulled in by the broad `-k` selector. They
were not Phase 10C regressions. The validation was narrowed as planned.

Backend/intake validation:

```powershell
py -m pytest tests\unit\test_outlook_msg_source_import.py tests\integration\test_msg_package_intake_api.py tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py -q
```

Result: `50 passed`.

Phase 10C frontend static validation:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py::test_task102_new_project_single_page_editor_shell tests\unit\test_frontend_shell_files.py::test_task103_application_form_import_is_explicit_and_confirmed tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q
```

Result: `4 passed`.

Frontend build:

```powershell
cd frontend
npm run build
```

Result: passed.

Diff hygiene:

```powershell
git diff --check
```

Result: passed with LF/CRLF working-copy warnings only.
