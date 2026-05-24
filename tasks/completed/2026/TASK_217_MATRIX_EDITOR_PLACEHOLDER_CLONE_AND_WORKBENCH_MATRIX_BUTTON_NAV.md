# TASK_217_MATRIX_EDITOR_PLACEHOLDER_CLONE_AND_WORKBENCH_MATRIX_BUTTON_NAV

## Status

Approved and executed on 2026-05-17.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Why This Task Is Allowed Now

TASK_216 completed authority-sync/navigation contract. The user explicitly requested a placeholder-first Matrix Editor screen closer to the target mockup and asked that the right-side Workbench `Matrix` button opens this page.

## Model Fit Assessment

`GPT-5.3-codex` is suitable because this is a bounded frontend navigation + static placeholder UI slice with no backend/runtime engine/persistence scope.

## Objective

1. Wire the Workbench Step Workspace right-side `Matrix` button to open Matrix Editor.
2. Replace current Matrix Editor content with a mockup-style static placeholder layout (no functional matrix editing implementation required).

## Scope

Allowed:

- Frontend route navigation changes.
- Static placeholder page structure and styles.
- Task board state update and static board guard tests.

Forbidden:

- Backend/API contract changes.
- DB/ORM/migrations.
- StepInstance/runtime engine/report sync/evidence engine changes.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```
