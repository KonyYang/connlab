# TASK_246_MATRIX_EDITOR_COMPACT_FIXED_WIDTH_TABLE

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_246_MATRIX_EDITOR_COMPACT_FIXED_WIDTH_TABLE`.

## Why This Task Is Allowed Now

User smoke-tested TASK_245 and found the table-level minimum width made the first six columns too wide, hiding even the single required group column in the visible area.

User requested:

- use the per-column minimum width as the actual fixed width
- do not keep the table-level 1180px minimum when only a few group columns exist

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend CSS-only correction to the previous Matrix Editor width task.
- Bounded to Matrix Editor main table sizing.
- No backend/API/domain/persistence changes.
- Static tests can lock the regression fix.

## Objective

Correct Matrix Editor table sizing so the default two-row, one-group grid shows at least the first group column without the first six columns expanding beyond their intended fixed widths.

## Scope

Allowed:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- Matrix save/load contract changes
- initial seed data changes
- row/group operation changes
- visual redesign outside table width behavior

## Acceptance Criteria

- Remove the Matrix Editor table-level `min-width: max(1180px, 100%)` behavior.
- Keep per-column fixed widths for row selector, first 5 definition columns, and group columns.
- Use the per-column minimum widths as the fixed column widths.
- Prevent the first six columns from stretching to fill a large table minimum.
- Preserve horizontal scrolling when many group columns exceed the visible area.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task246 or matrix_editor"
```

Result: passed (`23 passed`, `69 deselected`).
