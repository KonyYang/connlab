# TASK_252CL_MATRIX_EDITOR_STEP_NOTES_PREFIX_COVERAGE_AND_CARD_VISUAL_RESTORE

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CL_MATRIX_EDITOR_STEP_NOTES_PREFIX_COVERAGE_AND_CARD_VISUAL_RESTORE`

## Why This Task Is Allowed Now

- User explicitly requested three bounded Matrix Editor refinements after TASK_252CK:
  1) Step Notes lines must include step token prefix (for example `3(a)`),
  2) note extraction/mapping coverage must be validated and completed for `GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx` remark set,
  3) Step Notes / Item-Section / Samples regions must have independent card background separation similar to target screenshot.
- Scope remains controlled within existing parser + Matrix Editor preview display.

## Model Fit Assessment

`GPT-5.3-codex` with `high` reasoning is suitable.

## Objective

1. Step Notes display each note with its mapped step token prefix (`3(a) ...`, `10(c) ...`).
2. Ensure A2 document remark markers `(a)..(e)` are parsed and correctly routed to step/sample note cards when referenced by selected group tokens.
3. Restore clear card-level visual separation with independent background colors for note cards.

## Scope

Allowed:

- `backend/modules/test_plan/product_spec_matrix_parser.py` (only if parser coverage gap is confirmed)
- `tests/unit/test_product_spec_matrix_parser.py`
- `tests/integration/test_project_test_plan_preview_api.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- task/plan/board documentation updates

Forbidden:

- New format support (`.doc`, `.pdf`, OCR, AI parsing)
- Runtime domain/persistence redesign
- Unrelated Matrix layout restructuring

## Acceptance Criteria

1. Step Notes lines include step token prefix, e.g. `3(a) Precondition ...`.
2. For A2-like marker set `(a)..(e)`, parser extracts all referenced marker notes; mapped note cards are not truncated by format mismatch.
3. Item/Section Notes remain concise (`Step N | Section:...`) while preserving mapped note body.
4. Note cards have distinct visual backgrounds:
   - Step Notes card (light warm tone),
   - Item/Section card (light cool tone),
   - Samples card (neutral tone).
5. Relevant tests and frontend build pass.

## Validation

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252cl or matrix_editor"
```

```powershell
cd frontend
npm run build
```
