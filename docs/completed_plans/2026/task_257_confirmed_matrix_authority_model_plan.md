# TASK_257 Confirmed Matrix Authority Model Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_257_CONFIRMED_MATRIX_AUTHORITY_MODEL`
- Why this task is allowed now:
  - `TASK_253` defined the Confirmed Matrix authority boundary.
  - `TASK_254` persisted Source Matrix lineage.
  - `TASK_255` persisted Project Matrix Draft working copies.
  - `TASK_256` wired Matrix Editor Save to draft persistence.
  - The next controlled backend boundary is first confirmed Matrix authority creation.

This document is a plan only. No implementation should start until user approval.

## 1) Task Goal

Create the first backend authority layer for Matrix confirmation.

The task converts one saved Project Matrix Draft into an immutable active Confirmed Matrix snapshot for the project. It does not implement revision flow, frontend confirm wiring, runtime execution, StepInstance, report generation, fee, duration, or equipment outputs.

## 2) Inputs And Outputs

Input:

- Existing persisted `ProjectMatrixDraftSnapshot`
- Existing Project identity
- Operator metadata for confirmation, at minimum `confirmed_by`

Output:

- Persisted active `ConfirmedMatrixVersion`
- Persisted confirmed selected groups
- Persisted confirmed non-sample rows
- Persisted sparse confirmed cells for selected groups
- Stable lineage back to draft/source import/source snapshot/source rows/source groups

## 3) Proposed Data Boundary

Confirmed Matrix owns immutable authority state:

- project authority identity
- source/draft lineage
- active authority flag and status
- confirmed selected groups
- group-level sample quantity expression
- all non-sample confirmed rows, including rows with no selected-group token/cell value
- sparse selected group cells

Project Matrix Draft remains editable working-copy state:

- draft rows/groups/cells
- draft selected groups
- draft sample quantity expressions

Source Matrix remains immutable import traceability:

- original imported full matrix
- parser/source metadata
- full unselected group traceability

Revision flow is not part of this task.

Confirmed row copy rule:

- Copy all non-sample draft rows.
- Do not copy draft sample rows as confirmed rows.
- Sample quantity remains group-level authority data on confirmed groups.
- Rows with no cell/token value in selected groups are still copied so row order and traceability remain stable for later revision/diff consumers.

## 4) File-Level Change Plan

1. Domain
   - Add `backend/domain/confirmed_matrix_authority_models.py`.
   - Add `ConfirmedMatrixStatus` or equivalent enum in `backend/domain/enums.py`.
   - Export confirmed authority classes through `backend/domain/__init__.py`.

2. Storage
   - Add `backend/infrastructure/storage/models_confirmed_matrix_authority.py`.
   - Register the module in `backend/infrastructure/storage/database.py::init_db`.
   - Keep confirmed authority tables separate from `storage/models.py`.
   - Add DB-level uniqueness guard for one active authority per project.
   - For SQLite, prefer a partial unique index on active authority rows if supported by the existing SQLAlchemy/SQLite path; otherwise document and test the equivalent guard strategy.

3. Repository
   - Add `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`.
   - Implement create and load operations for:
     - root version
     - confirmed groups
     - confirmed rows
     - confirmed sparse cells
   - Implement active-authority lookup by project.
   - Do not expose mutable update operations for confirmed rows/groups/cells.

4. Application Service
   - Add `backend/application/confirmed_matrix_authority_service.py`.
   - Load project and draft through existing repositories.
   - Validate draft can be confirmed:
     - draft exists and belongs to project
     - no active confirmed Matrix exists for project
     - at least one selected draft group
     - selected draft groups have nonblank `group_key` and `group_label`
     - selected groups have nonblank sample quantity expressions
   - Map draft rows/groups/cells to confirmed rows/groups/cells.
   - Copy all non-sample draft rows and exclude sample rows.
   - Set `confirmed_revision = 1` for this first-slice task.
   - Reject if an active confirmed Matrix already exists; do not auto-increment revision.
   - Do not mutate draft content or draft status.
   - Copy only cells whose group is selected.
   - Preserve lineage IDs and draft IDs.
   - Commit root/groups/rows/cells atomically in one transaction.

5. API
   - Add minimal route only if approved in implementation:
     - `POST /api/projects/{project_id}/matrix-drafts/{project_matrix_draft_id}/confirm`
   - Route body should carry `confirmed_by` and optional operator note.
   - Route must call application service only.
   - Return typed Pydantic response.

6. Tests
   - Unit tests for mapping, selected group filtering, sample quantity validation, and conflict when active authority exists.
   - Repository tests for roundtrip, sparse selected-cell copy, and atomic rollback.
   - Integration test for API happy path and error mapping.
   - Regression tests proving Source Matrix and Project Matrix Draft content are unchanged.

## 5) Data Model Sketch

Confirmed Matrix root:

- `confirmed_matrix_id`
- `project_id`
- `project_matrix_draft_id`
- `source_import_id`
- `source_snapshot_id`
- `confirmed_revision`
- `is_active_authority`
- `status`
- `confirmed_by`
- `confirmed_at`
- `validation_summary_json`

Revision rule:

- `confirmed_revision` is always `1` in TASK_257.
- Existing active authority returns conflict.
- Revision increment/supersession is deferred to `TASK_258_MATRIX_REVISION_FLOW`.

Confirmed group:

- `confirmed_group_id`
- `confirmed_matrix_id`
- `draft_group_id`
- `source_group_snapshot_id`
- `group_order`
- `group_key`
- `group_label`
- `sample_quantity_expression`
- `sample_note`

Confirmed row:

- `confirmed_row_id`
- `confirmed_matrix_id`
- `draft_row_id`
- `source_row_snapshot_id`
- `row_order`
- `test_item`
- `source_section`
- `method`
- `condition`
- `requirement`

Confirmed cell:

- `confirmed_cell_id`
- `confirmed_matrix_id`
- `confirmed_row_id`
- `confirmed_group_id`
- `draft_row_id`
- `draft_group_id`
- `cell_value`

## 6) API And Error Semantics

Minimal confirm request:

```json
{
  "confirmed_by": "operator",
  "confirmation_note": "optional"
}
```

Expected error mapping:

- `404`: project or draft not found
- `409`: active confirmed Matrix already exists for project
- `422`: draft is not confirmable, including no selected groups or missing selected-group sample quantity
- `500`: unexpected failure

DB uniqueness fallback:

- Active authority uniqueness must be protected below the service layer.
- If the DB uniqueness guard catches a duplicate active authority, the application/API boundary maps it to `409`.

## 7) Risks And Controls

Risk: Confirmed authority becomes editable draft state.

- Control: confirmed repository exposes create/read only for authority rows in this task.

Risk: This task accidentally implements revision flow.

- Control: if active authority already exists, reject with conflict. Supersession belongs to `TASK_258`.

Risk: Unselected groups leak into execution authority.

- Control: confirmed groups and confirmed cells include selected draft groups only. Full traceability remains via draft/source lineage.

Risk: Confirmed rows become ambiguous because row copy scope is unclear.

- Control: copy all non-sample draft rows. Exclude sample rows because sample quantity is group-level authority data.

Risk: Sample quantity becomes ambiguous.

- Control: selected confirmed group must have nonblank group-level `sample_quantity_expression`; source sample rows remain trace-only.

Risk: Blank selected group identifiers enter authority.

- Control: reject confirmation when selected group `group_key` or `group_label` is blank.

Risk: Service-level active authority check races with another confirmation.

- Control: add DB-level active authority uniqueness guard and map resulting conflict to `409`.

Risk: Partial authority persists on failure.

- Control: repository writes root/groups/rows/cells in one transaction and tests rollback on deliberate uniqueness failure.

Risk: API route bypasses application service.

- Control: route constructs command DTO and calls only application service.

## 8) Validation Plan

Backend unit/repository:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_authority_service.py tests\unit\test_confirmed_matrix_authority_repository.py -q
```

Backend integration:

```powershell
py -m pytest tests\integration\test_confirmed_matrix_authority_api.py tests\integration\test_project_matrix_draft_save_api.py -q
```

Dependency smoke:

```powershell
py -m pytest tests\integration\test_api_default_dependencies.py -q
```

If API/client files are touched unexpectedly, also run:

```powershell
cd frontend
npm run build
```

## 9) Out Of Scope

- Frontend confirm/publish button wiring.
- Matrix revision and supersession flow.
- Creating a new draft from confirmed authority.
- Runtime projection refresh.
- StepInstance or execution persistence.
- Evidence/image asset management.
- Report, fee, duration, or equipment generation.
- Confirmed Step Output generation.
- Office parsing or preview changes.

## 10) Review Checklist For This Plan

- Scope is backend authority only.
- Confirmed Matrix is immutable after creation.
- Existing active authority blocks this first slice instead of superseding.
- `confirmed_revision` is fixed to `1` in this first slice.
- DB-level active authority uniqueness is required in addition to service validation.
- All non-sample draft rows are copied; draft sample rows are excluded.
- Selected groups become authority; unselected groups remain traceable through draft/source.
- Blank selected group key/label is rejected.
- Source Matrix and Project Matrix Draft content are not mutated.
- API routes, if added, remain application-service only.
- Tests cover both happy path and rollback/error cases.
