# Runtime Projection Service And Read Model Boundary

> Created: 2026-05-16  
> Task: `TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY`  
> Scope: Documentation, governance, and runtime-boundary only. No service, engine, API, schema, or UI implementation.

## 1. Purpose

This document defines the future Runtime Projection Service boundary for ConnLab's Matrix-driven Laboratory Execution Phase.

It does not implement a service. It defines the ownership and composition boundaries that future implementation tasks must preserve.

Core rules:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
```

New TASK_198 governance rule:

```text
Projection composition must remain independently evolvable.
```

Projection aggregation, attention evaluation, report sync projection, evidence projection, stale calculation, and group summary projection must be able to evolve independently without breaking:

- Step identity;
- Matrix authority;
- Project lifecycle ownership;
- Runtime projection boundary.

## 2. Authority Baseline

Approved product principle:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
```

Authority boundaries:

- `Project` owns lifecycle identity, LTR, intake/source traceability, folder state, and overall readiness.
- `Matrix authority` owns what should be tested.
- `Group identity` owns group position inside one Matrix authority.
- `StepInstance` is the future execution domain object for lifecycle and execution data ownership.
- `Derived outputs` own generation/import lineage and freshness state.
- `Runtime Projection` owns composed read-state only.

Runtime Projection must never redefine:

- Project lifecycle;
- Matrix authority;
- group identity;
- Step identity;
- Step lifecycle source data;
- output source truth.

## 3. Runtime Projection Composition Responsibility

Runtime projection composition is the conceptual responsibility for combining source-owned state into operator-facing read models.

It may compose:

- identity references from Project, Matrix authority, group identity, and step sequence/token;
- Matrix technical context;
- lifecycle projection;
- data completeness projection;
- evidence/image projection;
- report/output projection;
- stale/freshness projection;
- runtime attention projection;
- group summary projection;
- consumer navigation context.

It must not own:

- source identity;
- execution lifecycle mutation;
- evidence/image storage;
- report generation;
- output ledger mutation;
- UI selection state.

Projection composition answers:

```text
What should the Runtime Console show right now?
```

It does not answer:

```text
What is the source of truth?
```

## 4. Projection Aggregation Flow

Future projection aggregation should follow a stable conceptual flow:

1. Read identity references:
   - Project;
   - Matrix authority;
   - group identity;
   - sequence/token.
2. Attach Matrix technical context:
   - test item;
   - section;
   - method;
   - condition;
   - requirement;
   - source trace.
3. Attach execution projection dimensions:
   - lifecycle;
   - data completeness;
   - evidence/image state;
   - failure/disposition state.
4. Attach derived-output projection dimensions:
   - report sync;
   - test record freshness;
   - fee freshness;
   - approval package freshness.
5. Attach freshness and invalidation markers:
   - current;
   - stale;
   - partial;
   - superseded;
   - unavailable;
   - conflicted.
6. Attach runtime attention projection:
   - P0 execution blocker;
   - P1 execution integrity risk;
   - P2 output integrity risk;
   - P3 runtime warning;
   - P4 setup completeness.
7. Emit read-model projections for:
   - Matrix Overview;
   - Step Workspace;
   - Workbench Runtime Console attention summary.

This flow is not an algorithm, API, class, cache, or engine. It is a boundary model.

## 5. Projection Refresh And Stale Boundary

Refresh/stale state is a property of projection freshness.

Stale projection means:

- one or more source dimensions changed after the projection was composed;
- the displayed read model may need refresh or re-composition;
- the operator may need attention guidance.

Stale projection does not:

- alter Step identity;
- supersede Matrix authority;
- mutate Project lifecycle;
- generate reports;
- store evidence;
- change execution lifecycle.

Freshness belongs to the projection layer. Source changes belong to their source owners.

## 6. Projection Invalidation Concepts

Projection invalidation is a conceptual signal that a read model should be rebuilt, marked stale, or treated as partial.

Potential invalidation triggers:

- Matrix authority change;
- group identity change;
- step token mapping change;
- future Step lifecycle change;
- future execution data change;
- future evidence/image state change;
- report/output generation;
- report/output import;
- output ledger freshness change;
- Project lifecycle change;
- setup/support status change that affects runtime attention;
- source material or traceability change.

Invalidation must not be confused with:

- database mutation;
- cache implementation;
- message bus implementation;
- notification implementation;
- runtime engine processing;
- UI state updates.

TASK_198 does not implement invalidation.

## 7. Projection Service Ownership

Future Runtime Projection Service ownership:

- compose read models from source-owned state;
- preserve source identity references;
- expose conceptual projection dimensions;
- preserve projection freshness meaning;
- keep projection layers independently evolvable;
- support Matrix Overview and Step Workspace consumption in later tasks.

It must not own:

- Project lifecycle authority;
- Matrix authority;
- Step lifecycle source truth;
- execution data persistence;
- evidence/image storage;
- report generation;
- report sync execution;
- output ledger writes;
- notification delivery;
- UI selection/hover/focus state.

Runtime Projection Service is a composition boundary, not a domain owner.

## 8. Read Model Boundary Versus Domain Boundary

Domain boundary answers:

```text
What exists, and who owns its source truth?
```

Read-model boundary answers:

```text
What should a consumer see for fast operational understanding?
```

Projection boundary answers:

```text
How are multiple source-owned states composed into a read model?
```

UI state answers:

```text
What is selected, expanded, focused, filtered, or emphasized?
```

These layers must stay separate.

Read models may duplicate or denormalize source-owned facts for consumption. They must not become source truth.

## 9. Matrix Overview Projection Consumption Model

Matrix Overview is a projection consumer.

It may consume:

- current Matrix authority reference;
- group runtime summary projections;
- step token projections;
- lifecycle markers;
- evidence/data markers;
- report sync markers;
- stale/freshness markers;
- runtime attention markers;
- selection target references.

Matrix Overview must not become:

- source of truth;
- Matrix definition editor;
- StepInstance object graph;
- status mutation engine;
- report sync engine;
- evidence/image storage surface;
- cache owner.

Matrix Overview should preserve the distinction between:

- authority context;
- runtime projection;
- selected UI state.

## 10. Step Workspace Projection Consumption Model

Step Workspace is a detailed projection consumer.

It may consume:

- selected identity reference;
- authority context;
- group and sequence/token context;
- lifecycle projection;
- data/evidence projection;
- report/output projection;
- runtime attention projection;
- freshness/stale projection.

Step Workspace selection must not:

- create StepInstance;
- mutate Matrix authority;
- mutate Project lifecycle;
- write execution data;
- store evidence/images;
- generate report sync state.

Future domain actions from Step Workspace require separately approved tasks.

## 11. Projection Source Dependency Map

Projection dependency direction:

```text
Source-owned state -> Runtime Projection composition -> Consumer read models
```

Source-owned state includes:

- Project lifecycle and traceability;
- Matrix authority;
- group identity;
- sequence/token identity;
- Matrix technical context;
- future Step lifecycle;
- future execution data;
- future evidence/image state;
- output ledger state;
- report/test-record/fee/approval freshness;
- runtime attention model;
- setup/support status.

Projection must not reverse this direction.

Forbidden dependency direction:

```text
UI token / projection marker / stale badge -> Step identity or Matrix authority
```

## 12. Independently Evolvable Composition Layers

Projection composition must remain independently evolvable.

Future layers should be separable:

- identity reference projection;
- lifecycle projection;
- data completeness projection;
- evidence/image projection;
- report sync projection;
- stale/freshness projection;
- runtime attention projection;
- group summary projection;
- Matrix Overview consumption projection;
- Step Workspace consumption projection.

Layer evolution examples:

- Attention evaluation can evolve without changing report sync projection.
- Report sync projection can evolve without changing Step identity.
- Evidence projection can evolve without changing lifecycle ownership.
- Stale calculation can evolve without changing Project lifecycle.
- Group summary projection can evolve without changing Matrix authority.

Rule:

```text
Changing a projection composition layer must preserve source ownership and identity references.
```

## 13. Runtime Attention Boundary

Runtime attention is a projection dimension, not a notification system or priority engine in this task.

It may later consume:

- execution blockers;
- execution integrity risks;
- report/output integrity risks;
- runtime warnings;
- setup completeness issues.

Runtime attention must not:

- mutate Step lifecycle;
- redefine Step identity;
- change Matrix authority;
- advance Project lifecycle;
- become notification delivery.

## 14. Report Sync Projection Boundary

Report sync projection is a derived-output projection dimension.

It may later describe:

- missing;
- current;
- stale;
- manual;
- failed;
- not applicable.

It must not:

- generate reports;
- edit reports;
- own report truth;
- mutate Step identity;
- mutate Matrix authority;
- mutate Project lifecycle.

## 15. Evidence Projection Boundary

Evidence/image projection is a projection dimension over future evidence/image source state.

It may later describe:

- missing required evidence;
- evidence present;
- evidence linked to selected step;
- evidence newer than report;
- image present or missing;
- source trace warning.

It must not:

- store evidence;
- move files;
- upload images;
- own Step identity;
- mutate Step lifecycle by itself.

## 16. Future Runtime Implementation Slices

Future work should remain split into separately approved tasks:

1. Runtime projection read-model DTO/API design.
2. Step identity domain implementation.
3. Step identity persistence.
4. Step lifecycle persistence.
5. Evidence/image projection provider.
6. Report sync projection provider.
7. Stale/freshness calculation provider.
8. Runtime attention provider.
9. Group summary projection provider.
10. Runtime Projection Service implementation.
11. Matrix Overview projection consumer implementation.
12. Step Workspace projection consumer implementation.

TASK_198 implements none of these.

## 17. Non-Implementation Boundary

This document intentionally does not define or implement:

- backend runtime implementation;
- Python dataclasses;
- ORM models;
- database schema;
- migrations;
- repositories;
- service classes;
- cache engine;
- projection engine;
- API routes;
- API DTOs;
- React components;
- CSS;
- report sync implementation;
- evidence/image implementation;
- notification implementation;
- StepInstance implementation.

TASK_198 is complete when this boundary is documented and the task board records the governance state.
