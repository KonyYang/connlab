# TASK_233_MATRIX_EDITOR_STEP_DESCRIPTION_SPECIAL_RULES

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_233_MATRIX_EDITOR_STEP_DESCRIPTION_SPECIAL_RULES`.

## Why This Task Is Allowed Now

User provided explicit business rules for special Step Description generation in Matrix Editor Step preview:

- Base default remains Matrix `Test Item`.
- Special rule families (`LLCR`, `IR`, `DWV`, `mating/un-mating`) use staged description text by group step order.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- Frontend-only rule enrichment over existing Step preview derivation.
- Deterministic string rules with bounded scope and no backend/persistence changes.

## Objective

Add deterministic special description defaults in Step preview for rows whose `Test Item` matches configured families:

1. If a special-family item appears once in selected group:
   - `Step Description = <Family Name>` (e.g., `LLCR`)
2. If it appears multiple times in selected group (by step number ascending):
   - first = `Initial <Family Name>`
   - last = `Final <Family Name>`
   - middle = `After <previous step Test Item>`
3. `previous step` means previous numeric step in same selected group (not previous special-family row).
4. If previous-step `Test Item` is empty in a middle case:
   - fallback to `<Family Name>`

Apply same rule family behavior for:

- `LLCR`
- `IR`
- `DWV`
- `mating/un-mating`

Alias extension requirement:

- family matching must support synonyms/aliases (e.g., `CR`, `Low level contact resistance` for LLCR).
- implement via a dedicated alias mapping structure (not hard-coded scattered conditions), so future aliases can be added in one place.
- current task keeps alias map in frontend local scope only; no backend/API contract change.

## Scope

Allowed:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_frontend_shell_files.py`
- `frontend/src/workbench.css` only if no-op/minor text fit adjustment is required
- task file and board update

Forbidden:

- backend/API/domain/persistence changes
- matrix model changes
- report/test-record logic changes
- AI or probabilistic rule inference

## Acceptance Criteria

- Existing Step preview behavior from TASK_232 remains (no `Test Item` column, `Requirement` from matrix requirement, `Step Description` editable).
- For matched special families, default `Step Description` follows the staged rule above.
- Rule runs per selected group and per family.
- Alias mapping entry point exists so new names can be added without changing rule flow.
- Non-matched rows still default `Step Description` to Matrix `Test Item`.
- Manual user override in Step preview continues to take precedence.
- Build and targeted tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task233 or task232 or matrix_editor"
```

Result:

- `npm run build` passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task233 or task232 or task231 or matrix_editor"` passed (`12 passed`, `69 deselected`).
