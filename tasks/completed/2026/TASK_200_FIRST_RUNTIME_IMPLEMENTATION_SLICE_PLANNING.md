# TASK_200 First Runtime Implementation Slice Planning

## Status

done

## Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Goal

Convert the TASK_194-TASK_199 governance foundation into a concrete first runtime implementation-slice plan.

This task is planning only. It does not implement runtime DTOs, token reference builders, parser code, projection services, API routes, database schema, frontend components, StepInstance, report sync, or evidence/image behavior.

## Key Correction

Future TASK_201 must not reimplement Matrix token parsing.

Existing reusable parsing and validation live in:

```text
backend/modules/test_plan/matrix_step_sequence_validation.py
```

Existing public symbols:

- `parse_step_tokens`
- `ParsedStepToken`
- `validate_group_step_sequences`

TASK_201 should build token references on top of this existing module instead of creating a duplicate parser such as:

```text
backend/modules/test_plan/matrix_step_token_parser.py
```

## Recommended Next Task

Future TASK_201 recommendation:

```text
TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE
```

Suggested goal:

```text
Implement a backend-only, in-memory projection DTO and token reference builder slice using existing Matrix step token parsing, with fake/static projection state fixtures and unit tests only.
```

TASK_201 still requires a separate user request, plan, and approval.

## In Scope

Define:

1. first minimal implementation slices;
2. Projection DTO slice boundary;
3. token reference builder boundary;
4. fake lifecycle assumptions;
5. runtime projection DTO ownership boundary;
6. candidate file-level implementation scope;
7. allowed implementation zones;
8. forbidden implementation zones;
9. validation strategy;
10. rollback boundary;
11. static versus runtime tests;
12. minimal runtime assumptions;
13. fake projection source strategy;
14. projection composition verification strategy.

## Out Of Scope

Do not implement:

- runtime projection DTOs;
- token reference builder;
- parser changes;
- backend runtime service;
- ORM models;
- persistence;
- SQLite schema;
- API routes;
- frontend/React/CSS;
- StepInstance persistence;
- runtime engine;
- report sync engine;
- evidence/image storage.

## Deliverables

- `docs/first_runtime_implementation_slice_planning.md`
- `docs/task_200_first_runtime_implementation_slice_planning_plan.md`
- `tasks/TASK_200_FIRST_RUNTIME_IMPLEMENTATION_SLICE_PLANNING.md`
- `docs/task_board.md` update

## Acceptance Criteria

- TASK_200 records that future TASK_201 should be `TASK_201_PROJECTION_DTO_AND_TOKEN_REFERENCE_BUILDER_MINIMAL_SLICE`.
- TASK_200 records that TASK_201 should reuse `backend/modules/test_plan/matrix_step_sequence_validation.py`.
- TASK_200 records that TASK_201 should not create a duplicate default parser at `backend/modules/test_plan/matrix_step_token_parser.py`.
- TASK_200 scopes TASK_201 to backend-only, in-memory, pure-function implementation.
- TASK_200 scopes TASK_201 to runtime projection DTO-like structures, token reference builder, fake/static projection state fixtures, and unit tests.
- TASK_200 keeps DB schema, ORM, API routes, frontend/React/CSS, StepInstance persistence, runtime engine, report sync engine, and evidence/image storage forbidden for TASK_201.
- TASK_200 recommends candidate TASK_201 files:
  - `backend/modules/runtime_projection/__init__.py`
  - `backend/modules/runtime_projection/models.py`
  - `backend/modules/runtime_projection/token_projection_builder.py`
  - `tests/unit/test_runtime_projection_token_builder.py`
- TASK_200 does not implement runtime code.
- TASK_200 completion does not automatically start TASK_201.

## Validation

Document-level consistency check:

- confirm TASK_200 task file exists;
- confirm TASK_200 planning document exists;
- confirm task board records TASK_200 completion;
- confirm no backend/frontend/API/DB runtime source files were intentionally changed.

Static governance guard tests:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

