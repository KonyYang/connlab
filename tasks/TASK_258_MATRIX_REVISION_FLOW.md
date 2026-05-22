# TASK_258_MATRIX_REVISION_FLOW

## Status

Complete.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_258_MATRIX_REVISION_FLOW` is complete.

## Why This Task Is Allowed Now

- `TASK_253_MATRIX_PERSISTENCE_DOMAIN_MODEL_DESIGN` defined the revision flow after confirmed Matrix authority exists.
- `TASK_254_SOURCE_MATRIX_IMPORT_PERSISTENCE_MODEL` persisted immutable Source Matrix lineage.
- `TASK_255_PROJECT_MATRIX_DRAFT_PERSISTENCE_MODEL` persisted editable Project Matrix Draft working copies.
- `TASK_256_MATRIX_EDITOR_SAVE_TO_DRAFT_WIRING` wired Matrix Editor Save to draft persistence.
- `TASK_257_CONFIRMED_MATRIX_AUTHORITY_MODEL` implemented first active Confirmed Matrix authority creation and intentionally deferred supersession/revision flow.
- The next controlled boundary is creating a new editable draft from active authority and confirming it as the next revision while superseding the previous active authority.

## Model Fit Assessment

`GPT-5.3-codex` with `medium` reasoning is suitable.

Reason:

- The task is a bounded backend persistence/application-service slice building on existing draft and confirmed authority models.
- It requires deterministic copy/mapping logic, transaction boundaries, uniqueness handling, and focused tests.
- It does not require frontend design, Office parsing, runtime execution, report generation, multi-user collaboration, or AI/LLM behavior.

## Objective

Implement backend Matrix revision flow.

This task adds controlled ability to create a new editable `ProjectMatrixDraft` from the current active `ConfirmedMatrixVersion`, then confirm that draft as the next immutable active authority revision while atomically superseding the previous active authority.

## Scope

Allowed:

- Add application service operations for Matrix revision flow:
  - create revision draft from active confirmed authority
  - confirm revision draft into next confirmed authority revision
- Add repository support required to:
  - load active confirmed authority by project
  - mark a previous active confirmed authority as superseded in the same transaction as new authority creation
  - load confirmed authority by draft lineage if needed for validation
- Extend confirmed Matrix storage/domain minimally for supersession metadata if not already present:
  - `status`
  - `is_active_authority`
  - `superseded_by_confirmed_matrix_id`
  - `superseded_at`
  - `superseded_reason`
- Add required Project Matrix Draft revision lineage metadata:
  - `base_confirmed_matrix_id` is mandatory for revision drafts and must reference the active confirmed authority used to create the draft.
  - Revision drafts must be distinguishable from source-import drafts so they do not reuse the existing `project_id + source_import_id` uniqueness path.
  - If a uniqueness constraint is added for revision drafts, it must be based on revision lineage such as `project_id + base_confirmed_matrix_id` for active/open revision drafts, not `source_import_id`.
- Add minimal backend APIs if required by integration tests:
  - create revision draft from active confirmed Matrix
  - confirm revision draft
- Preserve DB-level single active authority guarantee.
- Keep `confirmed_revision` monotonic per project:
  - first revision remains `1`
  - next revision is `max(existing confirmed_revision) + 1`
- Supersede previous active authority and create the new active authority atomically.
- Copy the same authority data rules as TASK_257:
  - selected draft groups only
  - all non-sample draft rows
  - sparse non-empty selected-group cells only
  - group-level sample quantity required for selected groups
- Add focused unit/integration tests.
- Update `docs/task_board.md` after completion.

Forbidden:

- Frontend `Publish/Confirm` or revision UI wiring.
- Runtime projection refresh or Runtime Console consumption.
- StepInstance persistence, execution records, evidence/image management, test records, reports, fee, duration, or equipment outputs.
- Confirmed Step Output generation.
- Matrix import parser, preview API, Word/Office gateway, or file handling changes.
- Direct editing/updating of confirmed rows/groups/cells.
- Deleting or overwriting historical confirmed Matrix authority records.
- Multi-user/LAN locking beyond DB uniqueness and transaction safety.
- Creating revisions from arbitrary historical confirmed versions. This task starts from the current active authority only.

## Acceptance Criteria

- A project with one active confirmed Matrix can create a new editable Project Matrix Draft revision from that active authority.
- The revision draft preserves mandatory lineage to the base active confirmed Matrix through `base_confirmed_matrix_id`.
- The revision draft is editable through existing draft save behavior; this task must not change Matrix Editor save semantics.
- A revision draft can be confirmed into a new active confirmed Matrix.
- Confirming a revision:
  - computes `confirmed_revision = previous_active.confirmed_revision + 1`
  - creates a new immutable confirmed authority snapshot
  - marks the previous active confirmed Matrix as superseded
  - sets previous active `is_active_authority = false`
  - sets new confirmed Matrix `is_active_authority = true`
  - performs all of the above atomically in one transaction
- If any part of revision confirmation fails, no partial new authority is persisted and the previous active authority remains active.
- DB-level active authority uniqueness remains enforced.
- Revision draft creation does not collide with the existing source-import draft uniqueness rule; revision drafts use nullable/no `source_import_id` plus explicit revision lineage, or an equivalent schema-safe uniqueness strategy documented in implementation.
- Revision confirmation keeps TASK_257 authority validation rules:
  - at least one selected group
  - selected group `group_key` and `group_label` nonblank
  - selected group sample quantity nonblank
  - copy all non-sample draft rows
  - copy sparse selected-group cells only
- Source Matrix import/snapshot rows remain immutable.
- Existing confirmed rows/groups/cells remain immutable history.
- API routes, if added, call application services only.
- Tests cover happy path revision draft creation, revision draft uniqueness behavior, required `base_confirmed_matrix_id`, no generated sample row placeholder, revision confirmation/supersession, revision number increment, rollback on failure, active uniqueness, draft/source immutability, historical confirmed immutability, and API error mapping.

## Validation

```powershell
py -m pytest tests\unit\test_matrix_revision_flow_service.py tests\unit\test_confirmed_matrix_authority_repository.py tests\unit\test_project_matrix_draft_repository.py -q
```

```powershell
py -m pytest tests\integration\test_matrix_revision_flow_api.py tests\integration\test_confirmed_matrix_authority_api.py -q
```

```powershell
py -m pytest tests\integration\test_api_default_dependencies.py -q
```

## Residual Risk Record

- Frontend operators cannot initiate this flow until a later UI wiring task exposes it.
- Confirmed Step Output remains deferred; revision authority is rows/groups/cells only.
- Runtime projection and downstream reports remain unchanged until later consumer tasks.
