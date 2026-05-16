# TASK_204 Runtime Projection Read-Only Consumer Minimal Slice

Status: done
Date: 2026-05-16

## Execution Mode

Single-file task mode.

This file contains both:

- the reviewable task plan
- the later execution record

Do not create a separate `docs/task_204_*_plan.md` file for this task.

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
TASK_204_RUNTIME_PROJECTION_READ_ONLY_CONSUMER_MINIMAL_SLICE pending user review
```

Why this task is allowed:

- TASK_201 created projection DTO-like structures and token reference builder.
- TASK_202 created deterministic projection composition summaries.
- TASK_203 completed documentation information architecture cleanup.
- Runtime governance now requires consumer-first runtime slices rather than more governance-only work.
- The user confirmed the consumer output should include minimal versions for both Matrix Overview and Step Workspace.

## Expert Guidance Evaluation

The attached `ConnLab_Runtime_Task_Sequencing_Guide.docx` is accepted as directionally sound:

- Do not start Runtime Console UI replacement yet.
- Runtime Console must consume stable runtime outputs instead of defining runtime shape.
- Continue sequence: Projection -> Aggregation -> Immutable Runtime Read Model -> Consumer Prototype -> UI.
- Keep Project Workbench as future Runtime Console and Matrix Editor as separate Definition Studio.
- Avoid StepInstance ORM, runtime engine, orchestration graph, and UI-first runtime design.

Adjustment:

- The expert document names the next adapter task as TASK_203, but this repository already used TASK_203 for documentation cleanup. The next implementation slice is TASK_204.

## Goal

Implement the first backend-only, in-memory, deterministic read-only runtime projection consumer outputs for both Matrix Overview and Step Workspace, without creating a runtime engine, API, persistence, or UI.

## Scope

TASK_204 should produce directly consumable runtime outputs:

- Matrix Overview minimal consumer view
- Step Workspace minimal consumer view
- deterministic adapter functions from existing projection outputs
- focused unit tests proving consumer outputs do not redefine identity or authority

This is an implementation slice, not a governance-only task.

## File Scope

Allowed implementation files:

- `backend/modules/runtime_projection/consumer_views.py`
- `tests/unit/test_runtime_projection_consumer_views.py`
- `backend/modules/runtime_projection/__init__.py`
- `docs/task_board.md`

Avoid changing unless proven necessary:

- `backend/modules/runtime_projection/models.py`

Reason:

- Projection minimality rule says new DTOs are forbidden unless existing DTOs are proven insufficient.
- Existing `InteractiveStepTokenProjection` and `RuntimeProjectionSummary` can support consumer views without expanding core model ontology.
- If consumer outputs need named immutable structures, define them in `consumer_views.py` as consumer-facing dataclasses rather than expanding core projection identity.

## Matrix Overview Consumer Output

Minimum responsibility:

- expose grouped runtime overview data from existing token projections
- preserve group identity and label
- expose token count and sequence count
- expose token references suitable for later Matrix Overview rendering
- expose projection markers as already supplied dimensions
- expose deterministic empty output for no projections

Candidate local output concepts:

- `MatrixOverviewConsumerView`
- `MatrixOverviewGroupView`
- `MatrixOverviewTokenView`

These are consumer/read-model outputs only. They are not source of truth and do not own Step identity.

## Step Workspace Consumer Output

Minimum responsibility:

- expose selected token projection by stable token reference
- expose technical row context for the selected token
- expose lifecycle/evidence/report/stale/attention projections
- expose group context from existing input projections
- expose neighboring token references where deterministic
- return a clear not-found output when token reference does not exist

Candidate local output concepts:

- `StepWorkspaceConsumerView`
- `SelectedStepTokenView`

These are read-only consumer outputs. They must not create StepInstance.

## Adapter Function Boundary

Recommended functions:

```text
build_matrix_overview_consumer_view(projections)
build_step_workspace_consumer_view(projections, selected_token_reference)
```

Inputs:

- tuple of `InteractiveStepTokenProjection`
- selected token reference for Step Workspace view

Outputs:

- immutable read-only consumer views
- no mutation of input projections
- no authority update
- no lifecycle update

## Forbidden Scope

TASK_204 must not implement:

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

- Matrix Overview groups tokens by stable group identity.
- Matrix Overview exposes token references without redefining identity.
- same sequence in different groups remains distinct.
- projection markers remain read-only consumer fields.
- Step Workspace selects a token by stable reference.
- Step Workspace not-found result is deterministic.
- missing projection dimensions do not invalidate token identity.
- consumer view functions do not mutate input projections.
- no Matrix authority mutation.
- no Project lifecycle mutation.
- fake/static projection fixtures remain acceptable test input.

Run:

```powershell
py -m pytest tests\unit\test_runtime_projection_consumer_views.py -q
```

Also run:

```powershell
py -m pytest tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q
```

If `docs/task_board.md` or board-state tests are updated:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## Acceptance Criteria

TASK_204 is complete when:

- consumer view functions exist and are backend-only/in-memory/pure.
- Matrix Overview and Step Workspace each have a minimal consumable output.
- outputs are deterministic and immutable.
- tests prove projection consumption does not mutate identity, authority, or lifecycle.
- no runtime engine, API, UI, DB, or StepInstance is introduced.
- `docs/task_board.md` is updated after completion.

## Execution Record

Completed.

Implemented files:

- `backend/modules/runtime_projection/consumer_views.py`
- `tests/unit/test_runtime_projection_consumer_views.py`
- `backend/modules/runtime_projection/__init__.py`

Board/document updates:

- `docs/task_board.md`

What was implemented:

- Added immutable, backend-only, in-memory consumer read models for Matrix Overview and Step Workspace:
  - `MatrixOverviewConsumerView`
  - `MatrixOverviewGroupView`
  - `MatrixOverviewTokenView`
  - `StepWorkspaceConsumerView`
  - `SelectedStepTokenView`
- Added pure-function builders:
  - `build_matrix_overview_consumer_view(projections)`
  - `build_step_workspace_consumer_view(projections, selected_token_reference)`
- Preserved runtime boundary:
  - no DB/API/UI/runtime engine/persistence changes
  - no parser duplication
  - no mutation of Matrix authority or Project lifecycle

Validation results:

- `py -m pytest tests\unit\test_runtime_projection_consumer_views.py -q`
  - `12 passed`
- `py -m pytest tests\unit\test_runtime_projection_token_builder.py tests\unit\test_runtime_projection_composition.py -q`
  - `23 passed`

Stop condition:

- TASK_204 completed and stopped.
- Did not auto-enter next task.
