# TASK_258 Matrix Revision Flow Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_258_MATRIX_REVISION_FLOW`
- Why this task is allowed now:
  - `TASK_253` defined the revision flow after confirmed authority.
  - `TASK_257` completed first active Confirmed Matrix authority creation and deliberately deferred supersession.
  - The board recommends `TASK_258_MATRIX_REVISION_FLOW` as the next controlled backend boundary.

This document is a plan only. No implementation should start until user approval.

## 1) Task Goal

Add backend Matrix revision flow.

The flow has two controlled operations:

1. Create a new editable Project Matrix Draft from the current active Confirmed Matrix.
2. Confirm that revision draft into the next active Confirmed Matrix while atomically superseding the previous active authority.

This task does not add frontend UI wiring, runtime projection refresh, StepInstance persistence, reports, fee, duration, equipment, Office parsing, or confirmed step output generation.

## 2) Inputs And Outputs

Input for revision draft creation:

- `project_id`
- current active `ConfirmedMatrixVersion`
- operator/reason metadata if needed for traceability

Output:

- new `ProjectMatrixDraft` derived from active confirmed authority
- draft lineage back to `base_confirmed_matrix_id`

Input for revision confirmation:

- `project_id`
- revision draft id
- `confirmed_by`
- optional supersession reason

Output:

- new active `ConfirmedMatrixVersion`
- previous active authority marked superseded
- previous active `is_active_authority = false`
- new confirmed revision number

## 3) Proposed Data Boundary

Project Matrix Draft remains the editable workspace.

- Revision draft content starts as a copy of the active confirmed authority.
- Existing draft save API remains responsible for later edits.
- Revision draft must know which confirmed authority it was based on.

Confirmed Matrix remains immutable authority history.

- Confirmed rows/groups/cells are not edited.
- Superseding changes only root/version metadata:
  - status
  - active flag
  - superseded metadata
- New confirmed authority gets new row/group/cell snapshots.

Source Matrix remains immutable traceability.

Runtime/report/fee consumers remain out of scope.

## 4) File-Level Change Plan

1. Domain
   - Extend confirmed authority domain root with supersession metadata if missing:
     - `superseded_by`
     - `superseded_at`
     - `superseded_reason`
   - Add `SUPERSEDED` to `ConfirmedMatrixStatus`.
   - Extend Project Matrix Draft root/domain metadata if required for `base_confirmed_matrix_id`.

2. Storage
   - Update `backend/infrastructure/storage/models_confirmed_matrix_authority.py` for supersession metadata.
   - Update `backend/infrastructure/storage/models_project_matrix_draft.py` only if revision lineage metadata is added.
   - Add SQLite migration helpers only if existing tables need new nullable columns.
   - Preserve DB-level active authority uniqueness.

3. Repository
   - Extend `ConfirmedMatrixAuthorityRepository` with a transaction-scoped operation to:
     - create a new confirmed snapshot
     - supersede the previous active version
     - flush as one atomic unit
   - Add read helpers for latest revision number by project if needed.
   - Avoid update methods for confirmed row/group/cell content.
   - Extend `ProjectMatrixDraftRepository` only as needed to create/load revision drafts with base authority lineage.

4. Application Service
   - Add `backend/application/matrix_revision_flow_service.py`.
   - Operation A: create revision draft from active confirmed authority.
   - Operation B: confirm revision draft.
   - Reuse TASK_257 validation rules for selected groups and sample quantity.
   - Ensure new revision number is `previous_active.confirmed_revision + 1`.
   - Ensure previous active is superseded in the same transaction as new authority creation.

5. API
   - Add minimal backend routes only if approved in implementation:
     - `POST /api/projects/{project_id}/matrix-revisions`
       - creates a revision draft from active confirmed authority
     - `POST /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}/confirm-revision`
       - confirms revision draft and supersedes prior active authority
   - Routes must call application services only.
   - No frontend client wiring in this task.

6. Tests
   - Unit tests for revision draft mapping.
   - Unit tests for revision confirmation and supersession.
   - Repository rollback test for failure after superseding previous active but before commit.
   - Integration tests for API happy path and error mapping.

## 5) Revision Draft Mapping Rules

When creating a revision draft from active confirmed authority:

- Copy confirmed groups into draft groups.
- Mark confirmed groups as selected in the new draft.
- Preserve group order, key, label, sample quantity expression, sample note, draft/source lineage where available.
- Copy confirmed non-sample rows into draft rows.
- Preserve row order, test item, source section, method, condition, requirement, draft/source lineage where available.
- Copy confirmed sparse cells into draft cells.
- Keep sample quantity only as group-level draft data.
- Do not recreate sample rows as editable sample authority rows unless an existing repository invariant requires a sample row placeholder; if required, document it explicitly in implementation.

## 6) Revision Confirmation Rules

When confirming a revision draft:

- Require an active confirmed authority for the project.
- Require the revision draft to belong to the same project.
- Require the revision draft lineage to reference the active confirmed authority.
- Reject stale revision drafts based on a superseded/non-active confirmed authority.
- Validate selected groups:
  - at least one selected group
  - nonblank `group_key`
  - nonblank `group_label`
  - nonblank `sample_quantity_expression`
- Copy all non-sample draft rows.
- Copy sparse cells only for selected groups and confirmed non-sample rows.
- Set new `confirmed_revision = active.confirmed_revision + 1`.
- Set new status active/confirmed and `is_active_authority = true`.
- Set previous status superseded and `is_active_authority = false`.
- Store supersession metadata on previous active root.

## 7) API And Error Semantics

Expected errors:

- `404`: project, active authority, or draft not found.
- `409`: stale revision draft, active authority conflict, or DB uniqueness conflict.
- `422`: draft is not confirmable, including no selected groups, blank selected group key/label, or missing sample quantity.
- `500`: unexpected failure.

## 8) Risks And Controls

Risk: Supersession happens before new authority is safely created.

- Control: previous supersede + new authority creation must be one transaction. Rollback test must prove previous remains active on failure.

Risk: Revision flow edits confirmed content.

- Control: confirmed row/group/cell content remains immutable. Only root/version metadata changes for supersession.

Risk: Stale revision draft supersedes the wrong active authority.

- Control: revision confirmation validates draft `base_confirmed_matrix_id` against current active authority.

Risk: Revision number races.

- Control: DB-level active uniqueness remains; revision confirmation happens under one session/transaction. Race-specific LAN locking is out of scope.

Risk: This becomes runtime/report work.

- Control: no StepInstance, runtime projection, report, fee, duration, equipment, or Confirmed Step Output generation.

## 9) Validation Plan

Backend unit/repository:

```powershell
py -m pytest tests\unit\test_matrix_revision_flow_service.py tests\unit\test_confirmed_matrix_authority_repository.py tests\unit\test_project_matrix_draft_repository.py -q
```

Backend integration:

```powershell
py -m pytest tests\integration\test_matrix_revision_flow_api.py tests\integration\test_confirmed_matrix_authority_api.py -q
```

Dependency smoke:

```powershell
py -m pytest tests\integration\test_api_default_dependencies.py -q
```

## 10) Out Of Scope

- Frontend revision UI.
- Matrix Editor button/client wiring.
- Runtime projection refresh.
- StepInstance or execution persistence.
- Evidence/image asset management.
- Report, fee, duration, or equipment generation.
- Confirmed Step Output generation.
- Office parsing or preview changes.
- Creating revisions from non-active historical confirmed versions.

## 11) Review Checklist For This Plan

- Starts only from current active confirmed authority.
- New revision draft is editable through existing draft save behavior.
- Revision confirm atomically creates new active authority and supersedes previous active.
- Previous confirmed rows/groups/cells remain immutable.
- New confirmed revision number is deterministic.
- Stale revision drafts cannot supersede current active authority.
- No frontend/runtime/report scope is introduced.
