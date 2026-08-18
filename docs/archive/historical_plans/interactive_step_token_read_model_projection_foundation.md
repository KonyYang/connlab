# Interactive Step Token Read Model Projection Foundation

> Created: 2026-05-16  
> Task: `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL`  
> Scope: Documentation, governance, and read-model boundary only. No runtime implementation.

## 1. Purpose

This document defines the minimum read-model projection foundation for Interactive Step Tokens in ConnLab's Matrix-driven Laboratory Execution Phase.

It exists to prevent future runtime work from mixing:

- domain identity;
- Matrix authority;
- Project lifecycle;
- runtime projection;
- UI selection;
- derived-output sync markers.

Core rule:

```text
Projection != Domain Identity
```

Runtime Projection is not source of truth.

Additional governance rule:

```text
Projection layers must remain independently replaceable.
```

This means report sync projection, runtime attention projection, stale projection, evidence projection, and lifecycle projection must be replaceable in future implementation without changing Step identity, Matrix authority, or Project lifecycle ownership.

## 2. Authority Baseline

Approved product principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Authority ownership:

- `Project` owns lifecycle identity, LTR, source traceability, folder state, and overall project readiness.
- `Matrix authority` owns what should be tested.
- `Group identity` owns the group position inside one Matrix authority.
- `StepInstance` is the future domain execution object for lifecycle and execution data ownership.
- `Runtime Projection` owns display composition only.
- `Interactive Step Token` is a runtime projection surface.

Step identity comes only from:

```text
Project
+ Matrix authority
+ Group identity
+ Sequence/token
```

It must not come from:

- UI token color;
- badge text;
- stale marker;
- report sync marker;
- runtime attention priority;
- evidence marker;
- selected state;
- frontend projection state.

## 3. Interactive Step Token Projection Model

An Interactive Step Token is the operator-facing projection result for one executable step reference.

It should eventually project:

- identity reference:
  - project;
  - Matrix authority version;
  - group identity;
  - sequence number;
  - token variant or suffix.
- technical context:
  - test item;
  - section;
  - method;
  - condition;
  - requirement;
  - source trace.
- lifecycle projection:
  - not started;
  - ready;
  - in progress;
  - blocked;
  - pass;
  - fail;
  - retest required;
  - waived or not applicable.
- data completeness projection;
- evidence/image projection;
- report sync projection;
- freshness/stale projection;
- runtime attention projection;
- selection/navigation target.

The token answers:

```text
What should the operator see and enter now?
```

It does not answer:

```text
What is this step as a durable domain object?
```

## 4. Runtime Projection Sources

The read model may combine multiple future sources.

Identity and authority sources:

- Project identity;
- Matrix authority version;
- group identity;
- parsed sequence/token;
- source Matrix row context.

Runtime sources:

- Step lifecycle state;
- execution data completeness;
- evidence/image state;
- failure/disposition state;
- comments or review markers;
- runtime attention priority.

Derived-output sources:

- report sync state;
- test record freshness;
- fee evaluation freshness;
- approval package freshness;
- output lineage.

Setup and lifecycle context:

- Project lifecycle state;
- current readiness projection;
- setup completeness when it affects runtime attention.

These sources may be composed into one token projection, but each source retains its own ownership boundary.

## 5. Projection Aggregation Rules

Projection aggregation should follow a stable conceptual order:

1. Identity reference.
2. Matrix authority context.
3. Group and sequence/token context.
4. Lifecycle projection.
5. Execution integrity projection.
6. Evidence/image projection.
7. Report/output sync projection.
8. Runtime attention projection.
9. Freshness/stale projection.
10. UI selection/navigation projection.

Aggregation rules:

- Identity is always read first and remains stable.
- Projection dimensions may be missing or partial without invalidating identity.
- Higher-priority runtime attention may change the visible emphasis, but not the step identity.
- Report sync state may be stale/current/missing, but not redefine the step.
- Selected state is a user interaction projection only.
- Setup completeness is surfaced only when it blocks or materially affects runtime action.

## 6. Projection Ownership Boundaries

Project-owned:

- project lifecycle;
- LTR;
- intake/source traceability;
- folder state;
- project readiness context.

Matrix-owned:

- current authority;
- groups;
- step obligations;
- technical context;
- sequence/token meaning.

Step-owned, in future implementation:

- lifecycle;
- execution data;
- evidence/image linkage;
- disposition;
- comments;
- report binding.

Derived-output-owned:

- report/test-record/fee/approval-package lineage;
- freshness state;
- generation/import state;
- output failure/manual markers.

Projection-owned:

- composed display state;
- compact token status;
- group summary status;
- attention ordering;
- stale/current markers;
- navigation hints.

UI-owned:

- selected token;
- hover/focus state;
- collapsed/expanded view state;
- local display preference.

UI-owned state must never become business truth.

## 7. Runtime Read Model Boundaries

The Runtime Read Model is a consumer-facing projection model for Workbench and Matrix Overview.

It may be optimized for:

- fast operator scanning;
- Matrix Overview rendering;
- Step Workspace navigation;
- runtime attention surfacing;
- group summary projection;
- stale/output sync visibility.

It must not become:

- Step identity authority;
- Matrix authority;
- Project lifecycle authority;
- persistence authority;
- report source of truth;
- frontend-only business state;
- execution mutation engine.

Future read-model fields should be treated as projected observations, not durable identity.

## 8. Projection Refresh And Stale Concepts

Projection freshness describes whether the displayed read model reflects current source state.

Conceptual projection states:

- `current`: projection reflects current known authority and source states.
- `stale`: one or more source states changed after this projection was derived.
- `partial`: some projection layers are unavailable or not implemented yet.
- `unavailable`: required source is missing.
- `superseded`: Matrix authority changed and this projection belongs to an older authority.
- `conflicted`: source layers disagree and require resolution before reliable display.

Freshness belongs to the projection.

It must not:

- rewrite Step identity;
- mutate Matrix authority;
- advance Project lifecycle;
- imply output generation;
- imply evidence storage.

## 9. Projection Versus Authority Separation

Authority answers:

```text
What is the required execution map?
```

Domain identity answers:

```text
Which executable step is this?
```

Runtime projection answers:

```text
What does this step mean for the operator right now?
```

UI state answers:

```text
What is currently selected, visible, expanded, or emphasized?
```

These answers must remain separate.

Projection dimensions include:

- UI token;
- badge;
- stale marker;
- report sync marker;
- runtime attention;
- selected state;
- evidence marker;
- group runtime status.

These dimensions cannot redefine:

- Step identity;
- Matrix authority;
- Project lifecycle.

## 10. Independently Replaceable Projection Layers

Projection layers must remain independently replaceable.

This is a governance constraint for future implementation tasks.

Replaceable layers include:

- lifecycle projection;
- data completeness projection;
- evidence/image projection;
- report sync projection;
- stale/freshness projection;
- runtime attention projection;
- group summary projection;
- UI token display projection.

Replacement examples:

- A future report sync service can replace report sync projection without changing Step identity.
- A future attention priority engine can replace runtime attention projection without changing Matrix authority.
- A future evidence/image storage module can replace evidence projection without changing lifecycle ownership.
- A future stale/freshness calculator can replace stale projection without changing Project lifecycle.

Rule:

```text
Projection layer replacement must preserve identity references and authority ownership.
```

## 11. Matrix Projection Relationship

Matrix Overview is a runtime projection and navigation surface.

It should project:

- current Matrix authority version;
- group-level runtime summary;
- step tokens;
- lifecycle markers;
- evidence/data markers;
- report sync markers;
- stale/freshness markers;
- runtime attention markers;
- selected Step Workspace target.

Matrix Overview is not:

- an Excel-like editor;
- a StepInstance object graph;
- a source of truth for runtime state;
- a report sync engine;
- an evidence storage surface;
- a status mutation engine.

Definition changes route to Matrix Editor or a Matrix change request in future tasks.

## 12. Step Workspace Selection Relationship

Selecting a Step Token is a projection-to-workspace navigation event.

Selection should carry:

- identity reference;
- authority context;
- group context;
- sequence/token context;
- current projection summary.

Selection should not create or mutate:

- StepInstance;
- Matrix authority;
- Project lifecycle;
- report sync state;
- evidence/image state;
- execution status.

The Step Workspace should eventually use the identity reference to display or resolve detailed runtime state. TASK_197 does not implement that workspace.

## 13. Group Runtime Status Projection

Group runtime status is an aggregate projection.

It may summarize:

- highest attention priority in the group;
- active steps;
- failed steps;
- blocked steps;
- missing data/evidence;
- report sync gaps;
- stale projections.

Group status must not become:

- group identity;
- Matrix authority;
- Step lifecycle source of truth;
- Project lifecycle state.

Group runtime status is replaceable projection logic.

## 14. Runtime Attention Relationship

TASK_195 defines Runtime Attention Priority:

```text
P0 - blocks execution
P1 - risks execution integrity
P2 - risks report/output integrity
P3 - runtime warning
P4 - setup completeness
```

TASK_197 treats runtime attention as a projection layer.

Runtime attention may influence:

- token emphasis;
- group summary;
- Workbench attention ordering;
- Step Workspace navigation hint.

Runtime attention must not:

- redefine step identity;
- change Matrix authority;
- mutate lifecycle state by itself;
- become a notification system;
- become a priority engine in this task.

## 15. Report Sync Marker Relationship

Report sync marker is a derived-output projection layer.

It may eventually express:

- missing;
- current;
- stale;
- manual update required;
- failed;
- not applicable.

Report sync marker must not:

- become report generation;
- become report source of truth;
- mutate Step identity;
- mutate Matrix authority;
- close or advance Project lifecycle.

Report sync projection should be independently replaceable by a future report sync read model.

## 16. Future Runtime Implementation Slices

Future work should remain split into separately approved tasks:

1. Define API/read-model DTO shape.
2. Implement Step identity domain objects.
3. Implement Step identity persistence.
4. Implement Step lifecycle persistence.
5. Implement read-model projection service.
6. Implement evidence/image projection.
7. Implement report sync projection.
8. Implement runtime attention evaluation.
9. Implement Matrix Overview projection UI.
10. Implement Step Workspace runtime UI.

None of these are implemented by TASK_197.

## 17. Non-Implementation Boundary

This document intentionally does not define or implement:

- Python dataclasses;
- ORM models;
- database schema;
- migrations;
- repositories;
- application services;
- API routes;
- frontend components;
- CSS;
- runtime engine;
- priority engine;
- notification system;
- report sync engine;
- evidence/image storage;
- StepInstance implementation.

TASK_197 is complete when the read-model projection boundary is documented and the task board records the governance state.
