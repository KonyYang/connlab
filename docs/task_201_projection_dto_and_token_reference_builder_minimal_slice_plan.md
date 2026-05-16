# TASK_201 Projection DTO And Token Reference Builder Minimal Slice Plan

> Created: 2026-05-16  
> Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`  
> Proposed task: `TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE`  
> Status: Plan for review. No implementation is approved by this document.

## 1. Current Phase And Task Gate

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current task board state:

```text
TASK_200_FIRST_RUNTIME_IMPLEMENTATION_SLICE_PLANNING complete
Current Active Task: none; TASK_200 first runtime implementation slice planning complete, pending next controlled implementation task
```

Why TASK_201 planning is allowed now:

- TASK_194 established product governance.
- TASK_195 established Runtime Console information architecture.
- TASK_196 established Step-centric domain foundation.
- TASK_197 established Interactive Step Token projection/read-model foundation.
- TASK_198 established Runtime Projection Service/read-model boundary.
- TASK_199 established Matrix Overview consumption boundary at plan stage only.
- TASK_200 established the first runtime implementation-slice plan and corrected TASK_201 toward token reference building rather than parser reinvention.
- The user explicitly approved entering TASK_201 plan preparation.

## 2. Task Name

Use this task name:

```text
TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE
```

Do not use:

```text
TASK_201_PROJECTION_DTO_AND_TOKEN_PARSING_MINIMAL_SLICE
```

Reason:

ConnLab already has Matrix step token parsing foundation. TASK_201 should reuse existing parsing and build token references and projection DTOs on top of it.

## 3. Task Goal

Plan the first minimal backend-only implementation slice:

```text
Projection DTO + Token Reference Builder minimal slice
```

Future TASK_201 implementation should be:

- backend-only;
- in-memory;
- pure function oriented;
- deterministic;
- unit-testable;
- independent of API, DB, frontend, StepInstance, and runtime engines.

TASK_201 is not a complete runtime system.

## 4. Core Governance Rules

TASK_201 must preserve:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
Projection composition must remain independently evolvable.
```

Projection DTO fields are read-model/projection fields. They must not become domain source of truth.

## 5. Plan-Stage Output

This plan stage may create only:

- `docs/task_201_projection_dto_and_token_reference_builder_minimal_slice_plan.md`

This plan stage must not create:

- `tasks/TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE.md`
- runtime projection implementation document;
- backend/frontend/API/DB/runtime code;
- DTO/dataclass implementation;
- parser implementation;
- projection service implementation.

This plan stage must not update:

- `docs/task_board.md`
- backend files;
- frontend files;
- API files;
- database/schema/migration files;
- tests.

## 6. Reuse Existing Matrix Token Parsing

Future TASK_201 implementation must first inspect and reuse:

```text
backend/modules/test_plan/matrix_step_sequence_validation.py
```

Existing reusable symbols:

- `parse_step_tokens`
- `ParsedStepToken`
- `validate_group_step_sequences`

TASK_201 should not default to creating:

```text
backend/modules/test_plan/matrix_step_token_parser.py
```

Only if a future plan proves the existing parser is insufficient, and the user approves a parser-specific task, should a new parser file or parser hardening be considered.

## 7. Recommended Candidate Files For Formal TASK_201

Allowed candidate implementation files after approval:

```text
backend/modules/runtime_projection/__init__.py
backend/modules/runtime_projection/models.py
backend/modules/runtime_projection/token_projection_builder.py
tests/unit/test_runtime_projection_token_builder.py
```

Existing parser module may be imported:

```text
backend/modules/test_plan/matrix_step_sequence_validation.py
```

Not recommended by default:

```text
backend/modules/test_plan/matrix_step_token_parser.py
```

## 8. Projection DTO Scope

Future DTO-like structures may include:

- project reference;
- Matrix authority or draft reference;
- group reference;
- token reference;
- raw token;
- sequence number;
- optional suffix or variant;
- test item label;
- section;
- method;
- condition;
- requirement;
- lifecycle projection;
- evidence projection;
- report sync projection;
- stale projection;
- attention projection.

Boundary:

- These are projection/read-model fields.
- They are not domain source of truth.
- Identity fields are references, not persisted identity owners.
- Projection dimensions must remain independently optional and replaceable.
- DTOs must not imply API contracts in TASK_201.

## 9. Token Reference Builder Scope

Future implementation should build token references from:

- project reference;
- Matrix authority or draft reference;
- group identity;
- Matrix row technical context;
- parsed step token from `parse_step_tokens`.

Future implementation should generate:

- stable token reference;
- minimal InteractiveStepTokenProjection DTO;
- parser warnings surfaced as projection warnings where relevant.

The builder must not:

- create StepInstance;
- persist records;
- mutate Matrix authority;
- mutate Project lifecycle;
- create real lifecycle state;
- hide parser warnings;
- treat projection markers as identity.

## 10. Fake / Mock Projection Source Strategy

TASK_201 may plan fake/static projection state:

- `lifecycle = not_started`;
- `evidence = unknown`;
- `report_sync = unknown`;
- `stale = unknown`;
- `attention = none`.

Alternatively, tests may inject these projection dimensions explicitly through fixtures.

Fake projection state rules:

- fake state is test/placeholder state only;
- fake state is not production runtime state;
- fake state must not imply real lifecycle persistence;
- fake state must not imply evidence/image storage;
- fake state must not imply report sync behavior;
- fake state must not redefine token identity.

## 11. Validation Strategy For Formal TASK_201

Future unit tests should verify:

- token reference preserves project + Matrix authority + group + sequence;
- same sequence in different groups remains distinct;
- raw token is preserved;
- suffix/variant is normalized or preserved according to `ParsedStepToken.suffix_note`;
- parser warnings from `parse_step_tokens` remain visible;
- projection dimensions do not redefine identity;
- missing projection dimensions do not invalidate identity;
- fake lifecycle/evidence/report/attention states remain optional projection dimensions;
- no Matrix authority mutation;
- no Project lifecycle mutation.

Expected test type:

- unit tests only.

Not required:

- API tests;
- DB tests;
- frontend build;
- browser tests;
- Office tests.

## 12. Forbidden Scope For Formal TASK_201

TASK_201 must forbid:

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
- changes to existing production workflow.

TASK_201 should also avoid changing existing parser behavior unless a narrow test-proven parser defect is explicitly approved.

## 13. UI Direction Constraint

TASK_201 does not implement UI.

Future UI work should treat the current frontend Project Workbench page as a temporary shell, not as a refinement target.

Future Project Workbench UI should move toward the supplied Project Workbench target baseline:

- runtime console first;
- Matrix Overview as the main runtime map;
- right-side Step Workspace;
- top-level runtime progress and attention states;
- Setup Manager demoted to supporting access.

Future Matrix Editor should be a separate page following the supplied Matrix Editor target baseline:

- definition studio responsibility;
- test item library and templates;
- Matrix definition editing;
- group/step preview;
- not embedded back into Workbench runtime execution.

Do not put Matrix definition editing back into Workbench.

## 14. Rollback Boundary For Formal TASK_201

Future TASK_201 should be easy to roll back.

Rollback should only require removing:

- `backend/modules/runtime_projection/__init__.py`
- `backend/modules/runtime_projection/models.py`
- `backend/modules/runtime_projection/token_projection_builder.py`
- `tests/unit/test_runtime_projection_token_builder.py`
- TASK_201 docs/task-board updates.

Rollback must not require:

- database rollback;
- API route removal;
- frontend rollback;
- migration reversal;
- output ledger changes;
- Matrix authority data correction.

## 15. Acceptance Criteria For Formal TASK_201

Future TASK_201 should be accepted only if:

- it uses existing `parse_step_tokens` / `ParsedStepToken`;
- it does not create a duplicate default parser;
- it creates only backend-only in-memory projection DTO/reference builder code;
- it has focused unit tests;
- it does not touch API/DB/frontend/runtime engine;
- identity references remain separate from projection dimensions;
- fake projection states are explicit and optional.

## 16. Stop Condition

This plan stops before TASK_201 formal execution.

Do not create:

- `tasks/TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE.md`
- runtime implementation docs;
- backend/frontend/API/DB/runtime code;
- DTO/dataclass implementation;
- parser implementation;
- projection service implementation.

Do not update `docs/task_board.md`.

Wait for user review and explicit approval before entering TASK_201 formal execution.
