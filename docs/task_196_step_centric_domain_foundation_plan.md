# TASK_196 Step-Centric Domain Foundation Plan

> Status: draft for review  
> Created: 2026-05-16  
> Phase: Phase 11 controlled foundation baseline, preparing Matrix-driven Laboratory Execution Phase  
> Task ID: TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION

## 0. Execution Gate

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task before this plan: `none`.
- Current board state: TASK_195 complete, next recommended action is to define and approve `TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION`.
- Why this task is allowed now:
  - `docs/task_board.md` explicitly recommends TASK_196 after TASK_195.
  - The user explicitly requested preparing the TASK_196 plan.
  - This plan is the required pre-implementation plan document.

Important constraint:

- `tasks/TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION.md` does not exist yet.
- This plan proposes creating it during TASK_196 execution after user approval.

## 1. Purpose

TASK_196 will define the minimal step-centric domain foundation needed before any runtime implementation.

It must translate the approved Runtime IA into a domain-level foundation:

```text
Project -> Matrix authority -> TestGroup -> StepInstance -> derived outputs
```

The task is not implementation. It defines boundaries, object relationships, identity rules, lifecycle concepts, and future persistence/API constraints.

Approved principles to preserve:

```text
Matrix is the execution authority map, Project remains the lifecycle container.
Step is the future execution data and lifecycle unit.
```

## 2. Task Understanding

### 2.1 Goal

Define a minimal step-centric domain foundation that future implementation tasks can safely use.

The foundation should answer:

- What is a `StepInstance` conceptually?
- How does it relate to Project, Matrix authority, group, and token sequence?
- Which fields belong to step identity versus execution state?
- Which lifecycle states are needed conceptually?
- Which runtime attention categories map to Step, Group, Matrix, Project, setup, or derived outputs?
- What must remain outside TASK_196?

### 2.2 Inputs

Primary inputs:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/matrix_test_plan_data_management_decisions.md`
- `docs/project_workbench_matrix_authority_workspace_target.md`
- TASK_196 request from user

Reference inputs:

- current `ProjectTestPlanDraft` model and existing Matrix draft payload shape;
- current output ledger concepts from TASK_188;
- current Matrix sequence parsing and validation decisions;
- `TestFlowManager.zip` as lessons-only reference material, not source code.

### 2.3 Outputs

TASK_196 should output documentation only:

1. A formal task file:
   - `tasks/TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION.md`
2. A step-centric domain foundation document:
   - `docs/step_centric_domain_foundation.md`
3. A task-board update after completion:
   - `docs/task_board.md`
4. Optional static governance test updates only if existing guard tests need to recognize TASK_196 board state.

### 2.4 Modules Involved

Documentation/governance only:

- `docs/`
- `tasks/`
- possibly `tests/unit/*scope*` static governance tests.

No backend, frontend, database, API, or Office runtime modules are in scope for TASK_196 as planned here.

### 2.5 Explicit Non-Goals

TASK_196 must not implement:

- Python domain dataclasses;
- SQLAlchemy models;
- database migrations;
- repositories;
- services;
- API routes;
- frontend UI or DTOs;
- StepInstance persistence;
- runtime status engine;
- priority engine;
- notification system;
- report sync engine;
- test data import;
- image/evidence storage.

## 3. Step-Centric Foundation Deliverable Shape

The main document, `docs/step_centric_domain_foundation.md`, should contain the following sections.

## 4. Domain Authority Model

Define authority boundaries:

- `Project` is the lifecycle container and traceability root.
- `ProjectTestPlanDraft` or future Matrix authority version defines what should be tested.
- `TestGroup` represents a group within one Matrix authority version.
- `StepInstance` represents one executable occurrence of a step within one group and one Matrix authority version.
- Derived outputs reference Matrix/Step data but do not become source of truth.

The document should explicitly reject:

- step identity based only on test item name;
- Matrix cell string as long-term authority;
- report/test-record files as primary data.

## 5. Conceptual StepInstance Definition

Define `StepInstance` conceptually, without writing code.

Required identity dimensions:

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

## 6. Stable Identity Rules

Define stable identity rules before persistence exists:

1. Step identity must include project, Matrix authority version, group identity, and step sequence.
2. Repeated test items are allowed and must not collapse into one record.
3. Token suffixes such as `3(a)` are variants, not independent display-only strings.
4. Group identity must be stable and explicit before runtime data can attach safely.
5. When Matrix authority changes, existing StepInstances should be considered version-bound. Future tasks must define carry-forward or supersession behavior explicitly.

## 7. Matrix Token To StepInstance Mapping

Define conceptual mapping from Matrix tokens to future StepInstances:

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

The document should clarify that TASK_196 does not implement a parser or migration. Existing parsing decisions remain in `docs/matrix_test_plan_data_management_decisions.md` and `backend/modules/test_plan/matrix_step_sequence_validation.py`.

## 8. Step Lifecycle Concept

Define conceptual lifecycle states without creating enums.

Suggested lifecycle concepts:

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

Separate lifecycle from:

- data completeness;
- evidence completeness;
- report sync;
- setup completeness;
- derived-output freshness.

## 9. Runtime Attention Relationship

Map TASK_195 runtime attention model to future domain ownership:

- P0/P1 execution issues should usually attach to StepInstance or Matrix authority.
- P2 output integrity issues should attach to derived output records and reference Matrix/Step identity.
- P3 runtime warnings may attach to StepInstance, Group, Matrix authority, or Project.
- P4 setup completeness issues attach to setup/status surfaces, not to StepInstance unless they block execution.

The document should avoid implementing a priority engine.

## 10. Derived Output Relationship

Define conceptual relationships:

- Test record forms derive from Matrix authority and group/step definitions.
- Imported test record data should eventually attach to StepInstance.
- Report sections derive from StepInstance data/evidence and Matrix technical context.
- Fee evaluation derives from step count, test item, sample/group assumptions, and price mapping.
- Approval package derives from current output records and project evidence.

Derived outputs should become stale when their source Matrix/Step data changes.

## 11. Runtime Projection Boundary

Define the boundary between durable domain execution objects and runtime projection surfaces.

Purpose:

```text
Prevent future tasks from mixing StepInstance domain identity with Workbench / Matrix Overview display projections.
```

### 11.1 Domain Object Versus Projection

`StepInstance` is the domain execution object. It is responsible for:

- stable identity;
- lifecycle ownership;
- execution data ownership;
- evidence/image ownership;
- disposition ownership;
- future report-binding ownership.

`Matrix Overview` and `Workbench Runtime Console` display runtime projections. They are not the domain objects themselves.

The future UI token, Matrix cell, drawer row, or Workbench summary should be treated as a projection result, not as the source of truth.

### 11.2 Multi-State Projection

One Matrix cell or Step token may project multiple state dimensions at once:

- lifecycle status;
- data completeness;
- evidence/image state;
- report sync state;
- stale/freshness state;
- runtime attention priority.

These projected states may be visually combined in a future UI, but they must remain conceptually separate from stable Step identity.

### 11.3 Identity Must Not Be Polluted By Projection

Projection state must not change the meaning of Step identity.

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

### 11.4 Read Model And UI Model Boundary

Future UI display models, read models, and projection models may combine multiple sources:

- Matrix authority definition;
- Step lifecycle;
- evidence/image state;
- report sync state;
- output freshness;
- runtime attention priority.

However, projection/read/UI models must not become source of truth.

They are allowed to answer:

```text
What should the operator see right now?
```

They are not allowed to redefine:

```text
What is this step?
```

### 11.5 Guidance For TASK_197

Future `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL` should use this boundary:

- Step identity comes from Matrix authority + group + sequence/token.
- Runtime projection comes from Step lifecycle / evidence / report / output freshness.
- UI token is only the projection result.

TASK_196 must not implement the read model. It only records the boundary for future design.

### 11.6 Explicit Non-Implementation Boundary

This Runtime Projection Boundary does not authorize:

- Python dataclasses;
- DB schema;
- API design;
- frontend changes;
- read model implementation;
- status engine implementation.

## 12. Data Ownership Boundaries

Define what belongs where:

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

## 13. Future Implementation Slices

Define recommended later tasks without implementing them:

1. Domain doc to Python dataclasses/enums.
2. SQLite persistence design and migration.
3. Step read model from current Matrix authority.
4. Runtime issue projection service.
5. Step result/evidence persistence.
6. Report sync read model.

TASK_196 should recommend `TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL` only if the foundation is accepted.

## 14. File-Level Change Plan

### 14.1 `tasks/TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION.md`

Create the formal task file with:

- execution gate;
- purpose;
- in-scope/out-of-scope;
- acceptance criteria;
- validation method;
- stop condition.

### 14.2 `docs/step_centric_domain_foundation.md`

Create the main Step-centric domain foundation document with the sections above.

### 14.3 `docs/task_board.md`

After TASK_196 completion:

- record TASK_196 completion;
- update last updated date;
- record validation summary;
- set next recommended task.

Proposed next recommended task:

```text
TASK_197_INTERACTIVE_STEP_TOKEN_READ_MODEL
```

### 14.4 Static Governance Tests

Only if needed, update existing static guard tests so they recognize TASK_196 completion in the board.

Do not add runtime/backend tests because this is a documentation-only task.

## 15. Acceptance Criteria

TASK_196 is complete when:

- `tasks/TASK_196_STEP_CENTRIC_DOMAIN_FOUNDATION.md` exists.
- `docs/step_centric_domain_foundation.md` exists.
- The foundation document defines:
  - authority boundaries;
  - conceptual StepInstance definition;
  - stable identity rules;
  - Matrix token to StepInstance mapping;
  - lifecycle concepts;
  - runtime attention relationship;
  - derived output relationship;
  - Runtime Projection Boundary;
  - data ownership boundaries;
  - future implementation slices.
- The document explicitly blocks code/schema/API implementation in TASK_196.
- The document explicitly states that Runtime Projection must not redefine Step identity or become source of truth.
- The document explicitly preserves Project as lifecycle container and Matrix as execution authority map.
- `docs/task_board.md` records completion and next recommended task.
- No backend, frontend, API, DB, Office, or runtime source files are changed.

## 16. Validation Plan

Document validation:

1. Confirm required files exist.
2. Search TASK_196 documents for forbidden implementation language, including:
   - SQLAlchemy model implementation;
   - migration;
   - API endpoint;
   - React component;
   - persistence service;
   - priority engine.
3. Confirm Runtime Projection Boundary remains documentation-only and does not define read model implementation, status engine, API, DB schema, or frontend behavior.
4. Confirm no runtime source files changed.
5. Run governance guard tests if board state changes require it:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

No `npm run build` is required because no frontend implementation should change.

## 17. Risks And Controls

Risk: TASK_196 may drift from foundation design into schema or service implementation.  
Control: document conceptual domain only; defer all code/schema/API work.

Risk: StepInstance may be overdesigned before real runtime data exists.  
Control: define minimal identity and responsibility boundaries first; leave persistence details to later task.

Risk: repeated test items may collapse incorrectly.  
Control: require group + sequence + Matrix version identity, not test item name alone.

Risk: Matrix authority changes may corrupt runtime traceability if version binding is vague.  
Control: state that StepInstance identity is version-bound until a later task defines carry-forward behavior.

Risk: runtime projection may be mistaken for Step identity.  
Control: define StepInstance identity separately from lifecycle, evidence, report sync, freshness, attention, read-model, and UI token projection.

Risk: derived outputs may be mistaken for source data.  
Control: reinforce output-derived status and stale behavior.

## 18. Stop Condition

After this plan is reviewed, do not proceed to TASK_196 execution until the user explicitly approves.

After TASK_196 execution is later completed, stop again. Do not automatically enter TASK_197.
