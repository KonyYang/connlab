# TASK_200 First Runtime Implementation Slice Planning Plan

> Created: 2026-05-16  
> Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`  
> Proposed task: `TASK_200_FIRST_RUNTIME_IMPLEMENTATION_SLICE_PLANNING`  
> Status: Plan for review. No implementation is approved by this document.

## 1. Current Phase And Task Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current board state:

```text
TASK_198_RUNTIME_PROJECTION_SERVICE_AND_READ_MODEL_BOUNDARY complete
Current Active Task: none; TASK_198 runtime projection service boundary complete, pending next controlled implementation task
```

User decision:

```text
Do not formally execute TASK_199.
TASK_199 remains plan-stage.
```

Why TASK_200 planning is allowed now:

- TASK_194 established product governance.
- TASK_195 established Runtime Console information architecture.
- TASK_196 established Step-centric domain foundation.
- TASK_197 established projection/read-model foundation.
- TASK_198 established Runtime Projection Service composition boundary.
- TASK_199 plan established Matrix Overview consumption boundary, but will not be formally executed to avoid governance over-expansion.
- The user explicitly approved entering TASK_200 plan preparation.

## 2. Task Purpose

TASK_200 converts the TASK_194-199 governance system into a first minimal implementation-slice plan.

TASK_200 is not runtime implementation.

It defines:

- implementation boundary;
- acceptance criteria;
- rollback safety;
- test strategy;
- fake/mock strategy;
- minimal runtime slice decomposition.

The intended next implementation task after TASK_200 should be:

```text
Projection DTO / Token Parsing minimal slice
```

That implementation belongs to TASK_201 or later, not TASK_200.

## 3. Inputs

TASK_200 should use:

- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/step_centric_domain_foundation.md`
- `docs/interactive_step_token_read_model_projection_foundation.md`
- `docs/runtime_projection_service_and_read_model_boundary.md`
- `docs/task_199_matrix_overview_runtime_projection_consumption_model_plan.md`
- `docs/task_board.md`

The user-provided TASK_200 prompt is also authoritative.

## 4. Plan-Stage Output

This plan stage may create only:

- `docs/task_200_first_runtime_implementation_slice_planning_plan.md`

This plan stage must not create:

- TASK_200正文任务文件;
- runtime implementation docs beyond this plan;
- DTO/dataclass files;
- backend/frontend/API/DB code;
- parser/runtime/projection implementation.

This plan stage must not update:

- `docs/task_board.md`
- backend files;
- frontend files;
- API files;
- database/schema/migration files;
- tests.

## 5. Explicit Non-Scope

TASK_200 must not implement:

- backend runtime implementation;
- frontend implementation;
- API/DTO design or implementation;
- dataclasses;
- ORM models;
- persistence;
- SQLite schema;
- migrations;
- StepInstance implementation;
- projection implementation;
- runtime service implementation;
- Matrix token parser implementation;
- React/CSS implementation;
- report sync implementation;
- evidence/image implementation.

TASK_200 is planning only.

## 6. First Minimal Implementation Slices

TASK_200 should propose the first implementable slices in order.

Recommended first slice for TASK_201:

```text
Projection DTO / Token Parsing minimal slice
```

Purpose:

- define minimal backend-side data shapes for projection fixtures or pure read-model values;
- parse Matrix token strings into stable token references;
- produce fake/static projection outputs for tests;
- avoid persistence, API, UI, StepInstance, and runtime engine.

Possible later slices:

1. Minimal token parsing and projection DTO slice.
2. Fake projection source and fixture builder.
3. Runtime projection composition pure function/service slice.
4. API read-only projection endpoint slice.
5. Matrix Overview UI consumption slice.
6. Step Workspace selection shell slice.

TASK_200 should explicitly recommend TASK_201 as slice 1 only.

## 7. Projection DTO Slice Boundary

TASK_201 should be allowed to define minimal data shapes only if approved.

Potential boundary:

- pure Python DTO-like structures or Pydantic response models if API work is approved later;
- no ORM;
- no database;
- no StepInstance;
- no persistence;
- no frontend DTO consumption in the same task unless separately scoped.

DTO ownership must remain projection-only:

- identity reference fields are references, not source truth;
- status fields are projection values, not lifecycle mutation;
- stale/report/evidence/attention fields are projection dimensions.

## 8. Matrix Token Parsing Slice Boundary

TASK_201 may be the right place to create a minimal token parser, but only as an approved implementation task.

Potential parser scope:

- parse `2`, `4(b)`, `2,5,7`, `3(a)` into token references;
- preserve raw token text;
- normalize sequence number and optional variant;
- reject or warn on ambiguous tokens;
- avoid writing Matrix authority;
- avoid creating StepInstance.

Parser output must not become domain identity by itself. It is an input to future projection identity references.

## 9. Mock/Fake Lifecycle Assumptions

First implementation should avoid real lifecycle persistence.

Allowed fake assumptions for later TASK_201:

- all parsed tokens default to `not_started` projection;
- fake lifecycle state may be supplied by test fixtures;
- fake stale/report/evidence/attention markers may be supplied by fixtures;
- no persistence or real runtime state is required.

Fake assumptions must be visually and technically marked as fake/test-only in tests or docs.

## 10. Runtime Projection DTO Ownership Boundary

Projection DTOs should be owned by runtime projection/read-model layer when implemented.

They should not be owned by:

- Matrix authority models;
- StepInstance domain models;
- report sync engine;
- frontend components;
- database schema.

Projection DTOs may include:

- project reference;
- Matrix authority reference;
- group reference;
- token reference;
- lifecycle projection;
- evidence projection;
- report sync projection;
- stale projection;
- attention projection.

But each field must remain a projection/read-model field unless a later task creates domain ownership.

## 11. File-Level Implementation Scope

TASK_200 should propose, not execute, candidate file zones for TASK_201.

Potential allowed zones for TASK_201:

- `backend/modules/test_plan/` for token parsing if aligned with existing Matrix parsing code;
- `backend/modules/runtime_projection/` only if a new small module is approved;
- `tests/unit/` for pure token parsing and projection DTO tests;
- `docs/` for task and implementation notes.

Potential files may include:

- `backend/modules/test_plan/matrix_step_token_parser.py`
- `backend/modules/runtime_projection/projection_models.py`
- `tests/unit/test_matrix_step_token_parser.py`
- `tests/unit/test_runtime_projection_models.py`

These are candidates only. TASK_200 must not create them.

## 12. Allowed Implementation Zones

For the future TASK_201 implementation only, likely allowed zones:

- pure parsing;
- pure projection data shapes;
- fake/static projection fixtures;
- unit tests;
- documentation updates;
- task board update after completion.

Allowed implementation must remain:

- deterministic;
- in-memory;
- non-persistent;
- backend-only unless separately approved;
- independent of React/UI/API.

## 13. Forbidden Implementation Zones

TASK_201 should forbid, unless a later plan explicitly allows:

- database schema;
- ORM models;
- API routes;
- frontend components;
- frontend behavior;
- StepInstance persistence;
- real lifecycle persistence;
- report sync implementation;
- evidence/image storage;
- notification implementation;
- cache engine;
- runtime engine;
- mutation of Matrix authority.

TASK_200 must forbid all implementation.

## 14. Validation Strategy

TASK_200 should define validation strategy for TASK_201:

- unit tests for token parser;
- unit tests for projection DTO construction;
- tests for invalid/ambiguous token strings;
- tests for repeated sequence tokens in different groups;
- tests that projection fields do not redefine identity references;
- tests that fake lifecycle/evidence/report/attention markers are optional projection dimensions.

No integration/API/UI tests should be required for the first minimal slice unless TASK_201 expands scope.

## 15. Rollback Boundary

First implementation slice must be easy to roll back.

Rollback safety principles:

- no database migrations;
- no API routes;
- no frontend dependencies;
- no writes to existing Matrix authority records;
- no changes to existing output ledger behavior;
- no dependency injection rewiring;
- no changes to existing production workflows.

Rollback should mean removing the new parser/projection files and related unit tests.

## 16. Static Versus Runtime Tests

Static tests:

- board-state governance tests if task board is updated;
- optional architecture boundary tests if a new module path is introduced.

Runtime/unit tests:

- token parsing behavior;
- projection DTO construction;
- fake projection fixture composition;
- identity/projection separation checks.

Not required for TASK_201 first slice:

- API smoke tests;
- frontend build;
- browser tests;
- database tests;
- Office/Excel/Word tests.

## 17. Minimal Runtime Assumptions

The first implementation slice should assume:

- current Matrix authority is represented by existing ProjectTestPlanDraft data or fixture input;
- StepInstance does not exist yet;
- lifecycle state is fake/static;
- evidence state is fake/static;
- report sync state is fake/static;
- attention state is fake/static;
- no persistence or runtime engine exists.

These assumptions must be stated in TASK_201 so future reviewers do not mistake fake projection data for production runtime behavior.

## 18. Fake Projection Source Strategy

Fake projection source strategy for TASK_201:

- use test fixtures to supply lifecycle/evidence/report/attention states;
- keep fake source data local to tests or explicit fixture helpers;
- avoid hidden defaults that look like real runtime state;
- clearly mark generated projection as fake/static;
- avoid crossing into API or frontend.

Fake projection source should support verifying projection composition without requiring StepInstance or persistence.

## 19. Projection Composition Verification Strategy

TASK_201 should verify:

- identity references are preserved;
- projection dimensions can be attached independently;
- missing projection dimensions do not invalidate identity references;
- token parsing handles sequence and optional variant;
- same token sequence in different groups remains distinct by group reference;
- projection output does not mutate Matrix authority or Project lifecycle.

Verification should happen through pure unit tests.

## 20. Proposed TASK_201 Direction

Recommended next task after TASK_200 approval and completion:

```text
TASK_201_PROJECTION_DTO_AND_TOKEN_PARSING_MINIMAL_SLICE
```

Suggested one-sentence target:

```text
Implement a minimal backend-only, in-memory projection DTO and Matrix step token parser slice with fake projection sources, without persistence, API, frontend, StepInstance, or runtime engine.
```

TASK_201 should still require its own plan and explicit approval.

## 21. Approval Gate

This plan stops before TASK_200 formal execution.

Do not create a TASK_200正文任务文件, do not update `docs/task_board.md`, and do not implement any DTO/parser/runtime/projection/backend/frontend/API/DB code until the user explicitly approves the next step.

TASK_200 does not automatically start TASK_201. TASK_201 requires a separate user request, plan, and approval.
