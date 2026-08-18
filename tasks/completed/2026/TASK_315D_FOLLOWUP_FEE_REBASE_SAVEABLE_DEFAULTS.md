# TASK_315D Follow-up: Fee Rebase Saveable Defaults

Status: Complete.

## Goal

Close the regression where Matrix-to-Fee rebase/promotion can create Fee pricing draft rows with unsaveable placeholder values, causing Fee autosave/Confirm Fee to fail and making previously entered Notes or fee statistics appear lost after Matrix changes.

## User-Reproduced Symptom

1. Add Notes in Fee Evaluation.
2. Confirm Fee.
3. Reopen Matrix Editor and add/update Matrix content.
4. Return to Fee Evaluation.
5. Fee autosave shows a `unit_type` validation error or Confirm Fee shows `testing_fee_total must be numeric`, and the pricing edit/statistics state appears reset.

## Root Cause

TASK_315 rebase/promotion created default rows for newly added Matrix/Fee lines with unsaveable editable pricing fields. The first failure was `unit_type=""`; a second user smoke run exposed historical/promoted numeric placeholders such as `testing_fee="Pending"` and summary values like `external_cost="Pending"`. The frontend displayed these placeholders as pending UI state, but autosave/Confirm Fee payloads require saveable unit types and numeric totals, so the persistence loop failed before the Notes/statistics flow could close.

## Scope

- Backend pending rebase default rows must use saveable Fee defaults.
- Backend promotion must sanitize historical blank `unit_type` when remapping rows.
- Pricing draft API responses must sanitize historical `Pending` numeric placeholders into saveable numeric defaults while preserving Notes.
- Frontend saved-draft hydration must normalize blank `unit_type` and `Pending` numeric placeholders to the current preview/default values before autosave/Confirm Fee.
- Add regression tests for backend rebase/promotion and frontend autosave payload.

## Out Of Scope

- No Fee calculation algorithm changes.
- No Project Folder readiness changes.
- No Matrix Editor UI changes.
- No new rebase UI or inactive removed-row editing.

## Acceptance

- Added Matrix rows rebase into Fee rows with saveable defaults.
- Historical blank `unit_type` pricing drafts no longer cause frontend autosave to submit `unit_type=""`.
- Historical `Pending` numeric pricing drafts no longer cause Total Testing Fee or Confirm Fee summary fields to become non-numeric.
- Existing Notes are preserved through promotion/fallback when the row identity is matched.
- Focused backend and frontend tests pass.

## Completion Notes

- Pending rebase defaults now use `spend_time="0"`, `unit_price="0"`, `unit_type="Pending"`, `units="1"`, `base_fee="0"`, `discount="0%"`, and `testing_fee="0"`.
- Promotion remap now converts blank unit type to `Pending`.
- Frontend hydrate now converts blank saved unit type to the current preview fallback, e.g. the basic-fill rule default such as `per photo`.
- Pricing draft GET now converts historical `Pending` numeric placeholders to saveable defaults (`0`, `1`, `0%`, `200`) before returning payloads to the UI.
- Frontend hydrate now converts `Pending` numeric saved values to the current preview/default value, preserving existing calculated fee statistics where the basic-fill rule has a numeric price.
