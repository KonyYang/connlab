# TASK_205 Runtime Projection Snapshot Adapter Minimal Slice

Status: done
Date: 2026-05-16

## Execution Mode

Single-file task mode.

This file contains both:

- the reviewable task plan
- the later execution record

Do not create a separate `docs/task_205_*_plan.md` file for this task.

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
TASK_205_RUNTIME_PROJECTION_SNAPSHOT_ADAPTER_MINIMAL_SLICE pending user review
```

Why this task is allowed:

- TASK_201 created projection DTO-like structures and token reference builder.
- TASK_202 created deterministic projection composition summaries.
- TASK_204 created read-only consumer outputs for Matrix Overview and Step Workspace.
- Runtime governance now requires consumer-first slices that produce directly consumable runtime artifacts.
- The next useful artifact is a deterministic snapshot adapter that composes existing pure functions into one frontend/API-consumable runtime output without introducing API, DB, runtime engine, or UI.

## Model Fit Assessment

Recommended execution model:

```text
GPT-5.3-codex: suitable
```

Reason:

- The task is a narrow backend coding slice with pure functions, immutable outputs, and unit tests.
- It requires careful reuse of existing modules rather than broad product reasoning.
- It should not require frontier-level architecture exploration if the scope stays inside the approved runtime projection boundary.

Escalate to a stronger general model only if implementation reveals an architectural contradiction across Matrix authority, Project lifecycle, or runtime projection boundaries.

Future task rule:

- Every new task file must include a `Model Fit Assessment` section.
- The section must explicitly state whether `GPT-5.3-codex` is suitable for execution and why.

## Goal

Implement a minimal backend-only, in-memory, deterministic Runtime Projection Snapshot Adapter that composes existing projection builders, aggregation helpers, and consumer views into one directly consumable runtime snapshot.

This is not a runtime engine.

## Scope

TASK_205 should produce one narrow adapter layer:

- input: already-known project/matrix/group row data and optional selected token reference
- internal composition: existing token projection builder, existing runtime composition summary, existing Matrix Overview consumer view, existing Step Workspace consumer view
- output: immutable runtime snapshot object
- tests: prove deterministic composition, no mutation, no authority/lifecycle ownership, no parser duplication

The snapshot should be suitable for later API or frontend read-only consumption, but TASK_205 must not implement API routes or frontend behavior.

## File Scope

Allowed implementation files:

- `backend/modules/runtime_projection/snapshot_adapter.py`
- `tests/unit/test_runtime_projection_snapshot_adapter.py`
- `backend/modules/runtime_projection/__init__.py`
- `tasks/TASK_205_RUNTIME_PROJECTION_SNAPSHOT_ADAPTER_MINIMAL_SLICE.md`
- `docs/task_board.md`

Avoid changing unless proven necessary:

- `backend/modules/runtime_projection/models.py`
- `backend/modules/runtime_projection/consumer_views.py`
- `backend/modules/runtime_projection/composition.py`
- `backend/modules/runtime_projection/token_projection_builder.py`

Reason:

- TASK_205 should compose existing primitives rather than expanding projection ontology.
- New core DTOs are forbidden unless existing outputs are proven insufficient.
- If named snapshot structures are needed, define them locally in `snapshot_adapter.py` as adapter-facing immutable dataclasses.

## Proposed Adapter Output

Candidate local output concepts:

- `RuntimeProjectionSnapshot`
- `SnapshotBuildInput`
- `SnapshotMatrixRowInput`

Minimum `RuntimeProjectionSnapshot` content:

- project reference
- matrix reference
- parser warnings
- runtime projection summary from TASK_202
- Matrix Overview consumer view from TASK_204
- optional Step Workspace consumer view from TASK_204

These are adapter/read-model outputs only.

They are not source of truth and must not own:

- Project lifecycle
- Matrix authority
- Step identity
- runtime execution state

## Adapter Function Boundary

Recommended function:

```text
build_runtime_projection_snapshot(input_data)
```

The function may internally call:

- `build_step_token_projections`
- `compose_runtime_projection_summary`
- `build_matrix_overview_consumer_view`
- `build_step_workspace_consumer_view`

The function must not:

- call database repositories
- call API code
- call frontend code
- create StepInstance
- persist lifecycle state
- infer real execution state
- mutate Matrix authority
- mutate Project lifecycle

## Input Boundary

TASK_205 may define local immutable input dataclasses for testable adapter input.

Candidate input fields:

- project reference
- matrix reference
- group identity
- group label
- matrix row technical context
- raw matrix step token string
- optional selected token reference
- optional projection state fixture

Projection state fixture remains fake/static test input unless future runtime tasks explicitly replace it with real runtime sources.

## Forbidden Scope

TASK_205 must not implement:

- database schema
- ORM/dataclass persistence
- API routes
- frontend/React/CSS
- StepInstance
- lifecycle persistence
- runtime engine
- cache/refresh engine
- report sync engine
- evidence/image storage
- notification system
- Matrix Editor
- Workbench UI replacement
- mutation of Matrix authority
- mutation of Project lifecycle
- new Matrix token parser

## Validation Strategy

Focused unit tests should cover:

- snapshot includes project and matrix references.
- snapshot builds Matrix Overview consumer output from multiple rows.
- snapshot builds optional Step Workspace consumer output when a selected token reference exists.
- snapshot not-found selected token remains deterministic.
- parser warnings are collected and remain visible.
- same sequence in different groups remains distinct.
- fake/static projection dimensions pass through without becoming source of truth.
- snapshot adapter does not mutate input row data.
- no Matrix authority mutation.
- no Project lifecycle mutation.
- no duplicate parser file is introduced.

Run:

```powershell
py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py -q
```

Also run:

```powershell
py -m pytest tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q
```

If `docs/task_board.md` or board-state tests are updated:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Acceptance Criteria

TASK_205 is complete when:

- snapshot adapter functions exist and are backend-only/in-memory/pure.
- snapshot output composes TASK_201, TASK_202, and TASK_204 outputs.
- Matrix Overview and optional Step Workspace consumer outputs are directly available from the snapshot.
- parser warnings remain visible.
- outputs are deterministic and immutable.
- tests prove snapshot construction does not mutate identity, authority, or lifecycle.
- no runtime engine, API, UI, DB, or StepInstance is introduced.
- `docs/task_board.md` is updated after completion.

## Execution Record

Completed.

Implemented files:

- `backend/modules/runtime_projection/snapshot_adapter.py`
- `tests/unit/test_runtime_projection_snapshot_adapter.py`
- `backend/modules/runtime_projection/__init__.py`

Board/document updates:

- `docs/task_board.md`

What was implemented:

- Added immutable snapshot adapter inputs and output:
  - `SnapshotMatrixRowInput`
  - `SnapshotBuildInput`
  - `RuntimeProjectionSnapshot`
- Added pure-function builder:
  - `build_runtime_projection_snapshot(build_input)`
- Composed existing runtime projection primitives:
  - `build_step_token_projections` (TASK_201)
  - `compose_runtime_projection_summary` (TASK_202)
  - `build_matrix_overview_consumer_view` (TASK_204)
  - `build_step_workspace_consumer_view` (TASK_204)
- Preserved runtime boundary:
  - no DB/API/UI/runtime engine/persistence changes
  - no parser duplication
  - no mutation of Matrix authority or Project lifecycle

Validation results:

- `py -m pytest tests\unit\test_runtime_projection_snapshot_adapter.py -q`
  - `10 passed`
- `py -m pytest tests\unit\test_runtime_projection_consumer_views.py tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q`
  - `35 passed`

Stop condition:

- TASK_205 completed and stopped.
- Did not auto-enter next task.
