# TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL

## Status

Planned (awaiting user approval).

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL`

## Why This Task Is Allowed Now

- `TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN` defined the Matrix persistence boundary sequence.
- `TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL` completed immutable Source Matrix import persistence.
- The next controlled step in the approved sequence is editable Project Matrix Draft persistence derived from Source Matrix, before any confirmed authority model.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded backend persistence slice with explicit prior design.
- It requires domain models, SQLAlchemy tables, repository/service logic, and focused tests.
- It does not require frontend workflow changes, confirmed authority semantics, runtime execution, report generation, or new Office parsing.

## Objective

Implement editable Project Matrix Draft persistence from Source Matrix import snapshots.

This task creates the structured draft working-copy layer that can later be edited by Matrix Editor and then confirmed by a separate authority task.

## Scope

Allowed:

- Add domain models for Project Matrix Draft structure:
  - ProjectMatrixDraftRecord
  - ProjectMatrixDraftGroup
  - ProjectMatrixDraftRow
  - ProjectMatrixDraftCell
- Add storage models in a separate module, not by expanding `storage/models.py`.
- Add repository and application service for creating/loading draft working copies from a persisted Source Matrix import.
- Preserve selected groups and group-level sample quantity as draft working-copy state.
- Keep Source Matrix immutable and traceable.
- Add focused unit/integration tests.

Forbidden:

- Confirmed Matrix authority implementation.
- Active confirmed Matrix uniqueness rules.
- Matrix revision flow.
- Runtime execution, StepInstance persistence, report generation, fee/duration/equipment outputs.
- Frontend Matrix Editor save wiring.
- Parser, preview API, or Word/Office gateway changes.
- Reinterpreting `selected_group_keys_at_import` as authority state.

## Acceptance Criteria

- A Project Matrix Draft can be created from one persisted Source Matrix import snapshot.
- Draft records preserve lineage back to `source_matrix_import_records` / `source_matrix_snapshots`.
- Draft selected groups are persisted as editable draft state, not Source Matrix state.
- Draft group sample quantity can be initialized from Source Matrix group sample data and later stored independently.
- Draft rows/cells are persisted as a working copy suitable for later Matrix Editor save wiring.
- Source Matrix rows/groups/cells remain immutable and are not modified by draft creation.
- Manual Matrix source remains outside this task unless represented as an explicit future task.
- Tests cover happy path, selected-group subset behavior, lineage, and no Source Matrix mutation.

## Validation

```powershell
py -m pytest tests\unit\test_project_matrix_draft_persistence_service.py tests\unit\test_project_matrix_draft_repository.py -q
```

```powershell
py -m pytest tests\integration\test_project_matrix_draft_from_source_matrix_api.py tests\unit\test_source_matrix_persistence_service.py -q
```
