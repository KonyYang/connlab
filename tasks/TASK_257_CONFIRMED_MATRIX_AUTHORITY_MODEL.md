# TASK_257_CONFIRMED_MATRIX_AUTHORITY_MODEL

## Status

Planned. Awaiting user approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_257_CONFIRMED_MATRIX_AUTHORITY_MODEL` is planned only.

## Why This Task Is Allowed Now

- `TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN` defined Confirmed Matrix authority as the next persistence boundary after editable drafts.
- `TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL` persisted immutable Source Matrix lineage.
- `TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL` persisted structured editable Project Matrix Drafts.
- `TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING` wired Matrix Editor Save into Project Matrix Draft persistence.
- The next controlled boundary is confirming a saved draft into immutable Matrix authority before any runtime, report, fee, duration, equipment, or revision-flow consumer work.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded backend persistence and API slice with an existing design baseline.
- It requires SQLAlchemy models, domain dataclasses, repository/service orchestration, and focused tests.
- It does not require broad UI design, Office parsing, runtime execution, report generation, multi-user concurrency, or AI reasoning beyond deterministic mapping/validation.

## Objective

Implement the first Confirmed Matrix authority persistence model.

This task confirms one saved `ProjectMatrixDraft` into an immutable project-scoped authority snapshot that future execution/read-model/report consumers can read later. It must not implement revision flow, runtime execution, StepInstance, report generation, or frontend publish wiring.

## Scope

Allowed:

- Add Confirmed Matrix domain models and status enum:
  - `ConfirmedMatrixVersion`
  - `ConfirmedMatrixGroup`
  - `ConfirmedMatrixRow`
  - `ConfirmedMatrixCell`
- Add separate SQLAlchemy storage model module for confirmed Matrix authority.
- Add repository methods to create and load confirmed Matrix authority snapshots.
- Add application service to confirm one existing `ProjectMatrixDraft` into one immutable active `ConfirmedMatrixVersion`.
- Add a minimal backend API route if required for integration tests.
- Enforce project-level single active confirmed authority for this first authority slice.
- Reject confirmation if the project already has an active confirmed Matrix. Superseding/revision flow is reserved for `TASK_258_MATRIX_REVISION_FLOW`.
- Copy only selected draft groups into confirmed authority groups.
- Copy rows and sparse non-empty cells for selected confirmed groups.
- Preserve lineage back to draft, source import/snapshot, source groups, and source rows where available.
- Persist group-level sample quantity expression as confirmed group authority data.
- Add focused unit/integration tests.
- Update `docs/task_board.md` after completion.

Forbidden:

- Matrix revision flow or superseding an existing active confirmed Matrix.
- Editing or updating confirmed Matrix rows/groups/cells after creation.
- Frontend `Publish for approval` / `Confirm Matrix` wiring.
- Runtime execution, StepInstance persistence, evidence/image management, test records, report generation, fee, duration, or equipment outputs.
- Report/readiness projection changes.
- Confirmed Step Output generation from step preview logic.
- Parser, preview API, Word/Office gateway, or Matrix import UI changes.
- Mutating Source Matrix import/snapshot rows.
- Mutating Project Matrix Draft content while confirming, except optional status metadata if explicitly documented in the implementation plan.
- Direct repository calls from API routes.
- Multi-user/LAN optimistic concurrency or lock management.

## Acceptance Criteria

- A saved `ProjectMatrixDraft` can be confirmed into one immutable `ConfirmedMatrixVersion`.
- Confirmed Matrix root preserves:
  - `project_id`
  - `project_matrix_draft_id`
  - `source_import_id`
  - `source_snapshot_id`
  - `confirmed_revision`
  - `is_active_authority`
  - `status`
  - `confirmed_by`
  - `confirmed_at`
- The first confirmed revision for a project is created as active authority.
- If an active confirmed Matrix already exists for the project, confirmation returns a conflict-style application error and does not create partial confirmed rows.
- Confirmed groups include only draft groups where `is_selected = true`.
- Confirmation fails if no selected draft groups exist.
- Confirmed selected groups preserve group order, group key/label, draft/source group lineage, and group-level sample quantity expression.
- Confirmation fails if any selected group lacks a nonblank sample quantity expression unless the implementation plan explicitly documents a different validation rule and the user approves it.
- Confirmed rows preserve row order, draft/source row lineage, `test_item`, `source_section`, `method`, `condition`, and `requirement`.
- Confirmed cells use sparse non-empty storage and include only cells that belong to selected confirmed groups.
- Confirmed authority creation is atomic across root, groups, rows, and cells. Any failure rolls back the entire confirmation.
- Confirmed Matrix records are immutable after creation in this task; repository/service must not expose update methods for confirmed rows/groups/cells.
- API routes, if added, call the application service only.
- Source Matrix and Project Matrix Draft row/group/cell content remain unchanged by confirmation.
- Tests cover happy path, no selected groups, missing sample quantity, existing active authority conflict, sparse selected-cell copy, lineage preservation, source/draft immutability, API route boundary, and atomic rollback on failure.

## Validation

```powershell
py -m pytest tests\unit\test_confirmed_matrix_authority_service.py tests\unit\test_confirmed_matrix_authority_repository.py -q
```

```powershell
py -m pytest tests\integration\test_confirmed_matrix_authority_api.py tests\integration\test_project_matrix_draft_save_api.py -q
```

```powershell
py -m pytest tests\integration\test_api_default_dependencies.py -q
```

## Residual Risk Record

- This task intentionally supports only first active authority creation. Revision/supersession is deferred to `TASK_258_MATRIX_REVISION_FLOW`.
- Confirmed Step Output is deferred because the current draft persistence authority source is rows/groups/cells; generating execution/report step outputs would cross into runtime/report semantics.
- Frontend publish/confirm wiring is deferred to a later UI task so this task can harden the backend authority boundary first.
