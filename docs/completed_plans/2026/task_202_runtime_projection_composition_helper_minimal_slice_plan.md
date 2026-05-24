# TASK_202 Runtime Projection Composition Helper Minimal Slice Plan

> Created: 2026-05-16  
> Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`  
> Proposed task: `TASK_202_RUNTIME_PROJECTION_COMPOSITION_HELPER_MINIMAL_SLICE`  
> Status: Plan for review. No implementation is approved by this document.

## 1. Current Phase And Task Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task board state:

```text
TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE complete
Current Active Task: none; TASK_201 projection dto and token reference builder minimal slice complete, pending next controlled implementation task
```

Why TASK_202 planning is allowed now:

- TASK_200 recommended moving from token reference building toward the next minimal runtime composition slice.
- TASK_201 implemented the first backend-only in-memory projection DTO and token reference builder slice.
- The task board says the next step is to define and approve the next minimal runtime composition slice only if requested.
- The user explicitly requested the next step according to the MD files.

This plan is the required reviewable plan before any implementation.

## 2. Task Goal

Plan the next minimal backend-only runtime slice:

```text
Runtime Projection Composition Helper minimal slice
```

The future TASK_202 implementation should compose existing token projections into simple read-model summaries without adding persistence, API, UI, StepInstance, or runtime engines.

## 3. Core Governance Rules

TASK_202 must preserve:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
Projection composition must remain independently evolvable.
```

Composition outputs are read-model/projection outputs. They must not become domain source of truth.

## 4. Inputs

TASK_202 should build on:

- `backend/modules/runtime_projection/models.py`
- `backend/modules/runtime_projection/token_projection_builder.py`
- `tests/unit/test_runtime_projection_token_builder.py`
- `docs/first_runtime_implementation_slice_planning.md`
- `docs/runtime_projection_service_and_read_model_boundary.md`
- `docs/interactive_step_token_read_model_projection_foundation.md`

Existing parser reuse still applies through TASK_201:

- `backend/modules/test_plan/matrix_step_sequence_validation.py`

TASK_202 should not modify parser behavior.

## 5. Plan-Stage Output

This plan stage may create only:

- `docs/task_202_runtime_projection_composition_helper_minimal_slice_plan.md`

This plan stage must not create:

- `tasks/TASK_202_RUNTIME_PROJECTION_COMPOSITION_HELPER_MINIMAL_SLICE.md`
- backend implementation files;
- tests;
- API/DB/frontend files.

This plan stage must not update:

- `docs/task_board.md`
- static governance tests.

## 6. Proposed Future Implementation Scope

If approved later, TASK_202 may add a small composition helper under:

```text
backend/modules/runtime_projection/composition.py
backend/modules/runtime_projection/fake_fixture_builder.py
tests/unit/test_runtime_projection_composition.py
```

It may update exports in:

```text
backend/modules/runtime_projection/__init__.py
```

Candidate DTO-like additions may live in:

```text
backend/modules/runtime_projection/models.py
```

Only if needed, candidate structures may include:

- `GroupRuntimeProjection`
- `RuntimeProjectionSummary`
- `ProjectionIssueCount`

These names are candidates, not approved implementation details.

`fake_fixture_builder.py` is an optional test-infrastructure candidate only. It may be used to create explicit fake/static projection inputs for unit tests, but it must not become a production runtime source, hidden default state provider, cache, or data persistence layer.

## 7. Composition Responsibility

Future composition should accept already-built `InteractiveStepTokenProjection` objects and produce simple aggregate read-model outputs.

Allowed conceptual responsibilities:

- count total projected tokens;
- group tokens by group identity;
- preserve identity references;
- derive group-level counts from projection dimensions;
- surface parser/projection warnings if passed in;
- identify simple attention priority ordering from existing projection fields.

Forbidden responsibilities:

- parsing Matrix token strings again;
- creating StepInstance;
- mutating Matrix authority;
- mutating Project lifecycle;
- persisting projection results;
- generating API responses;
- driving frontend behavior;
- calculating real runtime lifecycle.

## 8. Fake Projection Source Boundary

TASK_202 may use fake/static projection dimensions produced by TASK_201.

Examples:

- `lifecycle_projection = "not_started"`
- `evidence_projection = "unknown"`
- `report_sync_projection = "unknown"`
- `stale_projection = "unknown"`
- `attention_projection = "none"`

These values remain fake/static projection fields. They are not production runtime state.

The composition helper should treat missing projection dimensions as valid partial projections, not as invalid identity.

If a `fake_fixture_builder` is introduced during formal TASK_202 execution, it must stay test-oriented and deterministic:

- create fake `InteractiveStepTokenProjection` inputs for composition tests;
- make fake lifecycle/evidence/report/stale/attention states explicit;
- avoid hiding defaults that look like real runtime state;
- avoid reading files, databases, APIs, or frontend state;
- avoid mutating Matrix authority, Project lifecycle, or token references.

## 9. Minimal Composition Rules

Future TASK_202 should keep rules deliberately small:

- token identity remains unchanged by composition;
- group identity remains unchanged by composition;
- missing projection dimensions do not drop tokens;
- aggregation reads projection fields but does not rewrite them;
- repeated sequence numbers in different groups stay distinct;
- summary output must remain in-memory and deterministic.

No stale algorithm, attention engine, report sync engine, evidence engine, or lifecycle engine should be introduced.

## 10. Validation Strategy For Formal TASK_202

Future unit tests should cover:

- composing an empty token list returns an empty/zero summary;
- composing multiple tokens preserves token references;
- group summaries keep same sequence in different groups distinct;
- missing projection dimensions do not invalidate token identity;
- fake lifecycle/evidence/report/attention fields are counted only as projection dimensions;
- fake fixture builder outputs remain explicit test inputs, not production runtime state;
- aggregation does not mutate token projections;
- aggregation does not mutate Matrix authority references;
- aggregation does not mutate Project references;
- no parser function is called by composition helper.

Expected tests:

- unit tests only.

Not required:

- API tests;
- DB tests;
- frontend build;
- browser tests;
- Office tests.

## 11. Forbidden Scope For Formal TASK_202

TASK_202 must forbid:

- database schema;
- ORM models;
- migrations;
- API routes;
- frontend components;
- React/CSS;
- StepInstance persistence;
- real lifecycle persistence;
- report sync implementation;
- evidence/image storage;
- notification implementation;
- cache engine;
- runtime engine;
- mutation of Matrix authority;
- mutation of Project lifecycle;
- parser implementation or parser hardening;
- changes to existing production workflow.

## 12. Rollback Boundary

Future TASK_202 should be easy to roll back.

Rollback should only require removing:

- `backend/modules/runtime_projection/composition.py`
- `backend/modules/runtime_projection/fake_fixture_builder.py`
- `tests/unit/test_runtime_projection_composition.py`
- any TASK_202-only exports or DTO additions;
- TASK_202 docs/task-board updates.

Rollback must not require:

- database rollback;
- API route removal;
- frontend rollback;
- migration reversal;
- Matrix authority data correction;
- output ledger changes.

## 13. Stop Condition

This plan stops before TASK_202 formal execution.

Do not create:

- `tasks/TASK_202_RUNTIME_PROJECTION_COMPOSITION_HELPER_MINIMAL_SLICE.md`
- implementation files;
- tests;
- task board updates.

Wait for user review and explicit approval before entering TASK_202 formal execution.
