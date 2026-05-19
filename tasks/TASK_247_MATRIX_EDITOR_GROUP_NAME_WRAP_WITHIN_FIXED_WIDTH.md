# TASK_247_MATRIX_EDITOR_GROUP_NAME_WRAP_WITHIN_FIXED_WIDTH

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_247_MATRIX_EDITOR_GROUP_NAME_WRAP_WITHIN_FIXED_WIDTH`.

## Why This Task Is Allowed Now

User smoke-tested the fixed-width Matrix Editor group column and found a group name such as `11,12` does not fit cleanly inside the fixed 44px group header input.

User requested:

- do not increase group column width
- allow the group name content to wrap earlier when it cannot fit in one line

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend CSS-only correction.
- Bounded to Matrix Editor group header input rendering.
- No backend/API/domain/persistence changes.
- Static tests can lock the no-width-increase and wrap behavior.

## Objective

Update Matrix Editor group name input display so short multi-token group names can wrap inside the existing fixed-width group column instead of clipping or forcing a wider column.

## Scope

Allowed:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- changing group column width
- backend/API/domain/persistence changes
- group name validation rule changes
- row/group operation changes
- initial seed data changes
- broad visual redesign

## Acceptance Criteria

- Group column width remains unchanged at the existing fixed width.
- `.matrix-editor-group-name-input` no longer forces `white-space: nowrap`.
- Group name text can wrap within the existing fixed-width input.
- Text overflow ellipsis is removed or neutralized for group name input.
- Existing group-name validation colors and focus styles remain unchanged.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

Result: passed.

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task247 or matrix_editor"
```

Result: passed (`24 passed`, `69 deselected`).
