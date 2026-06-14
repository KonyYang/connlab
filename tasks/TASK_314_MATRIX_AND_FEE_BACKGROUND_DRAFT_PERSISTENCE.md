# TASK_314_MATRIX_AND_FEE_BACKGROUND_DRAFT_PERSISTENCE

Status: Split accepted. Do not implement as one combined task.

Historical executable plan: `docs/task_314_matrix_and_fee_background_draft_persistence_plan.md`

Current replacement tasks:

- `TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE`
- `TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE` (deferred; task file not created yet)
- `TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION` (deferred; task file not created yet)

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

## Split Decision

The original TASK_314 goal is still valid, but it combines two deep implementation areas:

1. Matrix Editor draft persistence:
   - session draft save / restore / discard
   - Confirm Matrix draft id and payload signature validation
   - Matrix Editor autosave, cancel discard, and confirm gating

2. Fee Evaluation draft persistence:
   - pricing draft autosave
   - pricing draft discard
   - removal of the normal-flow `Save changes` button
   - Confirm Fee disabled-state rules

These areas share a product principle, but they do not need to be implemented in one execution task.

## Current Direction

Execute the split in controlled slices:

### TASK_314A: Matrix Editor draft persistence

Task file: `tasks/TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE.md`

Plan: `docs/task_314a_matrix_editor_draft_persistence_plan.md`

TASK_314A is the immediate controlled task. It is the true prerequisite for `TASK_315_MATRIX_DRAFT_TO_FEE_DRAFT_INCREMENTAL_REBASE`, because TASK_315 needs Matrix autosave, Matrix draft discard, and Confirm Matrix saved-draft gating.

### TASK_314B: Fee Evaluation background draft persistence

Deferred.

Expected future scope:

- pricing draft autosave
- pricing draft discard endpoint
- removal of `Save changes` from the normal Fee Evaluation flow
- Confirm Fee disabled while dirty/pending/failed/stale

TASK_314B is useful for workflow consistency, but it is not required before TASK_315.

### TASK_314C: Linkage regression

Deferred.

Expected future scope:

- verify TASK_318 Official project folder check remains intact
- verify TASK_320 single-task Workbench UI remains intact
- verify TASK_321 Required forms generation remains intact
- verify Confirmed Matrix / Confirmed Fee readiness effects remain coherent after TASK_314A and TASK_314B

## Governance Rule

Do not implement this umbrella TASK_314 directly.

If existing worktree changes attempted the original combined TASK_314, review them against TASK_314A first. Keep Matrix-only changes that match TASK_314A after validation, and defer or remove Fee Evaluation autosave changes unless a later TASK_314B is explicitly approved.

## Stop Point

Stop after creating/reviewing the TASK_314A task file and executable plan unless the user explicitly approves TASK_314A implementation.
