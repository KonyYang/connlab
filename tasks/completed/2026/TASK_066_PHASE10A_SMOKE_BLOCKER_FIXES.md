# TASK_066_PHASE10A_SMOKE_BLOCKER_FIXES

## Status

done

## Goal

Fix the Phase 10A manual browser smoke blockers reported in `docs/archive/validation_summaries/smoken_result.md` without starting Phase 10B or adding future-scope behavior.

## Scope

- Make intake case review show draft fields returned by the backend.
- Allow operators to fill missing required intake fields before project confirmation.
- Persist operator field corrections as intake draft manual overrides.
- Keep project creation behind explicit operator confirmation.
- Prevent the project folder/evidence workflow from hard-failing when no generated folder record exists yet; show an actionable preview response instead.
- Add focused backend and frontend guard tests for the hotfix.
- Update `docs/task_board.md` after validation.

## Out Of Scope

- No copied-workbook LTR write hardening.
- No Outlook inbox auto-scan.
- No email sending.
- No Matrix, Report, AI review, LAN deployment, permissions, or external LTR workbook mutation.
- No direct frontend file, Office, project-folder, or workbook manipulation.
- No broad UI redesign beyond the smoke blocker fix.

## Design Notes

- Backend remains authoritative for confirmation blockers.
- UI calls only centralized API client functions.
- Manual field correction updates intake draft overrides, then reloads the review state.
- Missing project folder record is treated as a not-ready workflow state for evidence placement preview, not as an unrecoverable UI interruption.

## Validation

- Relevant intake review/confirmation tests.
- Relevant evidence placement tests.
- Frontend static guard test.
- Frontend build if UI changes compile successfully.

## Completion Notes

- Intake case review fields are editable and saved as manual overrides before confirmation.
- Backend confirmation remains authoritative and still requires explicit operator confirmation.
- Evidence placement preview now reports a not-ready warning when no generated folder record exists; evidence copy still requires a folder record.
- Validation:
  - `py -m pytest tests\integration\test_manual_intake_api.py tests\unit\test_intake_case_review_service.py tests\unit\test_evidence_placement_service.py tests\unit\test_frontend_shell_files.py -q` -> `30 passed`
  - `npm run build` from `frontend\` -> passed
