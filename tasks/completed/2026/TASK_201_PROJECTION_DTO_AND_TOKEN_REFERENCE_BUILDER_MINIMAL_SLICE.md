# TASK_201 Projection DTO And Token Reference Builder Minimal Slice

## Status

done

## Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Goal

Implement the first minimal backend-only runtime slice:

- projection DTO-like structures;
- token reference builder;
- fake/static projection state;
- pure unit tests.

The slice must stay in-memory, deterministic, and pure function oriented.

## Scope

Implemented:

- `backend/modules/runtime_projection/models.py`
- `backend/modules/runtime_projection/token_projection_builder.py`
- `backend/modules/runtime_projection/__init__.py`
- `tests/unit/test_runtime_projection_token_builder.py`

Reused existing parser foundation:

- `backend/modules/test_plan/matrix_step_sequence_validation.py`
  - `parse_step_tokens`
  - `ParsedStepToken`
  - `validate_group_step_sequences`

Explicitly not created:

- `backend/modules/test_plan/matrix_step_token_parser.py`

## Boundary

This task keeps:

```text
Projection != Domain Identity
Runtime Projection is not source of truth.
Projection composition must remain independently evolvable.
```

Projection fields are read-model/projection fields only. They are not domain source of truth.

## Out Of Scope

Not implemented:

- database schema;
- ORM models;
- migrations;
- API routes;
- frontend components;
- React/CSS;
- StepInstance persistence;
- real lifecycle persistence;
- runtime service/projection service engines;
- report sync implementation;
- evidence/image storage;
- notification implementation;
- cache engine;
- runtime engine;
- mutation of Matrix authority;
- mutation of Project lifecycle;
- production workflow changes.

## Validation

Focused unit tests:

```powershell
python -m pytest -q tests/unit/test_runtime_projection_token_builder.py
```

Existing parser-related tests:

```powershell
python -m pytest -q tests/unit/test_matrix_step_sequence_validation.py
```

Board-state governance guard tests (because board updated):

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Stop Point

TASK_201 completes here and does not automatically enter the next task.
