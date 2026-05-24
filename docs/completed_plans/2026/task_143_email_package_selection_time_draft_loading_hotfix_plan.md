# TASK_143 Email Package Selection-Time Draft Loading Hotfix Plan

## Current Phase And Task

- Phase: `Phase 10C - New Project intake flow friction cleanup`
- Task: `TASK_143_EMAIL_PACKAGE_SELECTION_TIME_DRAFT_LOADING_HOTFIX`
- Status: complete

## Scope

Fix the manual smoke issue where duplicate draft resolution appears immediately after email import. The corrected flow is:

1. Import `.msg`.
2. Show source and attachments only.
3. Wait for the operator to select an application form.
4. Load a new selected form directly into right-side `Application information`.
5. If the selected form already has an unconfirmed draft, show a simplified duplicate card.
6. After `Open existing draft` or `Replace existing draft`, load the resolved draft into right-side `Application information`.

## File-Level Plan

- `frontend/src/pages/IntakeInboxPage.tsx`: gate automatic draft preparation after email import, keep selection-time draft loading as the main path, and ensure duplicate resolution calls the same right-side editor loading path.
- `frontend/src/features/intake/IntakeSourcePanel.tsx`: remove duplicate resolution rendering from the Email source panel.
- `frontend/src/features/intake/*`: add a compact selection-context duplicate component if needed.
- `frontend/src/intake-inbox.css`: adjust compact duplicate card styling.
- `tests/unit/test_frontend_shell_files.py`: add static guards for simplified copy and component placement.

## Out Of Scope

- No backend contract change unless verification proves the frontend cannot use the existing selection-time API.
- No Outlook inbox auto-scan.
- No email sending.
- No future-scope features.
- No modal redesign.
- No `Create separate draft` action in this hotfix.

## Acceptance

- `.msg` import alone does not show `This application draft already exists`.
- Selecting a new form loads `Application information`.
- Selecting a duplicate form shows only the simplified two-button card.
- Both duplicate actions load `Application information`.
- Direct Word upload still works.

## Validation

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"
cd frontend
npm run build
git diff --check
```

Manual smoke follows the 10-step checklist in `tasks/TASK_143_EMAIL_PACKAGE_SELECTION_TIME_DRAFT_LOADING_HOTFIX.md`.

## Completion Notes

- Email import no longer auto-selects the first attachment.
- Email packages with selectable Word forms wait for explicit form selection before draft preparation.
- Duplicate resolution is rendered from the Attachments selection context, not the Email source summary.
- The duplicate card no longer shows application/email/size comparison rows and no longer exposes `Create separate draft`.
- Successful new selection, open existing, and replace existing paths all load the right-side `Application information` editor.
- Follow-up manual-smoke fix: resolved duplicate drafts with an existing selected case reload review data directly, avoiding a second blank-draft preparation pass that cleared the right-side editor.

## Validation Results

- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "duplicate or msg_package or application_form_import"`: `3 passed, 52 deselected`
- `py -m pytest tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q`: `1 passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py::test_task142_draft_duplicate_resolution_is_business_readable tests\unit\test_frontend_shell_files.py::test_task143_email_import_waits_for_application_form_selection -q`: `2 passed`
- `npm run build` from `frontend`: passed
- `git diff --check`: passed with LF/CRLF working-copy warnings only
