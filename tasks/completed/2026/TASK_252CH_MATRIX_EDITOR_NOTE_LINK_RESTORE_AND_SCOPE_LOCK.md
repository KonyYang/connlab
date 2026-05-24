# TASK_252CH_MATRIX_EDITOR_NOTE_LINK_RESTORE_AND_SCOPE_LOCK

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_252CH_MATRIX_EDITOR_NOTE_LINK_RESTORE_AND_SCOPE_LOCK`.

## Why This Task Is Allowed Now

- `docs/task_board.md` shows no active task and requires explicit user approval before next Matrix Editor task.
- User explicitly requested rollback correction after over-revert and chose full rebuild path (`1`).
- This task is a bounded recovery/hardening slice for the existing Matrix Editor import + Step preview note behavior, without introducing new domains.

## Model Fit Assessment

`GPT-5.3-codex` with `high` reasoning is suitable.

Reason:

- Requires careful restoration of previously validated behavior under a dirty workspace.
- Includes parser-note mapping edge cases (step token markers, section/item markers, samples markers) and UI presentation constraints.
- Must avoid another over-broad revert and preserve existing unrelated edits.

## Objective

Restore and lock the previously accepted behavior for Matrix note display and linkage:

1. Keep marker-bearing source tokens visible in main matrix cells (e.g., `3(a)`, `14(c)`, `5*`).
2. Keep Step preview note cards separated by origin:
   - `Step Notes` for step-token markers only.
   - `Item/Section Notes` for Test Item / Section marker notes only.
   - `Samples Notes` for sample quantity markers only.
3. Ensure per-step note linkage is exact (only steps that actually carry markers get those notes).
4. Keep Samples line editable and same-row layout (`Samples` + input), preserving full literal token text (e.g., `5+(5e)/5+(5e)/5+(5e)`).
5. Ensure marker-based fallback survives step-number edits (e.g., `10(a)` -> `14(a)` keeps `(a)` note link).
6. Remove accidental cross-card leakage and over-display regressions introduced by rollback/rebuild churn.

## Scope

Allowed:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/services/*` and/or DTO mapper files only if required for note payload wiring
- `backend/api/routes_project_test_plan.py` only if response schema mapping requires restoration
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/api/client.ts` (typed contracts only)
- `frontend/src/workbench.css` (minimal style adjustments only)
- tests directly covering parser/API/frontend shell assertions
- task/plan/board documentation updates

Forbidden:

- new import file formats (`.doc`/PDF/Excel)
- persistence/model redesign
- runtime execution domain expansion
- unrelated UI redesign
- broad git restore/reset operations

## Acceptance Criteria

1. Main grid preserves marker-bearing visible token text (no forced numeric-only simplification for matrix cells).
2. Step preview `Step Notes` contains only notes linked to currently visible steps that actually carry step-token markers.
3. Step preview `Item/Section Notes` contains only item/section marker notes for referenced steps, formatted concisely.
4. No "any note in row => all steps in row show note" behavior.
5. Samples row in Step preview shows `Samples` label + editable input on same row; input keeps literal sample expression with markers.
6. `Samples Notes` appears only when sample marker notes exist.
7. Marker note linkage survives step renumbering when marker suffix remains unchanged.
8. Regression checks pass for both user-provided `.docx` samples:
   - `GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`
   - `GS-12-1507 RA Coplanar Rev7 (3).docx`

## Validation

Backend targeted:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

Frontend targeted:

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task252 or matrix_editor or samples or notes"
```

Manual smoke:

1. Import both reference `.docx` files.
2. Verify marker tokens are visible in matrix cells.
3. Select groups with mixed noted/unnoted step usage; verify note cards show only correct origins.
4. Edit a step token number keeping same marker suffix; verify note linkage remains.
5. Verify samples input and samples notes behavior.
