# TASK_216_MATRIX_AUTHORITY_TO_RUNTIME_CONSOLE_SYNC_CONTRACT_AND_NAVIGATION_SLICE

## Status

Approved and executed on 2026-05-17.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Why This Task Is Allowed Now

TASK_215 is complete and there is no active task. The user approved the next controlled implementation slice to reduce practical split between Matrix definition editing and Workbench runtime projection consumption, while preserving governance boundaries.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it is a bounded frontend/runtime-consumer integration slice with existing API surfaces and no StepInstance/runtime engine/persistence scope.

## Objective

Define and implement a minimal, consumable authority-sync and navigation contract between:

- Project Workbench Runtime Console (runtime projection consumer)
- Matrix definition editing surface (Matrix Editor page)

without turning either surface into domain source-of-truth mutation layers.

## Scope

Allowed:

- Add a dedicated Matrix Editor route/page for project-scoped matrix definition editing.
- Reuse existing matrix draft update/validate/confirm APIs.
- Add Workbench runtime authority-sync visibility:
  - authority version
  - candidate draft presence/version
  - runtime projection matrix reference
  - sync/stale indication
- Add Workbench to Matrix Editor navigation entry and Matrix Editor back-to-Workbench navigation.
- Handle selected token stale/missing case safely after projection refresh by clearing invalid selection.
- Update `docs/task_board.md` and static board-state guard tests.

Forbidden:

- StepInstance implementation/persistence
- runtime engine/orchestration
- lifecycle persistence
- DB schema/migrations/ORM changes
- backend runtime mutation service
- report sync engine
- evidence storage engine
- React table virtualization or unrelated UI redesign

## Acceptance Criteria

- Workbench shows matrix authority/runtime projection sync contract summary.
- Workbench exposes an `Edit Matrix Definition` action that opens a dedicated Matrix Editor page.
- Matrix Editor page exists at a project-scoped route and supports existing draft edit/validate/confirm flow.
- Runtime token selection is cleared when selected token no longer exists in refreshed projection.
- No backend schema/API contract breaking changes introduced.
- `npm run build` passes.
- static board-state governance tests pass.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```
