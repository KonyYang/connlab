# TASK_228_MATRIX_EDITOR_COLUMN_HEADER_DIRECT_CONTEXT_MENU

## Status

Complete. Implemented and validated on 2026-05-18.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_228_MATRIX_EDITOR_COLUMN_HEADER_DIRECT_CONTEXT_MENU`.

## Why This Task Is Allowed Now

After `TASK_227`, user feedback indicates the A/B/C index row is visually misleading and consumes space. The user approved replacing it with direct column selection and right-click actions on group headers.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only Matrix grid interaction refinement.
- Reuses existing column selection and context-menu operation logic.
- No backend/API/domain/workbench changes.

## Objective

1. Remove the A/B/C index row from Matrix grid header.
2. Use each group header as the only column operation entry.
3. Keep editable group names in header.
4. Click group header selects whole column.
5. Right-click group header opens column context menu.
6. Preserve row selection, row context menu, inline editing, and structural guards.

## Scope

Allowed:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` targeted assertions
- task file and board updates

Forbidden:

- backend changes
- API contract changes
- domain model changes
- persistence changes
- Workbench page changes
- unrelated UI redesign

## Acceptance Criteria

- No A/B/C index row in table header.
- Group header keeps editable name input.
- Left click group header selects and highlights whole column.
- Right click group header opens group context menu.
- Header input still editable without breaking selection/menu behavior.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task228 or task227 or task226"
```

Result:

- `cd frontend; npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task228 or task227 or task226"` passed (`3 passed`, `73 deselected`).
