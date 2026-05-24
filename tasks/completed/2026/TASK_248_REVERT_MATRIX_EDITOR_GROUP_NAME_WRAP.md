# TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_248_REVERT_MATRIX_EDITOR_GROUP_NAME_WRAP`.

## Why This Task Is Allowed Now

User reviewed TASK_247 and requested reverting the most recent group-name wrapping change because the visual effect was not acceptable.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Small frontend CSS rollback.
- Bounded to the last Matrix Editor group name input wrapping change.
- No backend/API/domain/persistence changes.
- Existing static tests can be updated to lock the rollback behavior.

## Objective

Revert TASK_247 behavior for Matrix Editor group header names:

- restore single-line group name input behavior
- restore overflow clipping/ellipsis behavior
- keep all fixed group column widths from TASK_246

## Scope

Allowed:

- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- changing group column width
- reverting TASK_246 fixed column width behavior
- backend/API/domain/persistence changes
- group name validation rule changes
- row/group operation changes
- initial seed data changes

## Acceptance Criteria

- `.matrix-editor-group-name-input` uses `white-space: nowrap`.
- `.matrix-editor-group-name-input` uses `overflow: hidden`.
- `.matrix-editor-group-name-input` uses `text-overflow: ellipsis`.
- TASK_247 wrapping assertions are removed or converted to TASK_248 rollback assertions.
- Group column fixed width remains unchanged at `44px`.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task248 or matrix_editor"
```

Result:

- `npm run build` passed.
- Targeted static checks passed: `25 passed, 69 deselected`.
