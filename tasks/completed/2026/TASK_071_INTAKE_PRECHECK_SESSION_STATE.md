# TASK_071_INTAKE_PRECHECK_SESSION_STATE

## Status

done

## Goal

Keep imported Intake package state while navigating between New Project Intake and Precheck pages, and make the step navigation match the operator workflow.

## Scope

- Preserve current Intake imported email package data in the frontend session while the app remains open.
- Preserve selected attachment and selected Word application-form asset when leaving and returning to Intake.
- Make `Continue to Precheck` navigate directly to the Precheck/case-review step.
- Make Precheck back navigation return directly to Intake.
- Keep existing backend APIs unchanged.
- Add/update static frontend guard tests.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No persistent browser storage.
- No database schema change.
- No new backend API.
- No Project Folder or LTR Number implementation change.
- No Outlook inbox auto-scan, email sending, Matrix, Report, AI review, LAN deployment, permissions, or external LTR workbook mutation.

## Validation

- Frontend build.
- Static frontend guard tests.

## Completion Notes

- Lifted Intake import state from `IntakeInboxPage` into `App` session state.
- Preserved imported package, selected attachment, selected Word application-form asset, source mode, and direct Word filename across route changes while the app remains open.
- Changed `Continue to Precheck` to navigate directly to the Precheck/case-review step.
- Changed Precheck Back to return directly to Intake.
- No backend API or persistence change was added.

## Validation Result

- `npm run build` from `frontend/`: passed
- `py -m pytest tests\unit\test_frontend_shell_files.py -q`: `21 passed`
- `py -m pytest -q`: `247 passed`
- `git diff --check`: passed with line-ending warnings only
