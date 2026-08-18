# TASK_314 Matrix And Fee Background Draft Persistence Umbrella Plan

Status: Split accepted. Superseded for implementation by TASK_314A/TASK_314B/TASK_314C.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Split Summary

The original TASK_314 plan captured the right product goal:

- preserve unfinished Matrix Editor and Fee Evaluation edits as non-authority drafts
- publish authority only through explicit `Confirm Matrix` / `Confirm Fee`
- make `Cancel` / `Cancel edits` explicitly discard unconfirmed drafts

However, the plan bundled two deep subsystems into one execution unit. The accepted split is:

```text
TASK_314A = Matrix Editor draft persistence
TASK_314B = Fee Evaluation background draft persistence
TASK_314C = Matrix/Fee/Project Folder regression pass
```

## Replacement Implementation Path

### TASK_314A

Task file:

```text
tasks/TASK_314A_MATRIX_EDITOR_DRAFT_PERSISTENCE.md
```

Executable plan:

```text
docs/task_314a_matrix_editor_draft_persistence_plan.md
```

TASK_314A implements:

- Matrix Editor session seed restore from current Matrix draft
- Matrix Editor autosave draft endpoint
- Matrix Editor discard endpoint
- Confirm Matrix draft id/signature validation
- Matrix Editor autosave/cancel/confirm gating

TASK_314A is the true prerequisite for TASK_315.

### TASK_314B

Complete. Implemented after separate explicit approval.

Task file: `tasks/TASK_314B_FEE_EVALUATION_BACKGROUND_DRAFT_PERSISTENCE.md`

Plan: `docs/task_314b_fee_evaluation_background_draft_persistence_plan.md`

Completed scope:

- Fee Evaluation pricing draft autosave
- pricing draft discard endpoint
- removal of normal-flow `Save changes`
- Confirm Fee disabled while dirty/pending/failed/stale

### TASK_314C

Complete. Implemented after separate explicit approval.

Task file: `tasks/TASK_314C_MATRIX_FEE_PROJECT_FOLDER_REGRESSION.md`

Plan: `docs/task_314c_matrix_fee_project_folder_regression_plan.md`

Completed scope:

- regression verification for Confirmed Matrix/Fee authority behavior
- TASK_318 Official project folder check
- TASK_320 single-task Workbench UI
- TASK_321 Required forms generation

## Governance Notes

- Do not implement the combined TASK_314 as a single task.
- Do not treat Fee Evaluation autosave as required for TASK_315.
- Do not implement TASK_315 without separate explicit approval.
- If existing worktree changes include combined TASK_314 implementation, review and narrow them against TASK_314A before continuing.

## Stop Point

This umbrella plan is retained only as split rationale and historical context.

Use `docs/task_314a_matrix_editor_draft_persistence_plan.md`, `docs/task_314b_fee_evaluation_background_draft_persistence_plan.md`, and `docs/task_314c_matrix_fee_project_folder_regression_plan.md` as completed split-slice history.
