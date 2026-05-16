# Step-Centric Domain Foundation

> Created: 2026-05-16  
> Task: `TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION`  
> Scope: Domain foundation documentation only. No dataclasses, DB schema, API, frontend, read model, or status engine implementation.

## 1. Purpose

This document defines the minimal step-centric domain foundation for ConnLab's Matrix-driven Laboratory Execution Phase.

It prepares future implementation tasks by separating:

- durable domain identity;
- Matrix authority definition;
- step execution ownership;
- runtime projection;
- derived output freshness.

Approved principles:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
Step is the future execution data and lifecycle unit.
```

## 2. Domain Authority Model

Authority boundaries:

- `Project` is the lifecycle container and traceability root.
- `ProjectTestPlanDraft` or future Matrix authority version defines what should be tested.
- `TestGroup` represents a group within one Matrix authority version.
- `StepInstance` represents one executable occurrence of a step within one group and one Matrix authority version.
- Derived outputs reference Matrix/Step data but do not become source of truth.

Rejected patterns:

- step identity based only on test item name;
- Matrix cell string as long-term authority;
- report/test-record files as primary data;
- UI token state as domain identity.

## 3. Conceptual StepInstance Definition

`StepInstance` is a future domain execution object. This document defines it conceptually only.

Identity dimensions:

- project identity;
- Matrix authority draft/version identity;
- group identity;
- group display label;
- step sequence number;
- token variant or suffix note;
- test item identity or normalized test item label.

Technical definition dimensions:

- section;
- method/reference standard;
- condition;
- requirement;
- step description;
- source trace.

Execution dimensions:

- execution status;
- lifecycle status;
- data state;
- evidence/image state;
- failure/disposition state;
- report sync relationship;
- derived-output freshness relationship.

## 4. Stable Identity Rules

Stable identity rules:

1. Step identity must include project, Matrix authority version, group identity, and step sequence.
2. Repeated test items are allowed and must not collapse into one record.
3. Token suffixes such as `3(a)` are variants, not independent display-only strings.
4. Group identity must be stable and explicit before runtime data can attach safely.
5. When Matrix authority changes, existing StepInstances should be considered version-bound until a later task defines carry-forward or supersession behavior.

Step identity answers:

```text
What executable step is this?
```

It must not be redefined by pass/fail state, evidence state, report sync state, runtime attention priority, display sorting, or UI selection.

## 5. Matrix Token To StepInstance Mapping

Conceptual mapping:

```text
Matrix row context + Group column + token -> StepInstance candidate
```

Mapping inputs:

- Matrix authority version;
- group key;
- row technical context;
- raw token;
- parsed step sequence;
- parsed suffix/variant;
- source trace.

Mapping output:

- one conceptual executable step occurrence.

TASK_196 does not implement a parser or migration. Existing parsing decisions remain in:

- `docs/matrix_test_plan_data_management_decisions.md`
- `backend/modules/test_plan/matrix_step_sequence_validation.py`

## 6. Step Lifecycle Concept

Conceptual lifecycle states:

- not started;
- ready;
- in progress;
- paused;
- blocked;
- pass;
- fail;
- retest required;
- waived;
- not applicable;
- closed.

Lifecycle is separate from:

- data completeness;
- evidence completeness;
- report sync;
- setup completeness;
- derived-output freshness.

## 7. Runtime Attention Relationship

TASK_195 defines runtime attention priority. TASK_196 maps that concept to future domain ownership:

- P0/P1 execution issues usually attach to StepInstance or Matrix authority.
- P2 output integrity issues attach to derived output records and reference Matrix/Step identity.
- P3 runtime warnings may attach to StepInstance, Group, Matrix authority, or Project.
- P4 setup completeness issues attach to setup/status surfaces, not to StepInstance unless they block execution.

This document does not implement a priority engine.

## 8. Derived Output Relationship

Conceptual relationships:

- Test record forms derive from Matrix authority and group/step definitions.
- Imported test record data should eventually attach to StepInstance.
- Report sections derive from StepInstance data/evidence and Matrix technical context.
- Fee evaluation derives from step count, test item, sample/group assumptions, and price mapping.
- Approval package derives from current output records and project evidence.

Derived outputs should become stale when their source Matrix/Step data changes.

## 9. Runtime Projection Boundary

The Runtime Projection Boundary prevents future tasks from mixing StepInstance domain identity with Workbench / Matrix Overview display projections.

### 9.1 Domain Object Versus Projection

`StepInstance` is the domain execution object. It is responsible for:

- stable identity;
- lifecycle ownership;
- execution data ownership;
- evidence/image ownership;
- disposition ownership;
- future report-binding ownership.

`Matrix Overview` and `Workbench Runtime Console` display runtime projections. They are not the domain objects themselves.

Future UI tokens, Matrix cells, drawer rows, or Workbench summaries are projection results, not source of truth.

### 9.2 Multi-State Projection

One Matrix cell or Step token may project multiple state dimensions:

- lifecycle status;
- data completeness;
- evidence/image state;
- report sync state;
- stale/freshness state;
- runtime attention priority.

These projected states may be visually combined in a future UI, but they remain conceptually separate from stable Step identity.

### 9.3 Identity Must Not Be Polluted By Projection

Stable Step identity comes from:

```text
Matrix authority + group identity + step sequence/token identity
```

It must not be redefined by:

- pass/fail status;
- evidence presence;
- report stale/current state;
- runtime attention priority;
- selected UI row;
- display sorting;
- badge state;
- frontend filtering.

### 9.4 Read Model And UI Model Boundary

Future UI display models, read models, and projection models may combine multiple sources:

- Matrix authority definition;
- Step lifecycle;
- evidence/image state;
- report sync state;
- output freshness;
- runtime attention priority.

Projection/read/UI models must not become source of truth.

They answer:

```text
What should the operator see right now?
```

They do not redefine:

```text
What is this step?
```

### 9.5 Guidance For TASK_197

Future `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL` should use this boundary:

- Step identity comes from Matrix authority + group + sequence/token.
- Runtime projection comes from Step lifecycle / evidence / report / output freshness.
- UI token is only the projection result.

TASK_196 does not implement the read model. It records the boundary for future design.

## 10. Data Ownership Boundaries

Project-owned:

- lifecycle identity;
- LTR;
- intake/source evidence;
- folder;
- overall readiness.

Matrix-owned:

- authority version;
- test definition;
- groups;
- step mapping;
- technical conditions and requirements.

Step-owned:

- execution state;
- measurements/results;
- evidence/images;
- comments;
- disposition;
- report binding.

Output-owned:

- generation/import lineage;
- output path;
- freshness status;
- failure/manual notes.

Setup-owned:

- external resources;
- folder readiness;
- approval package preparation;
- source material placement.

## 11. Future Implementation Slices

Recommended later tasks:

1. Translate domain document to Python dataclasses/enums.
2. Design SQLite persistence and migration.
3. Build Step read model from current Matrix authority.
4. Build runtime issue projection service.
5. Add Step result/evidence persistence.
6. Add report sync read model.

The next recommended controlled task is:

```text
TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL
```

TASK_197 should still begin with its own plan and approval before any implementation.

## 12. Non-Implementation Boundary

This document intentionally does not define:

- Python dataclasses;
- database schema;
- API endpoints;
- repository contracts;
- service implementation;
- frontend DTOs;
- UI components;
- read model implementation;
- status engine implementation.

Those require separate approved tasks.
