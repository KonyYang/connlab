# TASK_078_INTAKE_PRECHECK_FIELD_CONTRACT_AND_SECTION1_RULES

## Status

done

## Goal

Define the authoritative Intake/Precheck field contract and SECTION 1 project-creation policy before implementing lookup APIs, parser calibration, draft editing, or frontend UI completion.

## Why This Task Is Allowed Now

- Current board state has no active implementation task after `TASK_077`.
- The user explicitly approved `TASK_078`.
- The task is documentation and test only.
- The work stays inside MVP Intake/Precheck scope and does not activate Phase 10B.

## Inputs

- Real or sanitized sample path provided by the user:
  - `local/office files samples/E-3718_H Laboratory Test Request-Even.docx`
- User business rules:
  - SECTION 1 fields are required before Project creation.
  - `Project #` is warning-only.
  - page header `Lab Test Request Number` must be blank; if non-blank, clear draft value and warn.
  - direct `.docx` must be a no-email entry path like `.msg`.
  - lookup values must become soft-coded through backend configuration or database.
  - send-copies recipients must be confirmed.
  - sample rows must support edit/add/delete/copy and at least one row must remain.
  - New Project Precheck must run before Project creation and exclude SECTION 2 lab estimated completion date.
  - imported source `.msg` is not an attachment; email-attached `.msg` files are attachments and should show `MSG`.

## Scope

- Add `docs/intake_precheck_field_contract.md`.
- Classify fields by project confirmation, warning, auto-clear, LTR readiness, editable draft, readonly source, and SECTION 2 exclusion states.
- Define sample row edit/copy/delete rules.
- Define lookup option groups and backend soft-code policy.
- Define direct `.docx` intake policy.
- Define draft-level SECTION 1 precheck policy.
- Define source `.msg` display policy.
- Add documentation regression tests.
- Update `docs/task_board.md`.

## Out Of Scope

- No parser code changes.
- No backend API changes.
- No frontend UI changes.
- No database/schema changes.
- No lookup implementation.
- No sample edit implementation.
- No route/session hardening implementation.
- No copied-workbook LTR write hardening.
- No Outlook inbox auto-scan, email sending, Matrix, Report, AI review, LAN deployment, or permissions.

## Completion Notes

- Added `docs/intake_precheck_field_contract.md`.
- Added `tests/unit/test_intake_precheck_field_contract.py`.
- Updated `docs/task_board.md` with `TASK_078` completion and next recommended task.
- No runtime code was changed.

## Validation Result

- `py -m pytest tests\unit\test_intake_precheck_field_contract.py -q`: `2 passed`

## Stop Condition

Stop after field contract documentation, tests, and board sync. Do not proceed into lookup, parser, backend, or frontend implementation without explicit user approval.

