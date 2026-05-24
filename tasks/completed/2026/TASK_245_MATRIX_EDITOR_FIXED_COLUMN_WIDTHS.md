# TASK_245_MATRIX_EDITOR_FIXED_COLUMN_WIDTHS

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_245_MATRIX_EDITOR_FIXED_COLUMN_WIDTHS`.

## Why This Task Is Allowed Now

User requested a bounded Matrix Editor table width correction after TASK_244:

- the first Matrix definition columns should keep stable widths
- group columns should keep stable widths
- widths should not shrink as group count increases
- the width baseline should match the previously acceptable 12-group layout

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend CSS-only table sizing correction with static test coverage.
- Bounded to Matrix Editor table area.
- No backend/API/domain/persistence changes.
- No workflow, data model, or structural operation changes.

## Objective

Fix Matrix Editor table sizing so columns remain stable when more group columns are added:

1. Keep the left row selector width stable.
2. Keep the first 5 definition columns stable:
   - `Test Item`
   - `Section`
   - `Method`
   - `Condition`
   - `Requirement`
3. Keep every group column stable.
4. When group columns exceed the visible area, use horizontal scrolling instead of compressing columns.

## Scope

Allowed:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- Matrix save/load contract changes
- row/group operation changes
- initial seed data changes
- layout redesign outside Matrix Editor table sizing

## Acceptance Criteria

- Matrix table column rules use fixed `width` plus `min-width` for:
  - row selector column
  - first 5 definition columns
  - group columns
- Group columns keep the existing 12-group baseline width, not proportional shrink.
- Matrix table can exceed the visible grid surface and rely on horizontal overflow.
- Existing Matrix Editor visual states and validation classes remain unchanged.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task245 or matrix_editor"
```

Result: passed (`22 passed`, `69 deselected`).
