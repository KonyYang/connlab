# TASK_234_MATRIX_EDITOR_REQUIREMENT_SPLIT_RULES

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_234_MATRIX_EDITOR_REQUIREMENT_SPLIT_RULES`.

## Why This Task Is Allowed Now

User requested Requirement optimization in Step preview for repeated special-family steps, aligned with existing Step Description staged logic.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only deterministic text split/refinement.
- Reuses existing selected-group step derivation and family matching.
- No backend/API/domain/persistence changes.

## Objective

Add staged default Requirement filling for special families (starting with LLCR; reusable for IR/DWV/mating where patterns apply):

1. If matrix requirement has `Initial ...; After ...` pattern:
   - first matching step -> `Initial ...`
   - remaining matching steps -> normalized `After` segment content
2. If matrix requirement has `Initial ...; After test: ∆R ...` pattern:
   - first -> `Initial ...`
   - remaining -> `∆R ...`
3. If no split pattern is recognized:
   - keep original matrix requirement default.
4. Manual Requirement override remains highest priority.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- matrix model changes
- report/test-record changes
- AI/NLP parsing

## Acceptance Criteria

- Requirement defaults for repeated LLCR-like steps can split into first/remaining segments based on deterministic `Initial`/`After` patterns.
- Handles `After test <= ...` and `After test: ...` forms by removing leading `After...` label in remaining segment output.
- Non-matching requirement formats remain unchanged.
- Existing Step Description staged logic and manual overrides remain intact.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task234 or task233 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task234 or task233 or task232 or matrix_editor"` passed (`13 passed`, `69 deselected`).
