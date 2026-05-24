# TASK_252CP_MATRIX_EDITOR_SAMPLES_ROW_VERTICAL_ALIGN_AND_TOKEN_WRAP

## Status

Approved and in implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CP_MATRIX_EDITOR_SAMPLES_ROW_VERTICAL_ALIGN_AND_TOKEN_WRAP`

## Why This Task Is Allowed Now

- User explicitly approved a bounded Matrix Editor UI fix for:
  - `Samples Quantity (PCS)` vertical centering
  - full visibility of sample expressions like `5+(5e)` without changing global group column width
- Scope is frontend-only and does not expand domain/runtime behavior.

## Objective

1. Vertically center the `Samples Quantity (PCS)` row label cell.
2. Avoid clipping of sample expressions in group cells by allowing wrapped display in the sample-row editor.
3. Keep existing matrix compact column widths unchanged.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task/board docs updates

Forbidden:

- backend/parser/API changes
- global group-column width changes
- unrelated Matrix behavior changes
