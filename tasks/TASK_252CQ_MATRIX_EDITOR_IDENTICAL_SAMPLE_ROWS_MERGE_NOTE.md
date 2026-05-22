# TASK_252CQ_MATRIX_EDITOR_IDENTICAL_SAMPLE_ROWS_MERGE_NOTE

## Status

Approved and in implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CQ_MATRIX_EDITOR_IDENTICAL_SAMPLE_ROWS_MERGE_NOTE`

## Why This Task Is Allowed Now

- User explicitly approved merging identical multi-row sample quantities and surfacing the merge source in right-side Samples notes.
- Scope is frontend-only and uses existing Matrix preview row data.

## Objective

1. Collapse identical imported sample rows into one displayed sample value per group.
2. Show a right-side Samples note indicating merged source rows, such as `Header / Rec. / Rec+ Cable share the same sample quantity.`
3. Preserve existing marker sample notes such as `(d)` / `(e)`.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`

Forbidden:

- backend/API schema changes
- global matrix column width changes
- unrelated Matrix Editor changes
