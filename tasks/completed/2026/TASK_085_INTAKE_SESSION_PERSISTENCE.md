# TASK_085_INTAKE_SESSION_PERSISTENCE

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion follow-up.

## Goal

Persist the current New Project Intake session through browser refresh using `sessionStorage`, without adding frontend dependencies or changing business behavior.

## Inputs

- `docs/archive/historical_plans/connlab_deep_evaluation_and_session_persistence_plan.md`
- Current `frontend/src/App.tsx`
- Current `frontend/src/pages/IntakeInboxPage.tsx`
- Current `frontend/src/pages/IntakeCaseReviewPage.tsx`

## Scope

Allowed:

- Move Intake session type/default state to a small feature boundary if needed.
- Add `sessionStorage` load/save/clear helpers.
- Initialize App-level Intake session from `sessionStorage`.
- Keep App-level session synchronized to `sessionStorage`.
- Clear the Intake session after successful Project confirmation.
- Add/update frontend static tests for persistence wiring.

Not allowed:

- New dependencies such as React Router, Zustand, Redux, Vitest, or testing-library.
- New business behavior.
- Backend API changes.
- Parser changes.
- Lookup storage changes.
- LTR workbook write hardening.
- Matrix, Report, AI review, LAN, permissions, Outlook inbox automation, or email sending.

## Acceptance Criteria

- Refreshing the browser can restore the current Intake session from `sessionStorage`.
- Importing a new `.msg` or direct `.docx` continues to replace the previous Intake session.
- Successful Project confirmation clears the persisted Intake session.
- Session persistence failure falls back safely to an empty session.
- `npm run build` and relevant frontend tests pass.

## Completion Notes

- Intake session type, empty state, and persistence helpers now live in `frontend/src/features/intake/intakeSession.ts`.
- `App.tsx` initializes Intake session from `sessionStorage` and synchronizes changes back to `sessionStorage`.
- Empty sessions remove the stored key, so new empty workflows do not leave stale state behind.
- Successful Project confirmation clears the persisted Intake session and resets App-level Intake state.
- No new frontend dependencies were added.

## Hotfix Notes

- Precheck `Back to Intake` now passes the active review case id and selected Word form asset id back to `App.tsx`.
- `App.tsx` merges that back-navigation snapshot into the App-level Intake session before navigating to `/intake`.
- Returning from Precheck to Intake now preserves the selected application form row, Continue eligibility, and selected precheck case binding.

## Validation

- `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- Result: `29 passed`
- `npm run build`
- Result: passed
- `py -m pytest -q`
- Result: `282 passed`
- `git diff --check`
- Result: passed with CRLF working-copy warnings only
