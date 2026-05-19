# TASK_240_MATRIX_EDITOR_NEW_ROW_EMPTY_FIELD_GUARDS

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_240_MATRIX_EDITOR_NEW_ROW_EMPTY_FIELD_GUARDS`.

## Why This Task Is Allowed Now

User requested visual validation guards for newly added/edited rows:

- first 5 base fields should show red border when empty
- row with all group step cells empty should show reminder/highlight

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only validation UX addition.
- Bounded to matrix grid rendering and local state.
- No backend/API/domain/persistence changes.

## Objective

Add row-level empty-field warning cues:

1. For each row, base columns `item/section/method/condition/requirement`:
   - empty -> red bordered input style
2. For each row, when all group step cells are empty:
   - show row-level warning cue on step cells (or row warning style) to remind operator that no step is defined.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain changes
- matrix model changes
- report/test-record changes

## Acceptance Criteria

- Empty base fields in first 5 columns get visible red border styling.
- Row with all-empty group step cells gets visible warning cue.
- Existing group sequence/format validation remains functional.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task240 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task240 or task239 or matrix_editor"` passed (`19 passed`, `69 deselected`).
