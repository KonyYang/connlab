# TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE

Status: Planned. Awaiting user review and explicit approval before implementation.

Executable plan: `docs/task_315_matrix_draft_to_fee_draft_incremental_rebase_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_315 is a follow-up after TASK_314. It requires TASK_314 background Matrix draft persistence, Matrix draft discard, and Confirm Matrix gating to exist first.

## Model Fit Assessment

GPT-5.3-codex is suitable for TASK_315 because the task is a bounded data-rebase feature across existing Matrix and Fee Evaluation draft models. It requires careful lineage matching, API/service changes, and focused tests, but it does not require AI judgment, Office automation, multi-user merge, or report generation. The primary risk is matching old and new Matrix rows without relying on regenerated Confirmed Matrix UUIDs; this can be controlled with explicit rebase keys and regression tests.

## Goal

When a Matrix draft changes groups or step rows, the associated Fee Evaluation draft should be incrementally rebased instead of restarted from zero.

Operator intent:

- Added Matrix groups/steps create default Fee Evaluation rows.
- Removed Matrix groups/steps are soft-removed from Fee Evaluation so previous manual values remain reviewable but are excluded from active totals/export.
- Unchanged Matrix groups/steps keep their previously edited Fee values.
- Canceling Matrix edits discards the pending Fee rebase.
- Confirming Matrix promotes the pending Fee rebase into the latest current Fee pricing draft for the new Confirmed Matrix revision.

Test Record generation remains derived from Matrix and does not need this rebase behavior.

## Current Code Reality

- Fee Evaluation edited rows are currently keyed by `source_line_id`, `confirmed_group_id`, `confirmed_row_id`, `step_token`, and `step_index`.
- Confirming a new Matrix revision can generate new confirmed group/row ids, so current confirmed ids are not stable enough for cross-version Fee edit preservation.
- Fee pricing drafts are currently bound to active Confirmed Matrix id/revision and fee rule version.
- TASK_314 will add Matrix background draft persistence and discard semantics. TASK_315 uses that Matrix draft lifecycle as the parent lifecycle for pending Fee rebase state.

## V1 Contract

### Rebase Trigger

After TASK_314 Matrix autosave succeeds for an existing active Confirmed Matrix, TASK_315 runs a Matrix Draft -> Fee Draft rebase.

Inputs:

- Base active Confirmed Matrix authority.
- Current Matrix draft working copy.
- Current Fee pricing draft for the base Confirmed Matrix context, if present.
- Fee rule version used by current Fee Evaluation.

Output:

- A pending Fee rebase draft bound to the Matrix draft id.
- Matrix autosave response includes Fee rebase status and preserved/added/removed counts.

If there is no current Fee pricing draft, the source values are the default Fee Evaluation values from the base Confirmed Matrix.

### Rebase Matching

Do not match across Matrix revisions by confirmed UUIDs.

Use V1 rebase key:

```text
group_key_or_label + stable_row_identity + step_token + step_index
```

Where:

- `group_key_or_label` prefers normalized group key, then normalized group label.
- `stable_row_identity` prefers `source_row_snapshot_id` when present, then the persistent Matrix `draft_row_id`, then a normalized row signature fallback.
- `row_signature` fallback is normalized `test_item`, `section`, `method`, `condition`, and `requirement`.
- `step_token` is the numeric token display value.
- `step_index` is the parsed-token index within the Matrix cell.

Text-only Matrix edits to `test_item`, `method`, `condition`, or `requirement` must preserve Fee values when `source_row_snapshot_id` or `draft_row_id` is stable. Only rows without stable lineage fall back to text signature matching; V1 accepts remove/add behavior for those lineage-less rows if their fallback signature changes.

Behavior:

- Matching target row found: copy previous edited Fee values into the target row and update target lineage fields.
- Target row has no source match: create a new active Fee row with default rule-derived values.
- Source row has no target match: keep it as an inactive removed Fee row with previous edited values and `removed_from_matrix` reason.

### Pending Rebase Lifecycle

- Matrix autosave creates or updates one pending Fee rebase draft for the current Matrix draft id.
- Fee rebase failure does not make Matrix autosave fail and does not block `Confirm Matrix`; Matrix remains the execution authority map, while Fee remains a derived output.
- When Fee rebase fails, the Matrix autosave response returns `fee_rebase_status="failed"` and an actionable error message. Fee/Package readiness and `Confirm Fee` remain blocked or warning-gated until a current Fee pricing draft exists for the latest Confirmed Matrix/rule context.
- Matrix Cancel physically deletes the Matrix draft through TASK_314 and must also delete the pending Fee rebase draft for that Matrix draft id.
- Matrix Confirm promotes the pending Fee rebase draft to the new Confirmed Matrix revision as the current Fee pricing draft.
- If Matrix Confirm finds no pending Fee rebase draft, it attempts one synchronous rebase from the latest base-context Fee pricing draft.
- If that confirm-time rebase also fails, Matrix Confirm still publishes the new Confirmed Matrix revision, returns `fee_rebase_status="failed"`, and does not create or promote a current Fee pricing draft for the new revision.

### Fee Evaluation Page Behavior

After Matrix Confirm:

- Fee Evaluation opens the new current pricing draft for the new Confirmed Matrix revision.
- Preserved rows show existing edited values.
- Added rows show default rule-derived values.
- Removed rows appear in a separate inactive `Removed from Matrix` review section.
- Removed rows are excluded from active totals, Fee Form export, and Confirm Fee totals.

## In Scope

- Backend rebase service for Matrix Draft -> pending Fee rebase draft.
- Storage for pending Fee rebase draft bound to Matrix draft id.
- Matrix autosave response extension with Fee rebase status and summary counts.
- Promotion of pending Fee rebase into current-context Fee pricing draft after Confirm Matrix.
- Cleanup of pending Fee rebase on Matrix Cancel.
- Extension of pricing draft payload to preserve inactive removed rows.
- Fee Evaluation UI display for inactive removed rows.
- Fee/Package readiness guard when Fee rebase failed or no current pricing draft exists for the latest Confirmed Matrix/rule context.
- Tests covering preserved, added, removed, cancel, and confirm promotion scenarios.

## Out Of Scope

- No automatic Confirm Fee.
- No changed pricing-rule judgment beyond existing default Fee rule matching.
- No hard deletion of historical Fee edited values when Matrix rows are removed.
- No Test Record special handling.
- No report generation, StepInstance, evidence/image, AI review, permissions, LAN/server, or multi-user merge.
- No package execute or public-drive publishing.
- No draft audit history beyond the current pending rebase state.

## Acceptance Criteria

- Editing a Matrix draft to add a group or step creates corresponding active Fee default rows in the pending rebase.
- Editing a Matrix draft to remove a group or step marks corresponding Fee rows as inactive removed rows, preserving their previous edited values.
- Unchanged Matrix rows keep edited Fee values after rebase, even when the new Confirmed Matrix revision uses new confirmed ids.
- Text-only Matrix row edits preserve edited Fee values when stable source row or draft row lineage is available.
- Fee rebase failure returns `fee_rebase_status="failed"` without marking Matrix autosave or Matrix Confirm as failed.
- Confirming Matrix can still publish Matrix authority when Fee rebase fails; Fee/Package readiness and Confirm Fee remain blocked or warning-gated until a current Fee pricing draft exists for the new Matrix/rule context.
- Canceling Matrix edits deletes the pending Fee rebase and leaves the current Confirmed Matrix pricing draft unchanged.
- Confirming Matrix promotes the pending Fee rebase to a current Fee pricing draft bound to the new Confirmed Matrix id/revision.
- Fee Evaluation after Matrix Confirm shows preserved active rows, new default rows, and removed inactive rows separately.
- Removed inactive rows do not contribute to totals, Fee Form export, or Confirm Fee summary values.
- Confirm Fee still requires explicit user confirmation and does not happen as a side effect of Confirm Matrix.

## Required Validation

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py tests/integration/test_matrix_editor_session_api.py -q
```

```powershell
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
```

```powershell
cd frontend
npm test -- --run FeeEvaluationReviewExportPage MatrixEditorWorkspace --watch=false
```

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "fee or matrix_editor"
```

## Stop Point

Stop after TASK_315 implementation, validation, and task board update. Do not proceed to automatic Confirm Fee, package execute, report generation, StepInstance, AI, permission, or multi-user scope.
