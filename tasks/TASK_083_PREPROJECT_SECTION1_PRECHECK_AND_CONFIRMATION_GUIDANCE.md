# TASK_083_PREPROJECT_SECTION1_PRECHECK_AND_CONFIRMATION_GUIDANCE

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion.

## Goal

Run deterministic SECTION 1 precheck before Project creation and show operator-friendly blockers and warnings in the Precheck review page.

## Inputs

- `docs/intake_precheck_field_contract.md`
- User-confirmed rule:
  - Before confirming Project creation, run deterministic precheck against SECTION 1 only.
  - Exclude LAB_SECTION / laboratory estimated completion date from pre-project checks.
  - Missing SECTION 1 required fields should be shown clearly and should block confirmation.
  - `Project #` remains warning only.
  - Nonblank `Lab Test Request Number` should be auto-cleared from the draft with a warning.

## Scope

Allowed:

- Add or reuse deterministic draft-level precheck logic for intake cases.
- Surface SECTION 1 blockers and warnings in the Precheck review page.
- Highlight fields with missing or invalid values where current field metadata supports it.
- Keep backend confirmation authoritative.

Not allowed:

- Broad Precheck redesign.
- Lookup option changes.
- Parser calibration.
- Sample row editing changes.
- LTR workbook write hardening.
- Matrix, Report, AI review, LAN, permissions, or Outlook automation.

## Acceptance Criteria

- Confirmation cannot proceed when required SECTION 1 fields are missing.
- Warning-only fields are displayed as warnings and do not block confirmation.
- Lab SECTION 2 fields are excluded from pre-project blocking checks.
- Lab Test Request Number nonblank handling follows the field contract.
- Relevant backend/frontend tests pass.

## Completion Notes

- Added deterministic SECTION 1 draft precheck rules for required requestor/project fields, sample rows, requested testing, disposition, confidentiality/subcontract, and report copy recipients.
- `Project #` and nonblank `Lab Test Request Number` are warnings and do not block confirmation.
- `Lab Test Request Number` is cleared from the review draft view before Project creation.
- SECTION 2 lab fields are excluded from pre-project blockers.
- Backend confirmation now remains authoritative by rejecting Project creation when SECTION 1 precheck has error-level blockers.
- Precheck UI now shows a top issue summary and highlights fields with error or warning states.
- Fixed recipient chips were removed; `send_copies_recipients` is now a real editable field.

## Validation

- `py -m pytest tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- Result: `37 passed`
- `py -m pytest -q`
- Result: `275 passed`
- `npm run build`
- Result: passed
- `git diff --check`
- Result: passed with CRLF working-copy warnings only
- Sidebar correction: `py -m pytest tests\unit\test_frontend_shell_files.py -q`
- Result: `27 passed`; `npm run build`, result passed
