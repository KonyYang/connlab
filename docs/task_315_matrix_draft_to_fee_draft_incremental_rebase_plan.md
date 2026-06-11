# TASK_315 Matrix Draft To Fee Draft Incremental Rebase Plan

Status: Planned. Awaiting user review and explicit approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_315` is a planned follow-up after `TASK_314_MATRIX_AND_FEE_BACKGROUND_DRAFT_PERSISTENCE`. It must not be implemented before TASK_314 exists in code, because it depends on background Matrix draft persistence, draft discard, and Confirm Matrix gating.

## Why This Task Is Allowed To Plan Now

The user clarified that Matrix and Fee Evaluation should maintain their association across Matrix edits. If Matrix groups or steps are added or removed, Fee Evaluation should be incrementally adjusted while preserving already edited Fee values. Planning this task is allowed because it creates a reviewable future task and does not implement code.

## Step 1: Task Understanding

Goal:

- Rebase Fee Evaluation drafts from a base Confirmed Matrix context to a changed Matrix draft/new Confirmed Matrix context.
- Preserve edited Fee values for unchanged Matrix rows.
- Add default Fee rows for newly added Matrix groups/steps.
- Soft-remove Fee rows for removed Matrix groups/steps.
- Roll back pending Fee changes when Matrix edits are canceled.
- Promote the rebased Fee draft only after Matrix is confirmed.

Inputs:

- Base active Confirmed Matrix authority and its current Fee pricing draft.
- Current autosaved Matrix draft from TASK_314.
- Fee rule version and default rule-derived Fee rows.

Outputs:

- Pending Fee rebase draft bound to a Matrix draft id.
- Current Fee pricing draft bound to the new Confirmed Matrix id/revision after Confirm Matrix.
- Inactive removed Fee rows preserved for review but excluded from active totals/export.

Not allowed:

- No automatic Confirm Fee.
- No report, StepInstance, evidence/image, AI, permission, LAN/server, multi-user, package execute, or public-drive publishing scope.
- No pricing rule update or new price judgment.
- No reliance on regenerated Confirmed Matrix UUIDs for cross-version matching.

## Step 2: Backend Design

### Rebase Key

Add a deterministic rebase key helper shared by Matrix basic-fill and Fee draft rebase logic.

V1 key:

```text
group_key_or_label + stable_row_identity + step_token + step_index
```

Definitions:

- `group_key_or_label`: normalized group key when present; otherwise normalized group label.
- `stable_row_identity`: `source_row_snapshot_id` when present; otherwise the persistent Matrix `draft_row_id`; otherwise normalized `row_signature` fallback.
- `row_signature`: normalized `test_item`, `section`, `method`, `condition`, and `requirement`.
- `step_token`: numeric token display value from parsed Matrix token.
- `step_index`: parsed token index within the Matrix cell.

Do not use `confirmed_group_id`, `confirmed_row_id`, or Fee `line_id` as the cross-version match key, because new Matrix authority revisions may regenerate those ids.

Text-only Matrix edits to `test_item`, `method`, `condition`, or `requirement` must preserve existing Fee manual values when stable source row or draft row lineage exists. Rows without stable lineage use the text-signature fallback; V1 accepts remove/add behavior for those lineage-less rows if their fallback signature changes.

### Pending Fee Rebase Storage

Create a pending Fee rebase persistence slice bound to `project_matrix_draft_id`.

Minimum stored fields:

- `pending_rebase_id`
- `project_id`
- `project_matrix_draft_id`
- `base_confirmed_matrix_id`
- `base_confirmed_revision`
- `fee_rule_version_id`
- `payload_json`
- `created_at`
- `updated_at`

The payload must include:

- active edited Fee rows for target Matrix draft rows
- inactive removed Fee rows
- summary values such as condition confirmation, external cost, external cost note, and lab manpower hourly rate
- rebase summary counts: preserved, added, removed

### Pricing Draft Payload Extension

Extend `FeeEvaluationEditedExportValues` with inactive removed rows.

V1 inactive row fields:

- previous edited row values
- previous group label/key
- previous row signature display fields
- previous step token and step index
- `inactive_reason="removed_from_matrix"`

Inactive rows are persisted for review only. They are excluded from:

- active Fee totals
- Fee Form export
- Confirm Fee summary totals

### Rebase Service

Add a Matrix Fee draft rebase application service.

Behavior:

1. Load base Confirmed Matrix and base current pricing draft.
2. Build source Fee rows:
   - use saved base pricing draft when current
   - otherwise use default Fee rows derived from the base Confirmed Matrix
3. Build target Fee rows from the Matrix draft.
4. Match source to target by rebase key.
5. Preserve edited values for matched rows, updating target lineage.
6. Create default values for target-only rows.
7. Preserve source-only rows as inactive removed rows.
8. Save pending rebase by `project_matrix_draft_id`.
9. Return a rebase result object that can be `current` or `failed` without changing the Matrix draft save result.

Failure policy:

- Matrix draft autosave remains successful if the Matrix draft itself saved and validated.
- Fee rebase failure is reported as `fee_rebase_status="failed"` with an actionable message.
- Fee rebase failure blocks or warning-gates Fee readiness, Package readiness, Fee Form export, and Confirm Fee for the latest Matrix/rule context.
- Fee rebase failure does not block Matrix autosave and does not block Confirm Matrix.

### Matrix Cancel Integration

When TASK_314 discards a Matrix draft, also physically delete the pending Fee rebase bound to that `project_matrix_draft_id`.

No Confirmed Fee or current Confirmed Matrix pricing draft is changed by cancel.

### Matrix Confirm Integration

After Confirm Matrix creates the new Confirmed Matrix revision:

1. Load pending Fee rebase for the Matrix draft id.
2. Map rebased active rows onto the new Confirmed Matrix basic-fill rows using the same rebase key.
3. Save a current Fee pricing draft bound to the new confirmed matrix id/revision and fee rule version.
4. Carry inactive removed rows into that new pricing draft payload.
5. Do not create a Confirmed Fee version.

If no pending rebase exists, attempt one synchronous rebase from the base current Fee pricing draft to the new Confirmed Matrix revision.

If confirm-time rebase fails:

- Confirm Matrix still succeeds and publishes the new Confirmed Matrix authority.
- The response returns `fee_rebase_status="failed"` and the failure message.
- No current Fee pricing draft is created or promoted for the new Confirmed Matrix revision.
- Fee Evaluation and package readiness must show that Fee requires review/recovery before Confirm Fee or package readiness can proceed.

## Step 3: Frontend Design

### Matrix Editor

After Matrix autosave succeeds, display the Fee rebase status returned by the same autosave response:

- `Fee draft synchronized`
- `Fee draft sync failed`

Fee rebase runs after Matrix autosave, but it does not define Matrix autosave success. If rebase fails, the Matrix draft remains saved, the UI shows the Fee sync failure, and `Confirm Matrix` remains available once Matrix autosave itself is current and valid.

`Confirm Matrix` may complete while Fee rebase is failed. In that case the UI must surface that Fee and package readiness require recovery/review before Confirm Fee or downstream package readiness can proceed.

Cancel Matrix keeps the TASK_314 semantics:

- discard Matrix draft
- discard pending Fee rebase
- return to Workbench

### Fee Evaluation

After Matrix Confirm and navigation to Fee Evaluation:

- Load the current pricing draft for the new Confirmed Matrix revision.
- Show active rows normally.
- Show inactive removed rows in a separate `Removed from Matrix` review section.
- Exclude inactive removed rows from totals and export payload.

The page should show a compact rebase summary when present:

- preserved rows
- added rows
- removed rows

## Step 4: API / DTO Changes

Backend additions:

- Extend the TASK_314 Matrix draft autosave response with:
  - `fee_rebase_status: "not_required" | "current" | "failed"`
  - `fee_rebase_summary: { preserved_count, added_count, removed_count } | null`
  - `fee_rebase_error: string | null`

No separate frontend-triggered rebase endpoint is added in V1. Rebase runs inside the Matrix draft autosave application flow after the Matrix draft is saved.

- Matrix draft discard endpoint from TASK_314 deletes pending fee rebase as part of discard.

- Matrix confirm response must include Fee rebase summary when TASK_315 rebase is active:
  - `fee_rebase_status`
  - `fee_rebase_summary`
  - `fee_rebase_error`

Fee pricing draft response additions:

- inactive removed rows in payload/DTO
- rebase summary metadata when the pricing draft was produced by Matrix rebase

Do not change Confirmed Fee version authority schema in V1.

## Step 5: Testing Plan

Backend tests:

- Matching rows preserve edited Fee values when Confirmed Matrix ids change.
- Text-only row edits preserve edited Fee values when `source_row_snapshot_id` or `draft_row_id` is stable.
- Lineage-less rows use row-signature fallback and may become remove/add when the fallback signature changes.
- Added Matrix group creates active default Fee rows.
- Added Matrix step creates active default Fee row.
- Removed Matrix group moves old Fee rows to inactive removed rows.
- Removed Matrix step moves old Fee row to inactive removed row.
- Fee rebase failure returns failed status but does not fail Matrix autosave.
- Confirm Matrix succeeds when confirm-time Fee rebase fails and no current pricing draft is promoted.
- Matrix cancel deletes pending Fee rebase and leaves current pricing draft unchanged.
- Matrix confirm promotes pending rebase to a current pricing draft for the new Confirmed Matrix revision.
- Confirm Fee ignores inactive removed rows in totals.
- Fee Form export ignores inactive removed rows.

Frontend tests:

- Matrix Editor shows Fee draft sync status after autosave.
- Matrix Editor keeps Confirm Matrix available when Matrix autosave is current but Fee sync failed.
- Matrix cancel calls discard and does not leave Fee rebase visible after re-entry.
- Fee Evaluation renders `Removed from Matrix` inactive rows separately.
- Fee Evaluation and package readiness show blocked/review-required state when latest Matrix has no current pricing draft because rebase failed.
- Fee Evaluation totals exclude inactive rows.
- Confirm Fee payload excludes inactive rows from active totals/export.

Validation commands:

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
cd frontend
npm test -- --run FeeEvaluationReviewExportPage MatrixEditorWorkspace --watch=false
npm run build
cd ..
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or matrix_editor"
```

## Risks

- Cross-version matching can be wrong if row text changes materially. V1 should treat changed row signatures as remove + add rather than guessing.
- Inactive removed rows must never affect totals, export, or Confirm Fee.
- Rebase must not auto-confirm Fee. Operators still review and explicitly confirm.
- Matrix cancel must not mutate current Confirmed Matrix pricing drafts.

## Stop Point

After user review, stop unless explicit implementation approval is given. Implementation must update `docs/task_board.md` only after approved execution and validation.
