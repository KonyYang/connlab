# TASK_198 Runtime Projection Service And Read Model Boundary Plan

> Created: 2026-05-16  
> Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`  
> Proposed task: `TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY`  
> Status: Plan for review. No implementation is approved by this document.

## 1. Current Phase And Task Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task board state:

```text
TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL complete
Current Active Task: none; TASK_197 interactive step token read model complete, pending next controlled implementation task
```

Why TASK_198 planning is allowed now:

- TASK_194 established Matrix-driven product governance.
- TASK_195 established Runtime Console information architecture.
- TASK_196 established Step-centric domain foundation.
- TASK_197 established Interactive Step Token read-model projection boundaries.
- The user explicitly approved entering TASK_198 plan preparation.

Governance note:

- `docs/task_board.md` currently recommends `TASK_198_WORKBENCH_RUNTIME_CONSOLE_UI_BASELINE`.
- The user has now redirected TASK_198 to `TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY`.
- This plan treats that as a controlled task-direction correction to be recorded during formal TASK_198 execution after approval.

## 2. Task Purpose

TASK_198 should define the Runtime Projection Service Boundary.

This does not mean implementing a service. It means documenting the future service's responsibility boundary so later implementation does not collapse projection composition into domain identity, Matrix authority, UI state, cache state, or runtime engine behavior.

Core rules:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
```

New TASK_198 governance principle:

```text
Projection composition must remain independently evolvable.
```

Meaning:

- projection aggregation;
- attention evaluation;
- report sync projection;
- evidence projection;
- stale calculation;
- group summary projection;

must be able to evolve independently without breaking:

- Step identity;
- Matrix authority;
- Project lifecycle ownership;
- Runtime projection boundary.

## 3. Inputs

TASK_198 should use:

- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/step_centric_domain_foundation.md`
- `docs/interactive_step_token_read_model_projection_foundation.md`
- `docs/task_board.md`
- `docs/task_197_interactive_step_token_read_model_plan.md`

The user-provided TASK_198 prompt is also an authoritative input.

## 4. Outputs

Current plan stage may create only:

- `docs/task_198_runtime_projection_service_and_read_model_boundary_plan.md`

After approval, formal TASK_198 execution may create:

- `tasks/TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY.md`
- `docs/runtime_projection_service_and_read_model_boundary.md`

After approval, formal TASK_198 execution may update:

- `docs/task_board.md`
- static governance tests, only if needed for board-state acceptance.

## 5. Explicit Non-Scope

TASK_198 must not implement:

- backend runtime implementation;
- ORM or dataclasses;
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

TASK_198 must not create actual service classes, repositories, schemas, routes, or frontend consumers.

## 6. Required Content Scope

The TASK_198 body document should define these ten areas.

### 6.1 Runtime Projection Composition Responsibility

Define Runtime Projection composition as the conceptual responsibility for combining source-owned state into operator-facing read models.

It should compose:

- identity references from Project, Matrix authority, group, and step token;
- lifecycle projections;
- data/evidence projections;
- report/output projections;
- stale/freshness projections;
- runtime attention projections;
- group summary projections.

It must not own source truth.

### 6.2 Projection Aggregation Flow

Define an aggregation flow such as:

1. read identity and authority references;
2. attach Matrix/group/step technical context;
3. attach lifecycle/data/evidence projection dimensions;
4. attach report/output freshness dimensions;
5. attach stale/invalidation indicators;
6. attach runtime attention ranking;
7. emit read models for Matrix Overview and Step Workspace consumption.

This flow is conceptual. It is not an engine, algorithm, cache, API, or implementation.

### 6.3 Projection Refresh/Stale Boundary

Define refresh/stale as projection freshness, not domain mutation.

The document should clarify:

- stale projection means the view may not reflect current source dimensions;
- stale state does not alter Step identity;
- stale state does not supersede Matrix authority;
- stale state does not advance or block Project lifecycle by itself;
- stale state should guide user attention and future refresh behavior.

### 6.4 Projection Invalidation Concepts

Define conceptual invalidation triggers without implementing invalidation:

- Matrix authority change;
- Step lifecycle change;
- execution data change;
- evidence/image state change;
- report/output generation or import;
- source material change;
- Project lifecycle change;
- setup status change when it affects runtime attention.

Invalidation is a signal that projection should be rebuilt or marked stale. It is not a persistence model or cache engine.

### 6.5 Projection Service Ownership

Define ownership boundaries:

- Runtime Projection Service owns composition rules and read-model boundary.
- It does not own Project lifecycle.
- It does not own Matrix authority.
- It does not own Step lifecycle or execution data.
- It does not own evidence/image storage.
- It does not own report generation or sync.
- It does not own UI selection state.

### 6.6 Read-Model Boundary Versus Domain Boundary

Clarify the difference:

- domain objects answer what exists and what owns source truth;
- read models answer what the operator should see now;
- runtime projections answer how multiple source states are composed;
- UI state answers what is selected, expanded, focused, or filtered.

These layers must remain separate.

### 6.7 Matrix Overview Projection Consumption Model

Define Matrix Overview as a projection consumer:

- consumes group runtime summary;
- consumes step token projections;
- consumes attention/stale/report/evidence markers;
- consumes selected-step target references.

It must not become:

- source of truth;
- Matrix definition editor;
- status mutation engine;
- report sync engine;
- evidence storage surface.

### 6.8 Step Workspace Projection Consumption Model

Define Step Workspace as a detailed projection consumer:

- consumes selected identity reference;
- consumes current projection context;
- displays lifecycle/data/evidence/report/attention context in future tasks;
- routes to future domain actions only through separately approved tasks.

Selection remains projection/UI state. It cannot create or redefine Step identity.

### 6.9 Projection Source Dependency Map

Define a conceptual source dependency map:

- Project lifecycle and traceability;
- Matrix authority and group/step definition;
- future Step lifecycle and execution data;
- future evidence/image state;
- output ledger and report/test-record/fee/approval freshness;
- runtime attention model;
- setup/support status.

The map should show dependency direction from source-owned state to projection composition, not from projection back to source truth.

### 6.10 Future Runtime Implementation Slices

Define future implementation slices without implementing them:

1. runtime projection read-model DTO/API design;
2. Step identity persistence;
3. Step lifecycle persistence;
4. evidence/image projection provider;
5. report sync projection provider;
6. stale/freshness calculation provider;
7. runtime attention provider;
8. group summary projection provider;
9. Runtime Projection Service implementation;
10. Matrix Overview projection consumer implementation;
11. Step Workspace projection consumer implementation.

Each slice requires a separate approved task.

## 7. Planned File-Level Changes After Approval

### 7.1 `tasks/TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY.md`

Create the task contract:

- goal;
- context;
- in scope;
- out of scope;
- required boundaries;
- acceptance criteria;
- validation.

### 7.2 `docs/runtime_projection_service_and_read_model_boundary.md`

Create the main governance document:

- runtime projection composition responsibility;
- aggregation flow;
- refresh/stale boundary;
- invalidation concepts;
- service ownership;
- read-model versus domain boundary;
- Matrix Overview and Step Workspace consumption models;
- projection source dependency map;
- future implementation slices.

### 7.3 `docs/task_board.md`

After formal TASK_198 completion, update:

- task status;
- current active task line;
- deliverables;
- validation summary;
- next recommended task.

This update should also correct the TASK_198 direction from UI baseline to Runtime Projection Service Boundary if approved.

### 7.4 Static Governance Tests

Update only if existing board-state tests need the new current task text.

## 8. Risks And Controls

Risk: Runtime Projection Service is mistaken for a runtime engine.

Control: Define it as a boundary and composition responsibility only, with no implementation in TASK_198.

Risk: Projection composition becomes source of truth.

Control: Repeat that Project, Matrix, Step, evidence, and outputs own their source states; projection only composes display/read state.

Risk: projection aggregation, attention, stale, report sync, and evidence logic become tightly coupled.

Control: Add the principle that projection composition must remain independently evolvable.

Risk: Matrix Overview or Step Workspace consume projection as if it were domain truth.

Control: Define both as projection consumers and require future domain actions to route through separately approved tasks.

Risk: TASK_198 drifts into UI or service implementation.

Control: Limit formal execution to task document, governance document, task board update, and static governance tests.

## 9. Validation Plan

Plan-stage validation:

- confirm this plan file exists;
- confirm it does not create runtime implementation;
- confirm it documents the task-board naming correction.

Formal TASK_198 validation after approval:

- confirm the TASK_198 task file exists;
- confirm the runtime projection boundary document exists;
- confirm the ten required content areas are covered;
- confirm `Projection != Domain Identity` is present;
- confirm `Runtime Projection is not source of truth` is present;
- confirm `Projection composition must remain independently evolvable` is present;
- confirm forbidden implementation areas remain untouched.

Optional static governance guard command after formal execution:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 10. Approval Gate

This plan stops before TASK_198 formal execution.

Do not create `tasks/TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY.md`, do not create `docs/runtime_projection_service_and_read_model_boundary.md`, and do not update `docs/task_board.md` until the user explicitly approves this plan.
