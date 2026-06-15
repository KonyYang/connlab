# TASK_315C_MATRIX_CONFIRM_PROMOTION

Status: Complete.

Executable plan: `docs/task_315c_matrix_confirm_promotion_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Parent umbrella: `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE`.

Prerequisites:

- `TASK_315A_MATRIX_TO_FEE_REBASE_CORE` is complete.
- `TASK_315B_PENDING_REBASE_PERSISTENCE_AND_MATRIX_AUTOSAVE_CANCEL_LIFECYCLE` is complete, including review follow-up for step index alignment, Cancel race cleanup, and database-level stale generation CAS.

TASK_315C is the third executable slice of TASK_315. It promotes pending Matrix-to-Fee rebase output into the current Fee Evaluation pricing draft after Matrix Confirm publishes a new Confirmed Matrix revision. It must not add Fee UI, Project Folder regression, inactive-row display, or Confirm Fee authority behavior; those remain later slices.

## Why This Task Is Allowed To Plan Now

TASK_315B now persists pending rebase output for Matrix Editor autosaves and deletes it on Cancel. The next controlled lifecycle step is to consume that pending output after Matrix Confirm succeeds, so the new Confirmed Matrix context has a current Fee pricing draft.

Implementation was completed after separate explicit user approval.

## Goal

After Matrix Confirm publishes a new active Confirmed Matrix revision:

- promote the matching pending rebase into a current Fee Evaluation pricing draft for the new Confirmed Matrix context;
- if no usable pending rebase exists, attempt a synchronous fallback rebase;
- never block, rollback, or fail Matrix Confirm because Fee pricing draft promotion failed;
- report promotion status to the backend/API result so operators and tests can distinguish promoted, fallback-promoted, skipped, and failed cases.

## Inputs

- The saved Matrix Editor draft confirmed by `MatrixEditorSessionService.confirm_session`.
- The previous active Confirmed Matrix context.
- The newly published Confirmed Matrix snapshot.
- Pending rebase payload persisted by TASK_315B, bound to `project_matrix_draft_id + fee_rule_version_id`.
- Current active Fee rule version.
- Existing Fee Evaluation pricing draft store and validation rules.
- TASK_315A rebase core with explicit previous-context source rows when pending rebase is missing or unusable.

## Outputs

- A current `FeeEvaluationPricingDraftSnapshot` for the new Confirmed Matrix context when promotion succeeds.
- `MatrixEditorSessionConfirmResult` promotion metadata:
  - `fee_rebase_promotion_status`
  - `fee_rebase_promotion_error`
  - `fee_rebase_promotion_summary`
- Matrix Confirm remains successful even if promotion fails.
- Pending rebase for the confirmed Matrix draft is consumed/deleted only after successful promotion, or left available for diagnostics/retry if promotion fails.

## V1 Promotion Status Contract

Use these backend/API status strings:

```text
not_required | promoted | fallback_promoted | skipped | failed
```

Meanings:

- `not_required`: Matrix Confirm was no-change, first authority publish, or a path where no previous active Matrix/Fee context exists.
- `promoted`: a current pending rebase was found, validated, remapped to the new Confirmed Matrix ids, and saved as current Fee pricing draft.
- `fallback_promoted`: no usable pending rebase existed, but confirm-time synchronous fallback rebase succeeded and saved current Fee pricing draft.
- `skipped`: no current base Fee pricing draft exists and no pending rebase exists, so there is no operator Fee work to preserve; Matrix Confirm remains successful and Fee Evaluation can seed defaults later.
- `failed`: Matrix Confirm succeeded, but promotion/fallback failed. Response must include actionable `fee_rebase_promotion_error`.

Fee promotion failure must never change Matrix Confirm HTTP success into a failure.

## In Scope

- Pending rebase payload deserialization for promotion.
- Application service to promote pending/fallback rebase into current Fee pricing draft.
- Mapping promoted rows from Matrix draft ids to newly generated Confirmed Matrix row/group ids and newly generated Fee basic-fill identities.
- Confirm-time fallback rebase when pending rebase is missing/stale/unusable, using explicit previous active Matrix context as source and saved Matrix draft as target.
- Preservation of previous Fee pricing draft summary values during both pending promotion and fallback promotion.
- Matrix Confirm integration after confirmed snapshot publish succeeds.
- API response extension for Matrix Confirm promotion metadata.
- Backend unit/integration tests for pending promotion, fallback promotion, skipped and failed promotion, id remapping, and non-blocking Confirm behavior.

## Out Of Scope

- No Fee Evaluation UI changes.
- No inactive removed-row UI.
- No Project Folder Required forms regression or selector changes.
- No Confirm Fee behavior changes.
- No automatic Confirm Fee.
- No pricing-rule changes.
- No Matrix autosave pending storage changes except narrowly required helpers for reading/consuming pending.
- No Test Record behavior changes.
- No StepInstance, report generation, evidence/image, AI, permissions, LAN/server, or multi-user scope.

If implementation needs any out-of-scope behavior, stop and split it into TASK_315D or a new follow-up task.

## Acceptance Criteria

- Confirming a saved Matrix revision with a current pending rebase promotes it into a current Fee pricing draft for the newly confirmed Matrix id/revision.
- Promoted active rows use the new Confirmed Matrix `source_line_id`, `confirmed_group_id`, and `confirmed_row_id` identities, not stale Matrix draft ids, draft-shaped source line ids, or previous Confirmed Matrix ids.
- Promoted row content preserves editable pricing fields plus stable row matching intent (`step_token`, `step_index`, and lineage metadata where available), while regenerated identity fields must match the new Confirmed Matrix basic-fill output.
- Promotion output is validated against the new Confirmed Matrix basic-fill identity contract before save; a promoted draft must be loadable/savable by `FeeEvaluationPricingDraftPersistenceService`.
- Pending promotion and fallback promotion both preserve previous pricing draft summary values (`condition_confirmation_spend_time`, `external_cost`, `external_cost_note`, `lab_manpower_hourly_rate`). Blank/default summary is allowed only when no previous pricing draft exists.
- Promoted manual rows are saved into the new context and sample-preparation manual rows use the new Confirmed Matrix group id when applicable.
- Pending payload is consumed/deleted only after successful pricing draft save.
- If no usable pending rebase exists but a base Fee pricing draft exists, synchronous fallback rebase uses previous active Matrix context as source, saved Matrix draft as target, and attempts to produce/save the new current pricing draft after Matrix Confirm succeeds.
- If no pending rebase and no base Fee pricing draft exists, promotion returns `skipped` and Matrix Confirm succeeds.
- If promotion/fallback save fails, Matrix Confirm still returns `publish_status="published"` with `fee_rebase_promotion_status="failed"` and an actionable error.
- Matrix Confirm no-change returns `fee_rebase_promotion_status="not_required"`.
- First Confirmed Matrix authority publish returns `fee_rebase_promotion_status="not_required"`.
- No Confirmed Fee authority is created or modified.
- No frontend code is changed in TASK_315C unless a later approved UI slice requests it.

## Required Validation

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
```

```powershell
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

```powershell
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_repository.py tests/unit/test_matrix_fee_draft_rebase_service.py -q
```

If pricing draft persistence helpers are touched:

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

No frontend test/build is required unless frontend files are changed, which should not happen in TASK_315C.

## Stop Point

TASK_315C stops here. Do not proceed to TASK_315D, Fee UI, Project Folder regression, Confirm Fee changes, StepInstance, report, AI, permissions, LAN/server, or multi-user scope without separate explicit approval.

## Completion Notes

Implemented Matrix Confirm promotion of pending Matrix-to-Fee rebase output into a current Fee Evaluation pricing draft for the newly confirmed Matrix context. Confirm now reports non-fatal promotion status metadata. Pending promotion uses new Confirmed Matrix basic-fill identities, preserves previous pricing draft summary fields, and deletes pending only after successful save. Missing/unusable pending falls back to explicit previous active Matrix source rows plus saved Matrix draft target rows; missing previous pricing draft returns `skipped`.

Review follow-up: pending promotion now requires the pending rebase `matrix_draft_payload_signature` to match the exact saved Matrix draft signature being confirmed. Stale pending output from an older autosave of the same Matrix draft is treated as unusable and goes through fallback/skipped handling. Added coverage for stale-signature fallback and sample-preparation manual row remapping to the new Confirmed Matrix group identity.

Validation:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/unit/test_matrix_fee_pending_rebase_service.py tests/unit/test_matrix_fee_pending_rebase_repository.py tests/unit/test_matrix_fee_draft_rebase_service.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

Review follow-up validation:

```powershell
py -m pytest tests/unit/test_matrix_fee_rebase_promotion_service.py -q
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
```

All required validation passed.
