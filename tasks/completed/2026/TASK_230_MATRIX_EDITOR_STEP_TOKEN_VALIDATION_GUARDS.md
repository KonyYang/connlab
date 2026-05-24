# TASK_230_MATRIX_EDITOR_STEP_TOKEN_VALIDATION_GUARDS

## Status

Complete. Implemented and validated on 2026-05-19.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_230_MATRIX_EDITOR_STEP_TOKEN_VALIDATION_GUARDS`.

## Why This Task Is Allowed Now

User requested Matrix grid-only validation rules for per-group step token editing behavior and error highlighting.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only validation and UI feedback update.
- No backend/API/domain model change required.
- Existing group-name validation UI pattern can be reused.

## Objective

1. Step cells default to blank (not `-`) when no step is defined.
2. Step cell content format allows only digits and comma separators.
3. Per group, aggregated step numbers across all rows must:
   - start from `1`
   - be continuous with no gaps
   - have no duplicates
4. Violations show high-visibility inline error state and status strip message, aligned with group-name guard style.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css` (reuse/add validation styles)
- `tests/unit/test_frontend_shell_files.py` (targeted static assertions)
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- Workbench page changes
- unrelated redesign

## Acceptance Criteria

- Empty step token cells are blank by default.
- Invalid token character format is highlighted.
- Group-level sequence errors (not starting at 1, gaps, duplicates) are highlighted.
- Status strip shows clear validation error message.
- Existing row/group structural operations remain functional.
- Build and targeted static tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task230 or matrix_editor or task229"
```

Result:

- `cd frontend; npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task230 or matrix_editor or task229"` passed (`9 passed`, `69 deselected`).
