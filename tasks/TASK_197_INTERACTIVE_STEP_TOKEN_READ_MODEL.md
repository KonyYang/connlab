# TASK_197 Interactive Step Token Read Model

## Status

done

## Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Goal

Define the Interactive Step Token Read Model Projection Foundation for the Matrix-driven Laboratory Execution Phase.

This task is documentation, governance, and read-model boundary only. It does not implement a runtime system.

Core rule:

```text
Projection != Domain Identity
```

Additional governance rule:

```text
Projection layers must remain independently replaceable.
```

## Context

TASK_194 established:

- product governance;
- Matrix-driven Laboratory Execution Phase;
- `Matrix is the execution authority map, Project remains the lifecycle container.`

TASK_195 established:

- Workbench Runtime Console information architecture;
- runtime attention hierarchy;
- Matrix Overview as runtime projection and navigation surface.

TASK_196 established:

- Step-centric domain foundation;
- conceptual StepInstance identity;
- Runtime Projection Boundary.

TASK_197 now defines the minimum read-model foundation for Interactive Step Tokens so future runtime implementation does not mix projection state with domain identity.

## In Scope

Define:

1. Interactive Step Token projection model.
2. Runtime projection sources.
3. Projection aggregation rules.
4. Projection ownership boundaries.
5. Runtime read model boundaries.
6. Projection refresh/stale concepts.
7. Projection versus authority separation.
8. Matrix projection relationship.
9. Step Workspace selection relationship.
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
- report sync engine;
- evidence/image storage;
- notification system;
- StepInstance implementation.

Do not rewrite:

- Matrix Editor behavior;
- Matrix parsing implementation;
- existing Workbench UI;
- existing output ledger behavior.

## Required Boundaries

Step identity comes only from:

```text
Project
+ Matrix authority
+ Group identity
+ Sequence/token
```

The following are projection dimensions only:

- UI token;
- badge;
- stale marker;
- report sync marker;
- runtime attention;
- selected state;
- evidence marker;
- lifecycle display marker;
- group runtime status.

They must not redefine or pollute:

- Step identity;
- Matrix authority;
- Project lifecycle.

Runtime Projection is not source of truth.

## Deliverables

- `docs/interactive_step_token_read_model_projection_foundation.md`
- `docs/task_197_interactive_step_token_read_model_plan.md`
- `tasks/TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL.md`
- `docs/task_board.md` update

## Acceptance Criteria

- The projection foundation document exists and defines the ten required scope areas.
- The document explicitly states `Projection != Domain Identity`.
- The document explicitly states `Runtime Projection is not source of truth.`
- The document defines `Projection layers must remain independently replaceable.`
- Step identity is anchored to Project + Matrix authority + Group identity + Sequence/token.
- UI token, badge, stale marker, report sync marker, runtime attention, and selected state are documented as projection dimensions only.
- No backend, frontend, API, ORM, SQLite, persistence, runtime engine, report sync engine, evidence/image storage, notification, or StepInstance implementation is added.

## Validation

Document-level consistency check:

- Confirm the task file exists.
- Confirm the projection foundation document exists.
- Confirm task board records TASK_197 completion.
- Confirm no backend/frontend runtime source files were intentionally changed.

Static governance guard tests:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

