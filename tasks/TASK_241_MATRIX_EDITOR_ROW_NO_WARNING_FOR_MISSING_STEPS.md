# TASK_241_MATRIX_EDITOR_ROW_NO_WARNING_FOR_MISSING_STEPS

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_241_MATRIX_EDITOR_ROW_NO_WARNING_FOR_MISSING_STEPS`.

## Why This Task Is Allowed Now

User requested refinement of empty-step guidance:

- remove row-wide group-cell warning style
- instead highlight `No.` row index cell and show hover hint `缺少步骤编号`

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only cue adjustment.
- Bounded behavior/presentation change.
- No backend/API/domain changes.

## Objective

Replace row-wide empty-step warning with row-number warning cue:

1. Detect rows where all group step cells are empty.
2. Apply warning style to row selector (`No.`) cell/button only.
3. Add hover tooltip message: `缺少步骤编号`.
4. Remove/stop using row-wide step-empty input style for this scenario.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain changes
- matrix model changes
- step token validation logic changes

## Acceptance Criteria

- All-group-empty row no longer paints all group step cells with warning style.
- Row `No.` cell clearly indicates warning state.
- Hover on row `No.` warning target shows `缺少步骤编号`.
- Existing base-field empty warning and step format/sequence validation remain functional.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task241 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task241 or task240 or matrix_editor"` passed (`19 passed`, `69 deselected`).
