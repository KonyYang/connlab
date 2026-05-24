# TASK_206 Runtime Projection Read-Only API Adapter Minimal Slice

Status: done
Date: 2026-05-16

## Execution Mode

Single-file task mode.

This file contains both:

- the reviewable task plan
- the later execution record

Do not create a separate `docs/task_206_*_plan.md` file for this task.

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
TASK_206_RUNTIME_PROJECTION_READ_ONLY_API_ADAPTER_MINIMAL_SLICE pending user review
```

Why this task is allowed:

- TASK_201 created token projection DTO-like structures and token reference builder.
- TASK_202 created deterministic projection composition summary.
- TASK_204 created Matrix Overview and Step Workspace read-only consumer views.
- TASK_205 created a runtime projection snapshot adapter that composes existing pure functions.
- The next minimal consumable slice is read-only API adaptation of snapshot output for external consumers.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- The task is a bounded backend integration slice: one new read-only route module, one DTO mapping layer, and focused API/unit tests.
- Existing runtime projection logic is already implemented; TASK_206 should reuse and adapt, not redesign architecture.
- Scope is deterministic and low-ambiguity if the task keeps strict no-persistence/no-runtime-engine boundaries.

Escalate to a stronger model only if implementation reveals a contradiction between current API patterns and runtime projection boundary constraints.

## Goal

Expose a minimal read-only runtime projection snapshot through backend API adapters for consumption, without introducing persistence, runtime engines, or frontend changes.

## Scope

TASK_206 should provide:

- a read-only API route that returns runtime projection snapshot data from in-memory/fake/static inputs
- API DTO mapping boundary for snapshot output
- deterministic response shape for Matrix Overview and optional Step Workspace
- focused tests for route behavior and boundary constraints

This is an adapter slice, not runtime execution implementation.

## File Scope

Allowed implementation files:

- `backend/api/routes_runtime_projection_read_only.py`
- `backend/api/main.py`
- `tests/integration/test_runtime_projection_read_only_api.py`
- `tests/unit/test_runtime_projection_read_only_api_mapping.py`
- `backend/modules/runtime_projection/__init__.py` (only if needed for explicit export)
- `tasks/TASK_206_RUNTIME_PROJECTION_READ_ONLY_API_ADAPTER_MINIMAL_SLICE.md`
- `docs/task_board.md`

Avoid changing unless proven necessary:

- `backend/modules/runtime_projection/models.py`
- `backend/modules/runtime_projection/token_projection_builder.py`
- `backend/modules/runtime_projection/composition.py`
- `backend/modules/runtime_projection/consumer_views.py`
- `backend/modules/runtime_projection/snapshot_adapter.py`

## API Boundary

Recommended endpoint shape:

```text
POST /runtime-projection/read-only-snapshot
```

Request body should contain minimal build input equivalent to `SnapshotBuildInput`.

Response should contain:

- project reference
- matrix reference
- parser warnings
- runtime projection summary
- matrix overview consumer output
- optional step workspace consumer output

The route should:

- call snapshot adapter only
- keep deterministic behavior
- return typed Pydantic response models
- avoid business mutation

## Forbidden Scope

TASK_206 must not implement:

- database schema
- ORM/dataclass persistence
- migrations
- frontend/React/CSS
- StepInstance
- lifecycle persistence
- runtime engine
- cache engine
- report sync engine
- evidence/image storage
- notification system
- matrix editor behavior
- workbench UI replacement
- mutation of Matrix authority
- mutation of Project lifecycle
- parser duplication

## Validation Strategy

Focused tests should cover:

- health of new read-only route registration
- valid request returns deterministic snapshot output
- selected token reference present vs missing behavior
- parser warnings visible in API response
- same sequence in different groups remains distinct in response
- no persistence side effects
- no mutation of input identity fields
- no runtime engine behavior introduced

Run:

```powershell
py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py -q
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

TASK_206 is complete when:

- a read-only runtime projection API adapter route exists and is wired in `backend/api/main.py`
- route uses existing snapshot adapter and does not duplicate runtime projection logic
- response is typed and deterministic
- tests verify read-only boundary and behavior
- no DB/API mutation side effects are introduced beyond read-only response serving
- `docs/task_board.md` is updated after completion

## Execution Record

Completed.

Implemented files:

- `backend/api/routes_runtime_projection_read_only.py`
- `backend/api/main.py`
- `tests/integration/test_runtime_projection_read_only_api.py`
- `tests/unit/test_runtime_projection_read_only_api_mapping.py`

Board/document updates:

- `docs/task_board.md`

What was implemented:

- Added a read-only runtime projection snapshot API route:
  - `POST /api/runtime-projection/read-only-snapshot`
- Added request/response DTO mapping boundary in API route module.
- Reused existing runtime projection composition chain:
  - `build_runtime_projection_snapshot` (TASK_205)
  - no duplicated parser logic
  - no runtime engine/persistence/UI behavior
- Wired route into backend FastAPI app via `backend/api/main.py`.

Validation results:

- `py -m pytest tests\integration\test_runtime_projection_read_only_api.py tests\unit\test_runtime_projection_read_only_api_mapping.py -q`
  - `4 passed`
- `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q`
  - `45 passed`

Stop condition:

- TASK_206 completed and stopped.
- Did not auto-enter next task.
