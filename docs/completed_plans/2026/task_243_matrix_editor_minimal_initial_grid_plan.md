# TASK_243 Matrix Editor Minimal Initial Grid Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_243_MATRIX_EDITOR_MINIMAL_INITIAL_GRID`
- Allowed now: user requested this specific Matrix Editor initialization behavior.

## Goal

Make a fresh Matrix Editor open with the minimum usable Matrix structure:

- 1 test item row
- 1 group column

## Minimal Change Design

Current initialization uses sample constants:

- many `GROUP_COLUMNS`
- many `MATRIX_ROWS`
- sample group token values

Planned change:

1. Keep sample constants only if needed by other surfaces, but do not seed initial editor state with full sample matrix.
2. Change `buildInitialGroupColumns()` to return one group column.
3. Change `buildInitialMatrixRows()` to return one blank editable row with one blank group value.
4. Keep `buildEmptyRow()` and structural operations unchanged.
5. Keep existing empty-field and missing-step warnings active so the blank initial row is guided, not silently valid.

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- adjust initial seed helpers only
- do not change row/group operation functions

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_243 static checks for one-row/one-group initialization and blank group value.

## Risks

- Header metrics still show static old counts (`Groups`, `Steps`, `Items`). This task does not change metrics unless necessary; if visible mismatch is unacceptable, open a follow-up task for metric derivation.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task243 or matrix_editor"
```

## Out Of Scope

- backend persistence
- Matrix import/template behavior
- dynamic metrics overhaul
