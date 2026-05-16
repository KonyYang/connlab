# TASK_203 Documentation Information Architecture Cleanup

Status: Slice A, Slice B, Slice C, and Slice D complete
Date: 2026-05-16

## Goal

Align ConnLab Markdown documentation so current source-of-truth, historical records, task plans, and archive material are easier to distinguish.

This task is documentation-only. It does not implement backend, frontend, API, DB, runtime, UI, Matrix Editor, StepInstance, report sync, evidence storage, or workflow behavior.

## Approved Scope

Slice A:

- Create `docs/README.md` as the documentation map and read-order.
- Create `docs/archive/README.md` explaining archive semantics.
- Update root `README.md` to point to current control documents.
- Update `docs/03_DOMAIN_MODEL.md` from MVP-only model to current domain snapshot.
- Update `docs/04_API_CONTRACTS.md` from MVP-only contracts to current API surface snapshot.
- Update `docs/07_FUTURE_EXTENSION_MAP.md` so Matrix-driven execution is no longer treated as generic future scope.
- Update `docs/task_board.md` after completion.

Slice B:

- Move external AI modification notes to `docs/archive/external_ai/`.
- Move old phase-wide plans to `docs/archive/historical_plans/`.
- Move the historical packed blueprint to `docs/archive/legacy_blueprints/`.
- Update references and static governance tests for moved paths.

Slice C:

- Decide task-plan archive strategy.
- Keep `docs/task_XXX_*_plan.md` files in place.
- Add a central index and usage rule for task plan files.

Slice D:

- Slim `docs/task_board.md` by archiving long historical completion-note chains.
- Keep current phase/status/source-of-truth and active governance sections in `docs/task_board.md`.
- Add archive pointer for moved history notes.

## Explicitly Out Of Scope

- Moving `tasks/`.
- Moving `docs/task_XXX_*_plan.md`.
- Deleting archived historical blueprints or external AI notes.
- Slimming `docs/task_board.md`.
- Encoding/mojibake cleanup.
- Runtime implementation.
- API implementation.
- Frontend implementation.

## Governance

This task follows:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/runtime_governance_freeze_rule.md`
- `docs/task_203_documentation_information_architecture_cleanup_plan.md`

## Validation

Run static governance tests:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Run documentation reference checks:

```powershell
Select-String -Path README.md,PRODUCT.md,docs\*.md -Pattern "MVP API Contracts","MVP Domain Model","outside MVP"
```
