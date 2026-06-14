# TASK_315 Matrix Draft To Fee Draft Incremental Rebase Umbrella Plan

Status: Umbrella / split rationale. Not directly executable.

## Current Phase

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

## Current Task Status

`TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE` is no longer a single executable implementation task. It is the umbrella for a controlled Matrix-to-Fee draft rebase sequence.

Completed baseline:

- `TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE`
- `TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE`
- `TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION`

Next proposed executable slice:

```text
TASK_315A_MATRIX_TO_FEE_REBASE_CORE
```

Do not implement code from this umbrella plan. Implementation requires explicit approval for one subtask at a time.

## Why The Original TASK_315 Was Split

The original TASK_315 combined too many high-risk surfaces:

- backend Matrix-to-Fee rebase matching
- pending rebase persistence
- Matrix autosave status extension
- Matrix Cancel cleanup
- Matrix Confirm promotion
- Fee pricing draft payload schema extension
- Fee Evaluation inactive-row UI
- Fee totals/export/Confirm behavior
- Project Folder Required forms regression

Those surfaces cross TASK_314A, TASK_314B, and TASK_314C authority boundaries. Splitting TASK_315 keeps each implementation reviewable and prevents the rebase work from destabilizing Matrix confirmation, Fee confirmation, or Project Folder readiness in one step.

## Subtask Sequence

### TASK_315A - Matrix To Fee Rebase Core

Task file:

```text
tasks/TASK_315A_MATRIX_TO_FEE_REBASE_CORE.md
```

Plan file:

```text
docs/task_315a_matrix_to_fee_rebase_core_plan.md
```

Purpose:

- Build the pure backend rebase core.
- Define V1 rebase keys.
- Produce active target rows, inactive removed rows, and summary counts.
- Prove matching behavior with unit tests before touching persistence, APIs, or UI.

Hard stop:

- No Matrix autosave integration.
- No pending storage.
- No Matrix Confirm promotion.
- No frontend or Project Folder changes.

### TASK_315B - Pending Rebase Persistence And Matrix Autosave/Cancel Lifecycle

Purpose:

- Persist one pending rebase per Matrix draft/rule context.
- Trigger non-blocking rebase after successful Matrix autosave.
- Delete pending rebase on Matrix Cancel.
- Define stale autosave generation and in-flight cancellation behavior.

Prerequisite:

- Completed TASK_315A.

### TASK_315C - Matrix Confirm Promotion

Purpose:

- Promote pending rebase into a current Fee pricing draft after Matrix Confirm creates the new Confirmed Matrix revision.
- Attempt confirm-time synchronous fallback when pending rebase is missing.
- Preserve the failure policy: Matrix Confirm succeeds even if Fee rebase promotion fails.

Prerequisite:

- Completed TASK_315B.

### TASK_315D - Fee Evaluation UI And Project Folder Regression

Purpose:

- Render inactive `Removed from Matrix` rows in Fee Evaluation.
- Ensure inactive rows are excluded from totals, export, and Confirm Fee payload.
- Add Project Folder Required forms regressions proving a promoted pricing draft is not Confirmed Fee authority.

Prerequisite:

- Completed TASK_315C.

## Global Rebase Contract

### Inputs

- Base active Confirmed Matrix authority.
- Current Matrix draft working copy.
- Current Fee pricing draft for the base Confirmed Matrix/rule context, if present.
- Existing backend Fee Evaluation default-row construction path for default values and fee rule version resolution.

### Outputs

- Active target Fee rows for target Matrix rows.
- Inactive removed Fee rows for source rows no longer present in the target Matrix.
- Preserved manual rows according to V1 rules.
- Rebase summary counts.
- Later subtasks may persist this output as pending rebase or promoted pricing draft.

### Matching Key

Do not match across Matrix revisions by regenerated confirmed UUIDs.

Use V1 key:

```text
group_key_or_label + stable_row_identity + step_token + step_index
```

Definitions:

- `group_key_or_label`: normalized group key when present; otherwise normalized group label.
- `stable_row_identity`: `source_row_snapshot_id` when present; otherwise persistent Matrix `draft_row_id`; otherwise normalized row signature fallback.
- `row_signature`: normalized `test_item`, `section`, `method`, `condition`, and `requirement`.
- `step_token`: numeric token display value from parsed Matrix token.
- `step_index`: parsed-token index within the Matrix cell.

### Removed Rows

Removed rows are review metadata:

- stored outside active `rows`
- excluded from active validation
- excluded from totals
- excluded from Fee Form export
- excluded from Confirm Fee summary derivation

### Manual Rows

- Report preparation is global and should be preserved across rebase.
- Sample preparation is matched by normalized group key/label, not by regenerated confirmed group id.
- Removed group sample-preparation rows become inactive/review metadata or another explicit removed-group bucket in the approved subtask that introduces persistence/UI.

## Global Failure Policy

- Fee rebase failure must not make Matrix autosave fail.
- Fee rebase failure must not block Matrix Confirm.
- If Matrix Confirm succeeds but no current Fee pricing draft is promoted, Fee Evaluation must still recover through the existing default draft path from TASK_314B.
- Project Folder Required forms must remain blocked until current Confirmed Fee exists for the latest Matrix/rule context.

## Validation Strategy Across Subtasks

Run targeted tests in each subtask and expand only when integration is introduced.

Minimum eventual validation set:

```powershell
py -m pytest tests/unit/test_matrix_fee_draft_rebase_service.py -q
py -m pytest tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py tests/integration/test_fee_evaluation_pricing_draft_api.py -q
py -m pytest tests/unit/test_matrix_editor_session_service.py tests/integration/test_matrix_editor_session_api.py -q
py -m pytest tests/unit/test_confirmed_fee_version_service.py tests/integration/test_confirmed_fee_version_api.py -q
py -m pytest tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_folder_required_forms_service.py tests/integration/test_project_folder_required_forms_api.py -q
cd frontend
npm test -- --run FeeEvaluationReviewExportPage MatrixEditorWorkspace projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout --watch=false
npm run build
```

## Stop Point

This umbrella plan stops at subtask definition. The next allowed action, if separately approved, is implementation of `TASK_315A_MATRIX_TO_FEE_REBASE_CORE` only.
