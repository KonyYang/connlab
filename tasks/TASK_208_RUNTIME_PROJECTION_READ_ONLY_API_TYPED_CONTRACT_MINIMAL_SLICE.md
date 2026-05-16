# TASK_208 Runtime Projection Read-Only API Typed Contract Minimal Slice

Status: done
Date: 2026-05-16

## Execution Mode

Single-file task mode.

This file contains both:

- the reviewable task plan
- the later execution record

Do not create a separate `docs/task_208_*_plan.md` file for this task.

Approval rule:

- Before approval, only this task file may be reviewed and adjusted.
- After explicit user approval, implementation may proceed directly from this task file.
- After implementation, append the execution result to the `Execution Record` section and update `docs/task_board.md`.

## Current Phase / Active Task / Allowance

Current phase:

```text
Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
```

Current active task:

```text
TASK_208_RUNTIME_PROJECTION_READ_ONLY_API_TYPED_CONTRACT_MINIMAL_SLICE pending user review
```

Why this task is allowed:

- TASK_206 already exposed read-only runtime projection API route.
- TASK_207 synced API contract docs to the new route.
- Current API response shape still uses broad `dict[str, Any]` fields for nested runtime snapshot payloads.
- The next minimal consumable slice is typed contract hardening for stable downstream consumption.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- This is a bounded backend refactor of API schema typing and mapper tests.
- No runtime engine/persistence/UI work is involved.
- Existing runtime projection pure functions remain unchanged.

Escalate to a stronger model only if typed contract extraction reveals cross-module boundary contradictions.

## Goal

Harden `POST /api/runtime-projection/read-only-snapshot` response contract from generic nested dictionaries to explicit typed Pydantic response models, while preserving read-only behavior and deterministic output.

## Scope

TASK_208 should:

- define explicit typed API response models for runtime summary, matrix overview, and step workspace projections
- replace generic `dict[str, Any]` response members in runtime projection route
- keep existing route path and request shape backward-compatible where possible
- add focused tests for response contract stability

This is contract hardening, not runtime behavior expansion.

## File Scope

Allowed implementation files:

- `backend/api/routes_runtime_projection_read_only.py`
- `tests/integration/test_runtime_projection_read_only_api.py`
- `tests/unit/test_runtime_projection_read_only_api_mapping.py`
- `tests/unit/test_runtime_projection_read_only_api_contract.py`
- `tasks/TASK_208_RUNTIME_PROJECTION_READ_ONLY_API_TYPED_CONTRACT_MINIMAL_SLICE.md`
- `docs/task_board.md`

Avoid changing unless proven necessary:

- `backend/modules/runtime_projection/snapshot_adapter.py`
- `backend/modules/runtime_projection/consumer_views.py`
- `backend/modules/runtime_projection/composition.py`
- `backend/modules/runtime_projection/token_projection_builder.py`

## Contract Boundary

Must preserve:

- same route: `POST /api/runtime-projection/read-only-snapshot`
- read-only behavior
- deterministic output semantics
- projection boundary principles:
  - Projection != Domain Identity
  - Runtime Projection is not source of truth

Must improve:

- remove `dict[str, Any]` response placeholders
- expose explicit nested response models for:
  - parser warnings
  - runtime projection summary
  - matrix overview groups/tokens
  - optional step workspace selection state

## Forbidden Scope

TASK_208 must not implement:

- database schema or ORM changes
- persistence or runtime engine
- frontend/React/CSS
- StepInstance implementation
- API write endpoints for runtime projection
- matrix authority mutation
- project lifecycle mutation
- parser duplication

## Validation Strategy

Focused tests should cover:

- typed response model validation for normal payload
- typed response model validation for empty payload
- typed response model validation when selected token is missing
- parser warnings remain visible and typed
- route remains read-only and deterministic
- existing snapshot composition tests remain green

Run:

```powershell
py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py tests\unit\test_runtime_projection_read_only_api_contract.py -q
```

Also run:

```powershell
py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q
```

If `docs/task_board.md` or board-state tests are updated:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Acceptance Criteria

TASK_208 is complete when:

- runtime projection read-only API response uses explicit typed nested models
- route path and read-only semantics are preserved
- contract tests pass
- no runtime projection domain behavior is changed
- no persistence or runtime engine is introduced
- `docs/task_board.md` is updated after completion

## Execution Record

Completed.

Implemented files:

- `backend/api/routes_runtime_projection_read_only.py`
- `tests/unit/test_runtime_projection_read_only_api_contract.py`
- `tests/integration/test_runtime_projection_read_only_api.py`
- `tests/unit/test_runtime_projection_read_only_api_mapping.py`

Board/document updates:

- `docs/task_board.md`

What was implemented:

- Replaced broad dictionary response placeholders with explicit nested typed Pydantic response models in runtime projection read-only route.
- Preserved route path and read-only behavior:
  - `POST /api/runtime-projection/read-only-snapshot`
- Kept runtime projection composition behavior unchanged and reused existing snapshot adapter path.
- Added API contract unit tests for typed response models and null workspace case.

Validation results:

- `py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py tests\unit\test_runtime_projection_read_only_api_contract.py -q`
  - `6 passed`
- `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q`
  - `45 passed`

Stop condition:

- TASK_208 completed and stopped.
- Did not auto-enter next task.
