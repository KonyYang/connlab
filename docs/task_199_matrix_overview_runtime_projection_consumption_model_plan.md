# TASK_199 Matrix Overview Runtime Projection Consumption Model Plan

> Created: 2026-05-16  
> Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`  
> Proposed task: `TASK_199_MATRIX_OVERVIEW_RUNTIME_PROJECTION_CONSUMPTION_MODEL`  
> Status: Plan for review. No implementation is approved by this document.

## 1. Current Phase And Task Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task board state:

```text
TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY complete
Current Active Task: none; TASK_198 runtime projection service boundary complete, pending next controlled implementation task
Next recommended action: define and approve TASK_199_MATRIX_OVERVIEW_RUNTIME_PROJECTION_CONSUMPTION_MODEL
```

Why TASK_199 planning is allowed now:

- TASK_194 established Matrix-driven product governance.
- TASK_195 established Runtime Console information architecture.
- TASK_196 established Step-centric domain foundation.
- TASK_197 established Interactive Step Token projection/read-model foundation.
- TASK_198 established Runtime Projection Service and read-model boundary.
- The user explicitly approved entering TASK_199 plan preparation.

## 2. Task Goal

One-sentence goal:

```text
Define how Matrix Overview consumes runtime projection/read-model outputs as a navigation and attention surface, without becoming domain authority, runtime engine, or UI implementation.
```

TASK_199 remains:

```text
documentation/governance/consumer-boundary only
```

It is not a UI implementation task and not a runtime implementation task.

## 3. Core Governance Rules

TASK_199 must preserve:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
Projection composition must remain independently evolvable.
```

Matrix Overview is a projection consumer. It is not:

- Matrix authority;
- Step identity owner;
- Project lifecycle owner;
- runtime engine;
- read-model implementation;
- status mutation surface;
- report sync engine;
- evidence storage surface.

## 4. Inputs

TASK_199 should use:

- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/step_centric_domain_foundation.md`
- `docs/interactive_step_token_read_model_projection_foundation.md`
- `docs/runtime_projection_service_and_read_model_boundary.md`
- `docs/task_board.md`

The user-provided TASK_199 prompt is also authoritative.

## 5. Plan-Stage Output

This plan stage may create only:

- `docs/task_199_matrix_overview_runtime_projection_consumption_model_plan.md`

This plan stage must not create:

- `tasks/TASK_199_MATRIX_OVERVIEW_RUNTIME_PROJECTION_CONSUMPTION_MODEL.md`
- `docs/matrix_overview_runtime_projection_consumption_model.md`

This plan stage must not update:

- `docs/task_board.md`
- backend files;
- frontend files;
- API files;
- database/schema files;
- tests.

## 6. Explicit Non-Scope

TASK_199 must not implement:

- React component implementation;
- CSS/table implementation;
- frontend behavior changes;
- backend runtime implementation;
- API/DTO design;
- DB/schema/migration;
- runtime read-model implementation;
- projection service implementation;
- StepInstance implementation;
- report sync implementation;
- evidence/image implementation.

TASK_199 must not create:

- UI components;
- table models;
- frontend hooks;
- backend services;
- route handlers;
- DTO classes;
- persistence models;
- projection algorithms.

## 7. Required Content Scope

The future TASK_199 body document should define these ten areas.

### 7.1 Matrix Overview Consumes Runtime Projection Only

Define Matrix Overview as a projection consumer:

- it reads runtime projection/read-model outputs;
- it displays authority context, group summaries, and step token projections;
- it supports navigation and attention surfacing;
- it does not own source truth.

It must not mutate or redefine:

- Step identity;
- Matrix authority;
- Project lifecycle;
- source evidence;
- report/output freshness.

### 7.2 Matrix Cell, Step Token, And Group Summary Projection Reading

Define how Matrix Overview conceptually reads projection at three levels:

- Matrix cell:
  - consumes cell-level token projection and technical context;
  - does not remain a raw Excel-like string authority.
- Step token:
  - consumes identity reference plus projection dimensions;
  - does not become StepInstance.
- Group summary:
  - consumes aggregate projection;
  - does not become group identity or runtime source truth.

### 7.3 Token Marker Display Responsibility Boundary

Define token markers as visual/read-model indicators only.

Token markers may represent:

- lifecycle projection;
- attention priority;
- stale/freshness state;
- report sync state;
- evidence/data state;
- selected navigation target.

Markers must not:

- mutate status;
- create execution state;
- redefine identity;
- become backend truth;
- imply report/evidence operations.

### 7.4 Group Runtime Status Aggregation Consumption Boundary

Define group runtime status as consumed aggregate projection.

Group runtime status may summarize:

- highest active attention priority;
- active/blocked/failed steps;
- missing evidence/data;
- stale report/output markers;
- current selection context.

It must not become:

- group identity;
- Matrix authority;
- Step lifecycle source;
- execution engine state.

### 7.5 Marker Consumption Order

Define Matrix Overview marker consumption order:

1. authority/identity availability;
2. execution-blocking attention;
3. execution integrity attention;
4. stale/freshness conflict;
5. report sync risk;
6. evidence/data gap;
7. setup completeness marker;
8. selected/hover/display state.

The order is an information architecture rule, not UI styling or algorithm implementation.

### 7.6 Matrix Overview And Step Workspace Selection Relationship

Define selection as navigation from Matrix Overview projection to Step Workspace projection.

Selection carries:

- Project reference;
- Matrix authority reference;
- group identity reference;
- step sequence/token reference;
- current projection summary.

Selection must not create or mutate:

- StepInstance;
- execution data;
- Matrix authority;
- Project lifecycle;
- report sync state;
- evidence state.

### 7.7 Entering Step Workspace

Define when Matrix Overview should route to Step Workspace:

- user selects a valid step token;
- the token has enough identity reference to resolve a future step context;
- execution attention belongs to a specific step;
- evidence/data/report issue belongs to a specific step;
- user needs detailed step-level runtime context.

If identity is incomplete, route should indicate an authority/definition issue instead of pretending a Step Workspace exists.

### 7.8 Routing To Setup Manager, Output Status, Or Matrix Editor

Define routing rules:

- Setup Manager:
  - setup completeness issue;
  - folder/source/supporting material state;
  - approval package preparation state.
- Output Status:
  - report/test-record/fee/approval output freshness;
  - derived-output stale/current/manual/failed state.
- Matrix Editor:
  - missing Matrix authority;
  - group identity issue;
  - sequence/token definition issue;
  - technical definition issue requiring definition change.

Matrix Overview routes based on projection meaning. It does not perform the mutation.

### 7.9 Anti Excel-Like Editor Boundary

Define what Matrix Overview must not become:

- Excel-like editor;
- bulk cell editor;
- string authority surface;
- definition mutation surface;
- template import surface.

Definition changes belong to Matrix Editor or a future Matrix change request flow.

### 7.10 Forbidden Runtime/Object Ownership Boundary

Define explicit non-ownership:

- not StepInstance object graph;
- not runtime engine;
- not status mutation surface;
- not report sync engine;
- not evidence storage surface;
- not projection service implementation;
- not cache or invalidation owner.

Matrix Overview consumes projection and routes attention. It does not own runtime state.

## 8. Planned File-Level Changes After Approval

After user approval, formal TASK_199 execution may create:

### 8.1 `tasks/TASK_199_MATRIX_OVERVIEW_RUNTIME_PROJECTION_CONSUMPTION_MODEL.md`

Create the task contract:

- goal;
- context;
- in scope;
- out of scope;
- required boundaries;
- acceptance criteria;
- validation.

### 8.2 `docs/matrix_overview_runtime_projection_consumption_model.md`

Create the main governance document:

- Matrix Overview as runtime projection consumer;
- Matrix cell / Step token / Group summary projection consumption;
- token marker responsibility;
- group runtime status boundary;
- marker consumption order;
- Step Workspace selection relationship;
- routing rules to Step Workspace, Setup Manager, Output Status, and Matrix Editor;
- anti Excel-like editor boundary;
- forbidden runtime/object ownership boundary.

### 8.3 `docs/task_board.md`

After TASK_199 completion, update:

- task status;
- current active task line;
- deliverables;
- validation summary;
- next recommended action.

### 8.4 Static Governance Tests

Update only if existing board-state tests require the new current task text.

## 9. Risks And Controls

Risk: Matrix Overview becomes a UI implementation task.

Control: TASK_199 stays documentation/governance/consumer-boundary only and forbids React/CSS/table implementation.

Risk: Matrix Overview becomes an Excel-like editor again.

Control: Explicitly define it as a projection consumer and navigation/attention surface, not a definition mutation surface.

Risk: token markers become status mutation or source truth.

Control: Define markers as projection dimensions only.

Risk: group runtime status becomes group identity or execution engine state.

Control: Define group status as aggregate projection consumption only.

Risk: routing rules imply backend or frontend behavior implementation.

Control: Define routing as conceptual IA responsibility only; future behavior requires separately approved tasks.

## 10. Validation Plan

Plan-stage validation:

- confirm this plan file exists;
- confirm no TASK_199 body file was created;
- confirm `docs/task_board.md` was not updated;
- confirm no backend/frontend/API/DB files were modified;
- confirm the plan includes the three core governance rules;
- confirm the plan states that TASK_199 completion does not automatically enter TASK_200.

Formal TASK_199 validation after approval:

- confirm TASK_199 task file exists;
- confirm Matrix Overview consumption model document exists;
- confirm all ten required content areas are covered;
- confirm explicit non-implementation boundaries are present;
- run static governance tests only if board-state tests are updated.

## 11. Approval Gate

This plan stops before TASK_199 formal execution.

Do not create `tasks/TASK_199_MATRIX_OVERVIEW_RUNTIME_PROJECTION_CONSUMPTION_MODEL.md`, do not create `docs/matrix_overview_runtime_projection_consumption_model.md`, and do not update `docs/task_board.md` until the user explicitly approves this plan.

TASK_199 completion must not automatically enter TASK_200. TASK_200 requires a separate user request, plan, and approval.
