# TASK_239_MATRIX_EDITOR_CELL_EDIT_AUTO_SELECT_GROUP

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Objective

When editing any group step cell, auto-select its group column so the whole group column highlight is visible.

## Scope

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- board update only

## Validation

```powershell
cd frontend
npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task239 or matrix_editor"
```
