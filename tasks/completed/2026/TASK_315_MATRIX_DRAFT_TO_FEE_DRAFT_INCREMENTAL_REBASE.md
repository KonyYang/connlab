# TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE

Status: closed (archived 2026-08-18; umbrella/split rationale superseded by Sol-native manual task publishing)

Umbrella plan: `docs/task_315_matrix_draft_to_fee_draft_incremental_rebase_plan.md`

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

TASK_315 is the product-level umbrella for preserving Fee Evaluation draft work when Matrix Editor changes add, remove, or edit Matrix groups and steps. It is intentionally split into smaller executable tasks after TASK_314A, TASK_314B, and TASK_314C completed.

Do not implement TASK_315 as one combined task. Implement only an explicitly approved TASK_315 subtask.

## Completed Prerequisites

- `TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE` is complete and provides Matrix Editor autosave, restore, discard, and Confirm Matrix saved-draft gating.
- `TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE` is complete and provides Fee pricing draft autosave, discard, Confirm Fee gating, and saved-draft summary validation.
- `TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION` is complete and protects Matrix/Fee/Project Folder Required forms linkage.

## Product Goal

When a Matrix draft changes groups or step rows, the associated Fee Evaluation pricing draft should be incrementally rebased instead of restarted from zero.

Operator intent:

- Added Matrix groups/steps create default Fee Evaluation rows.
- Removed Matrix groups/steps are soft-removed from Fee Evaluation so previous manual values remain reviewable but are excluded from active totals/export.
- Unchanged Matrix groups/steps keep their previously edited Fee values.
- Existing Fee manual rows are preserved by their own rules: report preparation is global; sample preparation is rebased by group identity rather than regenerated confirmed group id.
- Canceling Matrix edits discards pending Fee rebase work.
- Confirming Matrix promotes the pending Fee rebase into the latest current Fee pricing draft for the new Confirmed Matrix revision.

Test Record generation remains derived from Matrix and does not need Fee draft rebase behavior.

## Accepted Split

### TASK_315A - Matrix To Fee Rebase Core

Task file: `tasks/TASK_315A_MATRIX_TO_FEE_REBASE_CORE.md`

Plan file: `docs/task_315a_matrix_to_fee_rebase_core_plan.md`

Scope:

- Backend pure rebase key and rebase service.
- Active target rows, inactive removed rows, and rebase summary value models.
- Preservation/default/remove logic using in-memory inputs or existing domain/value payloads.
- Unit tests for matching, added rows, removed rows, text edits with stable lineage, manual-row preservation, and inactive-row exclusion metadata.

No Matrix autosave integration, pending persistence, Matrix Confirm promotion, API route changes, frontend UI, Project Folder behavior, or production workflow wiring.

### TASK_315B - Pending Rebase Persistence And Matrix Autosave/Cancel Lifecycle

Planned follow-up. Not executable until TASK_315A is complete and separately approved.

Scope:

- Pending rebase storage bound to Matrix draft id and fee rule version.
- Matrix autosave non-blocking rebase status.
- Cancel cleanup and in-flight/stale-generation rules.

### TASK_315C - Matrix Confirm Promotion

Task file: `tasks/TASK_315C_MATRIX_CONFIRM_PROMOTION.md`

Plan file: `docs/task_315c_matrix_confirm_promotion_plan.md`

Planned follow-up. Not executable until separately approved.

Scope:

- Promote pending rebase into a current Fee pricing draft after Matrix Confirm.
- Confirm-time synchronous fallback.
- Failure path where Matrix Confirm succeeds but Fee pricing draft is not promoted.

### TASK_315D - Fee Evaluation UI And Project Folder Regression

Planned follow-up. Not executable until TASK_315C is complete and separately approved.

Scope:

- Display inactive `Removed from Matrix` rows in Fee Evaluation.
- Keep inactive rows out of totals, export, and Confirm Fee payloads.
- Rebase summary UI and Project Folder Required forms regression.

## Global V1 Contract

### Rebase Matching

Do not match across Matrix revisions by regenerated confirmed UUIDs.

Use V1 rebase key:

```text
group_key_or_label + stable_row_identity + step_token + step_index
```

Where:

- `group_key_or_label` prefers normalized group key, then normalized group label.
- `stable_row_identity` prefers `source_row_snapshot_id` when present, then persistent Matrix `draft_row_id`, then a normalized row signature fallback.
- `row_signature` fallback is normalized `test_item`, `section`, `method`, `condition`, and `requirement`.
- `step_token` is the numeric token display value.
- `step_index` is the parsed-token index within the Matrix cell.

Text-only Matrix edits to `test_item`, `method`, `condition`, or `requirement` must preserve Fee values when `source_row_snapshot_id` or `draft_row_id` is stable. Only rows without stable lineage fall back to text signature matching; V1 accepts remove/add behavior for those lineage-less rows if their fallback signature changes.

### Fee Authority Boundary

- A promoted pricing draft is still only a draft, not Confirmed Fee authority.
- Confirm Fee remains an explicit operator action.
- Project Folder Required forms remain blocked until current Confirmed Matrix and current Confirmed Fee authority both exist for the current Matrix/rule context.

### Inactive Removed Rows

- Removed rows must be serialized outside active `rows`, for example as `inactive_removed_rows`.
- Inactive rows are review metadata and must not be accepted as active basic-fill rows.
- Inactive rows must not contribute to active totals, Fee Form export, or Confirm Fee summary values.

## Out Of Scope For The Umbrella

Unless a later approved subtask explicitly says otherwise:

- No automatic Confirm Fee.
- No changed pricing-rule judgment beyond existing default Fee rule matching.
- No hard deletion of historical Fee edited values when Matrix rows are removed.
- No Test Record special handling.
- No report generation, StepInstance, evidence/image, AI review, permissions, LAN/server, or multi-user merge.
- No package execute or public-drive publishing.
- No draft audit history beyond the current pending rebase state.

## Stop Point

Stop after maintaining this umbrella and the approved subtask plan files. Do not implement TASK_315, TASK_315A, or later subtasks until the user explicitly approves the specific executable task.
