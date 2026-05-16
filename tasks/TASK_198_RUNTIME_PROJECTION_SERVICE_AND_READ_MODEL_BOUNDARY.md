# TASK_198 Runtime Projection Service And Read Model Boundary

## Status

done

## Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Goal

Define the Runtime Projection Service and read-model boundary for future Matrix-driven laboratory execution work.

This task is documentation, governance, and runtime-boundary only. It does not implement a runtime projection service, read-model API, cache, engine, schema, or UI.

Core rules:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
```

Additional governance rule:

```text
Projection composition must remain independently evolvable.
```

## Context

TASK_194 established product governance:

- Matrix-driven Laboratory Execution Phase;
- `Matrix is the execution authority map, Project remains the lifecycle container.`

TASK_195 established:

- Runtime Console information architecture;
- runtime attention priority;
- Matrix Overview and Step Workspace responsibilities.

TASK_196 established:

- Step-centric domain foundation;
- conceptual StepInstance identity;
- Runtime Projection Boundary.

TASK_197 established:

- Interactive Step Token read-model projection foundation;
- projection layers as replaceable dimensions;
- UI token, badge, stale marker, report sync marker, runtime attention, selected state, evidence projection, and group runtime status as projection only.

TASK_198 now defines the future Runtime Projection Service boundary without implementing the service.

## In Scope

Define:

1. Runtime projection composition responsibility.
2. Projection aggregation flow.
3. Projection refresh/stale boundary.
4. Projection invalidation concepts.
5. Projection service ownership.
6. Read-model boundary versus domain boundary.
7. Matrix Overview projection consumption model.
8. Step Workspace projection consumption model.
9. Projection source dependency map.
10. Future runtime implementation slices.

## Out Of Scope

Do not implement:

- backend runtime implementation;
- ORM or dataclass implementation;
- persistence;
- SQLite schema;
- API endpoints or DTOs;
- React components;
- CSS or frontend behavior;
- runtime engine;
- cache engine;
- projection engine;
- report sync implementation;
- evidence/image implementation;
- notification implementation;
- StepInstance implementation.

Do not create:

- service classes;
- repositories;
- database migrations;
- route handlers;
- frontend hooks;
- component consumers;
- cache invalidation code.

## Required Boundaries

Runtime Projection Service is a future boundary for composing read models. It must not become source truth.

Source truth remains owned by:

- Project lifecycle and traceability;
- Matrix authority and group/step definition;
- future Step lifecycle and execution data;
- future evidence/image storage;
- output ledger and derived-output lineage.

Runtime Projection composition may consume those sources in future tasks, but it must not mutate or redefine them.

## Deliverables

- `docs/runtime_projection_service_and_read_model_boundary.md`
- `docs/task_198_runtime_projection_service_and_read_model_boundary_plan.md`
- `tasks/TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY.md`
- `docs/task_board.md` update

## Acceptance Criteria

- The Runtime Projection Service boundary document exists.
- The document defines the ten required content areas.
- The document explicitly states `Projection != Domain Identity`.
- The document explicitly states `Runtime Projection is not source of truth.`
- The document defines `Projection composition must remain independently evolvable.`
- The document distinguishes projection composition from domain authority, persistence, runtime engines, cache engines, and UI state.
- Matrix Overview and Step Workspace are documented as projection consumers, not source-of-truth owners.
- No backend, frontend, API, ORM, SQLite, persistence, runtime engine, cache engine, projection engine, report sync, evidence/image, notification, or StepInstance implementation is added.

## Validation

Document-level consistency check:

- Confirm the TASK_198 task file exists.
- Confirm the runtime projection boundary document exists.
- Confirm task board records TASK_198 completion.
- Confirm no backend/frontend runtime source files were intentionally changed.

Static governance guard tests:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

