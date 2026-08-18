# First Runtime Implementation Slice Planning

> Created: 2026-05-16  
> Task: `TASK_200_FIRST_RUNTIME_IMPLEMENTATION_SLICE_PLANNING`  
> Scope: Planning only. No runtime DTO, parser, projection service, API, database, frontend, StepInstance, report sync, or evidence/image implementation.

## 1. Purpose

TASK_200 converts the governance foundation from TASK_194-TASK_199 into the first minimal runtime implementation-slice plan.

The goal is to move from boundary documents toward a small, reversible, testable first code slice without violating the runtime projection boundaries.

Core governance remains:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
Projection composition must remain independently evolvable.
```

## 2. Key Correction: Reuse Existing Matrix Token Parsing

Future implementation must not re-invent Matrix step token parsing.

Existing module:

```text
backend/modules/test_plan/matrix_step_sequence_validation.py
```

Existing reusable symbols:

- `parse_step_tokens`
- `ParsedStepToken`
- `validate_group_step_sequences`

TASK_201 should consume these existing functions/classes and build runtime projection token references from their output.

TASK_201 should not default to creating:

```text
backend/modules/test_plan/matrix_step_token_parser.py
```

If parsing behavior later needs expansion, that should be a separate parser-hardening task, not hidden inside the runtime projection slice.

## 3. Recommended TASK_201 Name

Recommended next implementation task:

```text
TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE
```

Suggested one-sentence target:

```text
Implement a backend-only, in-memory projection DTO and token reference builder slice using existing Matrix step token parsing, with fake/static projection state fixtures and unit tests only.
```

TASK_201 requires its own plan and explicit approval before code work.

## 4. First Minimal Implementation Slices

Recommended implementation sequence:

1. Projection DTO and token reference builder minimal slice.
2. Fake projection source fixture helper.
3. Pure projection composition helper.
4. Read-only API boundary planning.
5. Read-only API implementation.
6. Matrix Overview UI consumption planning.
7. Matrix Overview UI consumption implementation.

TASK_201 should only cover slice 1, with small fake/static fixture support if needed for tests.

## 5. Projection DTO Slice Boundary

TASK_201 may define lightweight DTO-like structures for runtime projection.

Allowed conceptual structures:

- project reference;
- Matrix authority reference;
- group reference;
- token reference;
- lifecycle projection;
- evidence projection;
- report sync projection;
- stale projection;
- attention projection.

Boundary rules:

- DTOs are projection/read-model structures, not domain entities.
- Identity fields are references, not source truth.
- Lifecycle, evidence, report, stale, and attention fields are projection dimensions.
- DTOs must be in-memory only.
- DTOs must not imply API contracts unless TASK_201 explicitly scopes that, which is not recommended.

## 6. Token Reference Builder Boundary

TASK_201 should build token references from existing parsed tokens.

Expected source input:

- Project reference;
- Matrix authority reference;
- group identity/reference;
- Matrix row or test item reference if available;
- raw Matrix step token cell value;
- parsed tokens from `parse_step_tokens`.

Expected output:

- one token reference per parsed token;
- raw token preserved;
- sequence preserved;
- suffix note preserved;
- group reference preserved;
- Matrix authority reference preserved;
- warnings preserved or surfaced as projection warnings.

The token reference builder must not:

- create StepInstance;
- mutate Matrix authority;
- persist records;
- create lifecycle state;
- hide parser warnings;
- redefine identity from projection markers.

## 7. Fake/Static Lifecycle Assumptions

TASK_201 should avoid real runtime lifecycle.

Allowed assumptions:

- default lifecycle projection can be fake/static, such as `not_started`;
- evidence projection can be fake/static or absent;
- report sync projection can be fake/static or absent;
- stale projection can be fake/static or absent;
- attention projection can be fake/static or absent.

Fake state must be explicit in tests and fixtures. It must not look like production runtime state.

## 8. Runtime Projection DTO Ownership Boundary

Runtime projection DTOs belong to the future runtime projection/read-model layer.

They do not belong to:

- Matrix authority domain;
- StepInstance domain;
- persistence schema;
- report sync engine;
- evidence storage;
- frontend components.

DTO ownership remains projection-only until later approved tasks establish deeper runtime ownership.

## 9. Candidate File-Level Scope For TASK_201

Recommended candidate files:

```text
backend/modules/runtime_projection/__init__.py
backend/modules/runtime_projection/models.py
backend/modules/runtime_projection/token_projection_builder.py
tests/unit/test_runtime_projection_token_builder.py
```

Rationale:

- keeps runtime projection code separate from Matrix authority parsing;
- reuses existing `backend/modules/test_plan/matrix_step_sequence_validation.py`;
- avoids adding a duplicate parser file;
- keeps tests unit-level and in-memory.

TASK_201 should not create:

```text
backend/modules/test_plan/matrix_step_token_parser.py
```

unless a future parser-specific task explicitly approves it.

## 10. Allowed Implementation Zones For TASK_201

Allowed zones:

- backend-only pure functions;
- lightweight projection models;
- token reference builder;
- fake/static projection fixtures for tests;
- unit tests;
- task/document updates.

Allowed behavior:

- deterministic;
- in-memory;
- no side effects;
- no persistence;
- no API exposure;
- no frontend consumption.

## 11. Forbidden Implementation Zones For TASK_201

TASK_201 should continue to forbid:

- DB schema;
- ORM;
- migrations;
- API routes;
- API DTO contracts;
- frontend/React/CSS;
- StepInstance persistence;
- runtime engine;
- cache engine;
- projection engine;
- report sync engine;
- evidence/image storage;
- notification system;
- mutation of Matrix authority;
- changes to existing project output ledger behavior.

## 12. Validation Strategy

TASK_201 should validate:

- token reference builder uses `parse_step_tokens`;
- raw token is preserved;
- sequence is preserved;
- suffix note is preserved;
- group identity remains part of token reference;
- same sequence in different groups remains distinct;
- parser warnings are preserved or surfaced;
- projection dimensions do not redefine identity references;
- missing fake projection dimensions do not invalidate token identity references.

Expected tests:

- unit tests only;
- no API smoke tests;
- no frontend build;
- no database tests;
- no Office tests.

## 13. Rollback Boundary

TASK_201 must be easy to roll back.

Rollback should require removing only:

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
- Office resource cleanup;
- output ledger changes.

## 14. Static Versus Runtime Tests

Static governance tests:

- update board-state tests if task board changes.

Runtime/unit tests:

- token reference builder tests;
- projection model construction tests;
- fake/static projection fixture tests;
- identity/projection separation tests.

Not required:

- integration tests;
- API tests;
- frontend static tests;
- browser tests;
- database tests.

## 15. Minimal Runtime Assumptions

TASK_201 should assume:

- Matrix authority already exists through current `ProjectTestPlanDraft` or test fixture input;
- StepInstance does not exist;
- lifecycle state is fake/static;
- evidence state is fake/static;
- report sync state is fake/static;
- stale state is fake/static;
- attention state is fake/static;
- no persistence or runtime engine exists.

These assumptions must be documented in TASK_201.

## 16. Fake Projection Source Strategy

Fake projection source strategy:

- fake projection states should live in unit test fixtures or explicit helper data;
- fake states should not be hidden production defaults;
- fake states should be optional;
- fake states should not mutate identity references;
- fake states should not imply report sync or evidence storage behavior.

This allows early verification of projection shape without implementing the runtime system.

## 17. Projection Composition Verification Strategy

TASK_201 should verify:

- token reference construction preserves source identity references;
- projection markers can be attached independently;
- projection markers can be omitted independently;
- source parsing warnings remain visible;
- repeated sequence numbers across groups remain distinct;
- projection output never mutates Matrix authority, Project lifecycle, or Step identity.

## 18. TASK_200 Non-Implementation Boundary

TASK_200 implements none of the above.

This document is a planning artifact only. It does not create:

- DTOs;
- dataclasses;
- parsers;
- builders;
- services;
- API routes;
- DB schema;
- frontend components.

## 19. Stop Point

TASK_200 completion does not automatically start TASK_201.

TASK_201 requires:

1. a separate user request;
2. a TASK_201 plan;
3. explicit user approval;
4. then implementation.
