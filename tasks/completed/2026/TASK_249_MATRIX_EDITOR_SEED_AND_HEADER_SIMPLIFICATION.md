# TASK_249_MATRIX_EDITOR_SEED_AND_HEADER_SIMPLIFICATION

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Why This Task Was Allowed

User explicitly approved `docs/task_249_matrix_editor_seed_and_header_simplification_plan.md`.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Bounded frontend-only UI simplification.
- No backend/API/domain/persistence impact.
- Existing static checks can lock the expected source changes.

## Objective

Align Matrix Editor edit area with requested target:

1. Initial group display name `G1 -> 1`
2. Remove selection hint strip (`Selection: none` and structural reminder copy)
3. Remove top grid toolbar (`Matrix Version / Group / Filter / Section`)

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`

Forbidden:

- Backend/API/domain/persistence changes
- Matrix structural rules and step validation behavior changes
- Workbench/runtime console behavior changes

## Implementation Summary

- Updated `buildInitialGroupColumns()` to seed `name: "1"`.
- Removed grid-toolbar JSX block from Matrix Editor edit area.
- Removed selection hint JSX block from Matrix Editor table wrapper.
- Updated frontend static assertions:
  - TASK_243 initial group-name expectation now checks `name: "1"`.
  - TASK_224 no longer asserts removed structural reminder copy.
  - Added TASK_249 assertion ensuring removed labels/copy no longer appear.

## Validation

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task249 or task244 or task243 or task224 or matrix_editor"
```

Result: `25 passed, 69 deselected`.

## Risks / Notes

- `setLastMessage` state setter is retained for structural-action feedback flows, but the previous on-screen selection/status strip is intentionally removed by scope.
