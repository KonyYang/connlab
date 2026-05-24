# TASK_082_PRECHECK_SAMPLE_ROW_EDIT_COPY_DELETE_UI

## Status

Done.

## Phase

Phase 10A - Intake Entry Completion.

## Goal

Make Precheck sample rows editable for real business confirmation before project creation.

## Inputs

- User-confirmed sample editing boundaries:
  - Allow editing all sample row fields.
  - Allow adding and deleting samples.
  - Whole-row Copy creates a new sample row.
  - Single-field copy is useful if feasible within scope.
  - At least one sample row must remain after delete.
- `docs/intake_precheck_field_contract.md`
- `docs/frontend_architecture_rules.md`

## Scope

Allowed:

- Replace text-only sample row rendering with editable row controls.
- Add compact icon-style edit/copy/delete row actions.
- Preserve at least one sample row.
- Persist sample row corrections through the existing draft/review update path, or add a narrowly scoped backend review update path if the current API cannot persist sample rows.
- Keep parsed rows visible and editable before project confirmation.

Not allowed:

- Broad Precheck redesign.
- Lookup option changes.
- Parser calibration.
- LTR workbook write hardening.
- Matrix, Report, AI review, LAN, permissions, or Outlook automation.

## Acceptance Criteria

- Operator can edit sample row fields before project confirmation.
- Operator can add, copy, and delete sample rows, while delete never removes the last row.
- Actions use compact icon-style buttons rather than large text buttons.
- Updated sample rows are persisted into the intake draft or review state used for project confirmation.
- Relevant frontend build and backend/frontend tests pass.

## Completion Notes

- Precheck sample rows now render as editable table inputs.
- Added compact icon action buttons for edit, copy, and delete, matching the requested simple reference style.
- Add Sample creates a blank row.
- Copy creates a new row immediately after the copied row.
- Delete is disabled when only one row remains.
- The review-fields API now accepts `sample_rows` and stores sample row corrections in draft manual overrides so project confirmation uses the corrected rows.
- Hotfix: sample columns now preserve the application-form shape by using `Part Number / Revision` as one column and `Traceability Manufacturing Lot Info` as one column instead of splitting those fields.

## Validation

- `py -m pytest tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py tests\unit\test_frontend_shell_files.py -q`
- Result: `34 passed`
- `npm run build`
- Result: passed
- Hotfix validation: `py -m pytest tests\unit\test_frontend_shell_files.py tests\unit\test_intake_case_review_service.py tests\integration\test_manual_intake_api.py -q`, result `34 passed`; `npm run build`, result passed.
