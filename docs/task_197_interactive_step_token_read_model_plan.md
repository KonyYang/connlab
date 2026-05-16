# TASK_197 Interactive Step Token Read Model Plan

> Created: 2026-05-16  
> Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`  
> Proposed task: `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL`  
> Status: Plan for review. No implementation is approved by this document.

## 1. Current Phase And Task Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task state from `docs/task_board.md`:

```text
TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION complete
Next recommended action: define and approve TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL
```

Why TASK_197 is allowed now:

- TASK_194 established product governance for the Matrix-driven Laboratory Execution Phase.
- TASK_195 established Runtime Console information architecture and runtime attention hierarchy.
- TASK_196 established Step-centric domain foundation and the Runtime Projection Boundary.
- The task board explicitly recommends defining and approving TASK_197 next.

Current gap:

- `tasks/TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL.md` does not exist yet.
- This plan proposes creating that task file and the corresponding read-model boundary document only after user approval.

## 2. Task Purpose

TASK_197 defines the minimum projection foundation for Interactive Step Tokens.

It is not a complete runtime system. It is a documentation, governance, and read-model boundary task.

Core rule:

```text
Projection != Domain Identity
```

Interactive Step Token is a runtime projection surface. It is not a domain authority object.

## 3. Inputs

TASK_197 should use these existing governance documents as inputs:

- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/step_centric_domain_foundation.md`
- `docs/task_board.md`
- `PRODUCT.md`
- `DESIGN.md`
- `DESIGN.json`

The user-provided TASK_197 constraints are also authoritative for this plan:

- Matrix Overview, Step Token, Runtime Console, Runtime Attention, Report Sync Marker, and Group Runtime Status are Runtime Projection / Read Model concepts.
- Step identity can only come from Project + Matrix authority + Group identity + Sequence/token.
- Runtime projection must not pollute Step identity, Matrix authority, or Project lifecycle.

## 4. Outputs

After approval, TASK_197 should create:

- `tasks/TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL.md`
- `docs/interactive_step_token_read_model_projection_foundation.md`

It may update:

- `docs/task_board.md`
- static governance guard tests, only if needed to accept the new board state.

It must not create or modify:

- backend runtime source files;
- database models or migrations;
- API routes or schemas;
- frontend components;
- CSS or visual implementation;
- persistence repositories;
- report sync engines;
- evidence or image storage.

## 5. Required Content Scope

The TASK_197 document should define these ten areas.

### 5.1 Interactive Step Token Projection Model

Define Step Token as a composed runtime projection with:

- stable identity reference;
- lifecycle projection;
- data completeness projection;
- evidence/image projection;
- report sync projection;
- freshness/stale projection;
- runtime attention projection;
- navigation target into Step Workspace.

The token is only the operator-facing projection result.

### 5.2 Runtime Projection Sources

Define conceptual sources:

- Matrix authority definition;
- group identity;
- step sequence/token parsing result;
- future Step lifecycle state;
- future execution data completeness;
- future evidence/image state;
- future report/output sync state;
- future runtime attention priority;
- project lifecycle context.

These sources can be combined for display, but they retain separate ownership.

### 5.3 Projection Aggregation Rules

Define how a token projection conceptually combines multiple state dimensions:

- identity first;
- authority context second;
- execution lifecycle third;
- integrity gaps fourth;
- output sync fifth;
- setup completeness last unless it blocks execution.

Aggregation answers:

```text
What should the operator see and enter now?
```

It does not answer:

```text
What is this step as a durable domain object?
```

### 5.4 Projection Ownership Boundaries

Define source ownership:

- Project owns lifecycle and traceability context.
- Matrix authority owns what should be tested.
- StepInstance owns future execution state and execution data.
- Derived outputs own output lineage and freshness.
- Runtime Projection owns display composition only.
- UI Token owns no business truth.

### 5.5 Runtime Read Model Boundaries

Define the read model as a consumer-facing projection model.

It may be optimized for Workbench display and navigation, but it must not become:

- persistence authority;
- Matrix authority;
- Step identity;
- report source of truth;
- frontend-only business state.

### 5.6 Projection Refresh And Stale Concepts

Define conceptual freshness without implementing a refresh engine:

- projection current against Matrix authority;
- projection stale against newer Step lifecycle/data/evidence/output state;
- projection unavailable because source is missing;
- projection partial because some source dimensions are not implemented yet;
- projection superseded because Matrix authority changed.

Freshness is a property of the projection, not a rewrite of domain identity.

### 5.7 Projection Versus Authority Separation

Make explicit that:

- Matrix authority defines executable obligations.
- Step identity references Matrix authority, group, and sequence/token.
- Runtime projection visualizes current operational meaning.
- UI token color, badge, priority, stale marker, report sync marker, and selected state cannot redefine identity.

### 5.8 Matrix Projection Relationship

Define Matrix Overview as:

- runtime projection surface;
- navigation map;
- attention summary surface;
- group and token status projection.

Matrix Overview is not:

- Excel-like editor;
- runtime source of truth;
- StepInstance object graph;
- report sync engine;
- status mutation surface.

### 5.9 Step Workspace Selection Relationship

Define selection as a projection-to-workspace navigation relationship:

- token selection identifies the referenced step identity;
- Step Workspace receives the identity reference plus projection context;
- Step Workspace resolves or displays execution details in later tasks;
- selection state itself is not domain state.

### 5.10 Future Runtime Implementation Slices

Define future task slices without implementing them:

1. read-model DTO/API design;
2. Step identity persistence;
3. Step lifecycle persistence;
4. evidence/image state projection;
5. report sync projection;
6. attention priority evaluation;
7. Matrix Overview UI projection;
8. Step Workspace runtime UI.

These slices must remain separately approved tasks.

## 6. Explicit Non-Scope

TASK_197 must not implement:

- persistence;
- ORM models;
- Python dataclasses;
- API endpoints;
- runtime engine;
- priority engine;
- notification system;
- frontend components;
- React or CSS behavior;
- SQLite schema;
- report sync engine;
- evidence or image storage;
- StepInstance implementation.

TASK_197 also must not rewrite existing Matrix parsing or Matrix Editor behavior.

## 7. Planned File-Level Changes After Approval

### 7.1 `tasks/TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL.md`

Create the task contract:

- goal;
- scope;
- inputs;
- deliverables;
- out-of-scope list;
- acceptance criteria;
- validation plan.

### 7.2 `docs/interactive_step_token_read_model_projection_foundation.md`

Create the main governance document:

- Step Token projection model;
- projection source map;
- aggregation and ownership rules;
- stale/freshness concepts;
- Matrix Overview relationship;
- Step Workspace selection relationship;
- future implementation slices.

### 7.3 `docs/task_board.md`

After TASK_197 completion, update:

- status;
- last updated date;
- deliverables;
- validation summary;
- next recommended task.

### 7.4 Static Governance Tests

Update only if existing tests require the new task-board state. No behavioral tests are expected because this is documentation/governance only.

## 8. Risks And Controls

Risk: Step Token gets treated as the StepInstance object.

Control: The document must repeat that token is projection output, while identity comes from Project + Matrix authority + Group identity + Sequence/token.

Risk: Matrix Overview drifts back into an Excel-like editor.

Control: Define Matrix Overview as runtime projection and navigation surface, not definition editing.

Risk: runtime badges or attention priority become hidden domain state.

Control: Define badges, priority, stale markers, and report markers as projection dimensions only.

Risk: TASK_197 accidentally starts implementation.

Control: Limit changes to task/document/board/static governance tests.

## 9. Validation Plan

Document validation:

- confirm the created task file exists;
- confirm the projection foundation document exists;
- confirm all ten required content areas are covered;
- confirm forbidden implementation areas are explicitly out of scope;
- confirm no backend/frontend runtime source files were intentionally changed.

Optional static guard validation:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

No backend, frontend, database, or API runtime tests are required unless the board/static governance tests are updated.

## 10. Approval Gate

This plan stops before implementation.

Implementation of TASK_197 should begin only after the user explicitly approves this plan.
