# TASK_243_MATRIX_EDITOR_MINIMAL_INITIAL_GRID

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_243_MATRIX_EDITOR_MINIMAL_INITIAL_GRID`.

## Why This Task Is Allowed Now

User requested Matrix Editor initialization to show only the minimal valid editing structure instead of the current populated sample matrix:

- one effective test item row
- one group column

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only initialization/default-state adjustment.
- Bounded to Matrix Editor local draft seed data.
- No backend/API/domain/persistence changes.

## Objective

Change Matrix Editor initial grid data so a fresh Matrix Editor shows:

1. one editable base row
2. one editable group column
3. blank step value by default
4. existing validation cues continue to guide missing base fields and missing step number

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- Matrix save/load contract changes
- layout redesign
- Step preview rule changes

## Acceptance Criteria

- Initial `groupColumns` contains exactly one group.
- Initial `editableRows` contains exactly one row.
- New initial row has blank base fields and blank group step value.
- Existing add/insert/duplicate/delete row/group operations still work.
- Existing minimum-structure guards still work.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task243 or matrix_editor"
```

Result: passed (`20 passed`, `69 deselected`).
