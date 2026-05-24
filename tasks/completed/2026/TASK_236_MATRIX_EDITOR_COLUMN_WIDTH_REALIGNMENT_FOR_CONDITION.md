# TASK_236_MATRIX_EDITOR_COLUMN_WIDTH_REALIGNMENT_FOR_CONDITION

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_236_MATRIX_EDITOR_COLUMN_WIDTH_REALIGNMENT_FOR_CONDITION`.

## Why This Task Is Allowed Now

User requested Matrix grid column width adjustment for real operator usage:

- Narrow `Test Item`, `Section`, `Method`
- Widen `Condition`

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only CSS/layout refinement.
- No business logic, backend, API, or data model changes.

## Objective

Rebalance Matrix main table widths so `Condition` has more horizontal space while preserving existing editing and selection behavior.

## Scope

Allowed:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (static guard update if needed)
- task file and board update

Forbidden:

- backend/API/domain changes
- matrix editing logic changes
- workbench routing/workflow changes

## Acceptance Criteria

- `Test Item`, `Section`, `Method` widths are reduced.
- `Condition` width is increased.
- `Requirement` and group columns remain usable and visible.
- No regression in row/column selection, context menu, or inline editing.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task236 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task236 or task235 or matrix_editor"` passed (`15 passed`, `69 deselected`).
