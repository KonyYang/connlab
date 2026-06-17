# TASK_315E: Fee Rebase Hidden Preserved Rows

Status: Complete.

## Goal

Preserve edited Fee Evaluation pricing rows when Matrix groups/steps are soft removed by being unselected, keep those rows hidden from the active Fee Form, and restore the previous edits when Matrix reselects the same groups/steps later. If Matrix performs a real structural delete, Fee Evaluation must follow the Matrix delete semantics instead of restoring the old row as a current draft candidate.

## Business Rule

Matrix remains the execution authority map. Fee Evaluation follows the current Matrix operation:

- Matrix selected rows/groups are active Fee rows.
- Matrix unselected rows/groups are hidden inactive Fee rows and are not visible, counted, exported, or confirmed.
- Matrix reselected rows/groups can restore previously edited Fee values from hidden inactive storage.
- Matrix truly deleted rows/groups are removed from Fee draft recovery scope.

## Current Problem

TASK_315A/B/C/D introduced Matrix-to-Fee incremental rebase, pending rebase payloads, Matrix Confirm promotion, and Fee UI integration. The rebase core already reports removed rows as `inactive_removed_rows`, and pending payloads can serialize them, but promoted/current Fee pricing drafts currently persist only active `rows`, `summary`, and `manual_rows`.

This means a Matrix soft removal can correctly disappear from the visible Fee Form while still losing the edited Fee values after Matrix Confirm. A later Matrix reselect may then default-fill the Fee row instead of restoring the operator's previous pricing edits.

## Scope

- Add a hidden preserved-row storage model to current Fee pricing drafts.
- Persist hidden inactive Fee rows through pricing draft JSON save/load.
- Promote pending/fallback rebase inactive rows into the new current pricing draft without showing them in the Fee Form.
- Use active rows plus hidden inactive rows as rebase source candidates when Matrix autosave creates a pending Fee rebase.
- Restore prior edits when Matrix reselects a previously soft-removed group/step.
- Keep inactive rows excluded from Fee totals, export payloads, Confirm Fee authority creation, and Project Folder readiness.
- Add backend tests for soft-remove preservation, reselect restoration, hard-delete cleanup semantics, and active-only validation/export behavior.
- Add focused frontend/API regression coverage only if backend response shape changes require it.

## Out Of Scope

- No UI surface for reviewing or editing hidden inactive rows.
- No removed-row details panel in Fee Evaluation.
- No Fee calculation algorithm changes.
- No Confirm Fee workflow changes beyond ensuring hidden rows are excluded.
- No Project Folder readiness or Required Forms logic changes.
- No Matrix Editor visual changes.
- No StepInstance, Report, AI review, permissions, LAN/server, or multi-user scope.
- No broad refactor of TASK_314/TASK_315 services beyond the hidden-row lifecycle.

## Required Design Semantics

### Active Fee Rows

Rows currently selected by Matrix. These are visible in Fee Evaluation, included in totals, saved as current active pricing rows, exported, and eligible for Confirm Fee.

### Hidden Preserved Fee Rows

Rows previously edited by the operator but currently absent from the selected Matrix target because the related Matrix group/step is soft removed. These are saved in the current pricing draft as hidden recovery data only.

### Matrix Soft Remove

A Matrix group/step is not selected in the current Matrix draft but still exists structurally in Matrix metadata. Fee Evaluation hides the matching row and preserves the previous edit in hidden storage.

### Matrix Hard Delete

A Matrix group/step no longer exists structurally in the Matrix draft/confirmed Matrix identity set. Fee Evaluation follows the Matrix delete semantics and must not restore that row as a current draft candidate.

## Implementation Constraints

- Preserve existing API compatibility as much as possible.
- Do not expose hidden inactive rows in the normal Fee Form preview payload.
- Keep exact-context pricing draft behavior from TASK_314B.
- Keep TASK_315D saveable default cleanup behavior.
- Validate hidden rows separately from active rows so inactive legacy identities do not block current Fee draft load/save.
- Prefer stable rebase identity keys already defined by `MatrixFeeRebaseKey`.
- Preserve the full rebase key or equivalent primitive identity at the moment a row becomes inactive; a previous row plus group label/signature is not sufficient for reliable restoration.
- Define Matrix soft remove using a structural Matrix identity set, not only the selected target rows. A row is recoverable only when its rebase key still exists structurally in the Matrix draft but is not selected.

## Acceptance Criteria

- Soft-remove a Matrix group/step after editing Fee values, confirm Matrix, and open Fee Evaluation: the group/step is hidden and excluded from totals.
- Reselect the same Matrix group/step later and confirm Matrix: the previous edited Fee values are restored.
- Active Fee autosave and Confirm Fee payloads do not include hidden inactive rows.
- Current pricing draft JSON round-trips hidden inactive rows without corrupting active rows, manual rows, or summary.
- Truly deleted Matrix groups/steps are not restored as current draft rows.
- Hidden inactive rows carry enough identity to match the same Matrix group/row/step when it is reselected later.
- Existing TASK_315 rebase/promotion/defaults tests still pass.
- New regression tests document soft-remove, restore, and hard-delete semantics.

## Validation Targets

- `py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py -q`
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q`
- `py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q`
- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false` only if frontend/API response handling changes.
- `cd frontend; npm run build` only if frontend files change.

## Stop Point

After this task is implemented and validated, stop. Do not proceed to UI editing for inactive rows or any later Matrix execution/report scope without a separate task and explicit approval.

## Completion Notes

- Added hidden inactive Fee row value objects to the pricing draft aggregate while keeping active `rows`, `manual_rows`, and `summary` as the only confirmable/exportable Fee data.
- Pricing draft JSON now round-trips hidden inactive rows and remains backward-compatible with historical payloads that lack `inactive_rows`.
- Matrix rebase removed rows now retain full rebase identity so soft-removed rows can be restored reliably when Matrix reselects the same group/row/step.
- Matrix pending rebase now treats active rows as highest priority, hidden inactive rows as recovery candidates, and default basic-fill rows as fallback.
- Pending rebase payload JSON helpers were split into a focused payload module so the pending rebase lifecycle service remains under the project file-size limit.
- Pending rebase source-row helpers were split into a focused source module so hidden-row recovery logic remains testable without growing the lifecycle service past the file-size limit.
- Matrix soft remove and hard delete are distinguished using structural Matrix rebase keys: unselected-but-structurally-present rows are preserved, structurally deleted rows are dropped from recovery scope.
- Matrix Confirm promotion carries inactive removed rows into the new current pricing draft hidden lane.
- Confirm Fee strips hidden inactive rows from the authority pricing snapshot and keeps summary validation active-only.
- Review follow-up fixed Fee autosave so active-only client saves preserve existing server-side hidden inactive rows.
- Review follow-up fixed restoration after confirmed Matrix soft remove by allowing hidden inactive rows to become rebase source candidates even when they are absent from the current Confirmed Matrix basic-fill.
- Added a service-level lifecycle regression covering Matrix soft-remove promotion, Fee autosave, Matrix reselect, and restored Fee pricing edits.

## Validation Summary

- `py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_rebase_promotion_service.py -q` (`41 passed`)
- `py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q` (`22 passed`)
- `py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q` (`16 passed`)
- `cd frontend; npm test -- --run FeeEvaluationReviewExportPage --watch=false` (`22 passed`, with existing non-failing React `act(...)` warnings)
- `cd frontend; npm run build` passed
