# TASK_227_MATRIX_EDITOR_EDITABLE_GROUP_HEADER_AND_COLUMN_INDEX

## Status

Complete. Implemented and validated on 2026-05-18.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_227_MATRIX_EDITOR_EDITABLE_GROUP_HEADER_AND_COLUMN_INDEX`.

## Why This Task Is Allowed Now

The user requested a Matrix Editor grid-only refinement after `TASK_226`: make group header names editable for business naming, add Excel-like column index letters to improve row/column targeting, and keep right-click structural actions.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only local table interaction changes.
- Reuses existing row/column selection and context-menu structure operations.
- No backend/API/domain model changes.

## Objective

1. Group header display names (`G1` etc.) must be editable inline.
2. Add a dedicated column index row using `A, B, C, ...` as selector/locator.
3. Keep column selection via click and right-click menu operations.
4. Row index behavior from `TASK_226` remains.
5. New group columns should default to empty display name (user fills manually).

## Scope

Allowed:

- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (targeted assertions)
- task file and board updates

Forbidden:

- backend changes
- API contract changes
- domain model changes
- persistence changes
- Workbench page changes
- unrelated UI redesign

## Acceptance Criteria

- Group header name is editable inline.
- A/B/C... column index row exists and can be used to select/right-click columns.
- Right-click column operations still work (insert/duplicate/move/delete).
- New group column name starts as empty.
- Row selector column and row highlight behavior still work.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task227 or task226 or task225"
```

Result:

- `cd frontend; npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task227 or task226 or task225"` passed (`3 passed`, `72 deselected`).
