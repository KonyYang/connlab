# TASK_315D Follow-up Plan: Fee Rebase Saveable Defaults

Status: Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Active Task

`TASK_315D_FOLLOWUP_FEE_REBASE_SAVEABLE_DEFAULTS`

## Why This Is Allowed

The user reproduced a TASK_314/TASK_315 regression on the Fee Evaluation page: after Fee Notes were entered and Matrix was changed, Fee autosave failed with `unit_type` validation and the notes appeared lost. A follow-up smoke run also showed `testing_fee_total must be numeric` because historical/promoted Fee drafts could carry `Pending` in numeric fields, breaking the fee statistics/Confirm Fee path. This is a direct defect in the approved Matrix/Fee draft persistence and rebase sequence, not a new feature.

## Investigation Summary

- API validation allows `pending`/`Pending` but rejects `unit_type=""`.
- Pending rebase default rows for newly added Matrix rows used blank pricing fields.
- Promotion could preserve that blank unit type into the new current pricing draft.
- Frontend select rendering visually mapped blank values to `Pending`, but the autosave payload still carried the blank value.
- Historical/current pricing draft payloads could also contain `Pending` in numeric editable fields and summary fields.
- Frontend hydrate treated those `Pending` numeric placeholders as saved edits, making Total Testing Fee and Confirm Fee summary values non-numeric.

## Implementation Plan

1. Add failing backend tests for saveable defaults on newly added Matrix rows.
2. Add failing backend promotion test for historical blank `unit_type`.
3. Add failing frontend test for blank promoted unit type before autosave.
4. Change backend rebase default rows to use saveable defaults.
5. Change backend promotion remap to sanitize blank `unit_type`.
6. Change frontend hydrate/apply logic to normalize blank saved unit type before autosave.
7. Add pricing draft API and frontend regression coverage for historical `Pending` numeric placeholders.
8. Change pricing draft GET response and frontend hydrate logic to normalize `Pending` numeric placeholders to saveable defaults/current preview values while preserving Notes and calculated fee defaults.
9. Run backend/frontend regression tests and build.

## Risks

- Defaults must not overwrite preserved pricing values. Tests cover preserved rows separately.
- Frontend fallback should prefer the rule/basic-fill default when available, not blindly `Pending`, so existing Matrix pricing defaults remain useful.
- Numeric placeholder cleanup must not erase Notes or valid calculated fee defaults; API/frontend tests cover both.

## Validation

- `py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py -q`
- `py -m pytest tests/integration/test_fee_evaluation_pricing_draft_api.py tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py -q`
- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false`
- `cd frontend; npm run build`

## Completion Summary

The save chain now rejects the bad state at the source and heals existing blank unit types plus `Pending` numeric placeholders at API/frontend hydration boundaries. Fee Notes can be saved after Matrix-driven Fee rebase instead of being stranded behind a `unit_type` validation error, and Total Testing Fee/Confirm Fee summary values remain numeric instead of becoming `Pending`.
