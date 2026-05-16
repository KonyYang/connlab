# API Surface Snapshot

Last Updated: 2026-05-16
Status: current route-group snapshot, not a full generated OpenAPI replacement

This document replaces the old MVP-only API contract summary. It records the current API surface at route-group level so future tasks do not rely on stale MVP examples.

FastAPI's generated OpenAPI output remains the detailed endpoint/schema source at runtime. Route bodies should stay thin and delegate to application services.

## API Rules

- Routes must return typed responses.
- Route bodies should call application services or focused module services.
- Do not leak SQLAlchemy models directly.
- Do not call Office COM from API routes.
- UI/frontend must call API routes rather than manipulating Office files, SQLite, or project folders directly.

## Health

- `GET /health`

## Project Registry

Module:

- `backend/api/routes_project.py`

Surface:

- `POST /api/projects`
- `GET /api/projects`
- `GET /api/projects/{project_id}`

## Intake And Application Material

Modules:

- `backend/api/routes_intake.py`
- `backend/api/routes_intake_review.py`
- `backend/api/routes_new_project_completion.py`

Surface includes:

- intake package/source import
- direct application form import
- application asset download
- selected-form and draft lifecycle operations
- intake review read/update/confirm flows
- New Project completion orchestration

This area is broader than the original MVP `POST /api/intake/application-form` contract.

## LTR And Workbook Authority

Modules:

- `backend/api/routes_ltr.py`
- `backend/api/routes_ltr_workbook.py`
- `backend/api/routes_ltr_workbook_compatibility.py`

Surface includes:

- Project LTR registration/readiness
- LTR record listing
- workbook write preview/commit
- workbook compatibility baseline
- LTR exception/frozen-field flows

LTR workbook operations must remain behind backend infrastructure/application boundaries.

## Folder And Evidence

Modules:

- `backend/api/routes_folder.py`
- `backend/api/routes_evidence.py`

Surface:

- latest project folder record
- folder preview
- folder generation
- evidence placement preview/execution

Folder operations remain preview-before-write and conflict-aware.

## External Resources And Lookups

Modules:

- `backend/api/routes_external_resources.py`
- `backend/api/routes_external_excel_resources.py`
- `backend/api/routes_lookup.py`
- `backend/api/routes_lookup_options.py`

Surface includes:

- configured external resources
- resource validation
- read-only external Excel resource views
- project lookup
- lookup option listing/import/update

## Project Test Plan / Matrix

Modules:

- `backend/api/routes_project_test_plan.py`
- `backend/api/routes_project_test_plan_drafts.py`
- `backend/api/routes_project_test_plan_matrix_edit.py`
- `backend/api/routes_project_test_plan_source_candidates.py`

Surface includes:

- Matrix preview from source path
- Project-scoped test-plan draft create/list/read/update
- source candidate listing
- source candidate Matrix preview
- Matrix draft update/validate/confirm

Matrix authority remains separate from UI projection and Project lifecycle.

## Section 2, Test Record, Fee, And Approval Package

Modules:

- `backend/api/routes_section2_completion_preview.py`
- `backend/api/routes_section2_write_back.py`
- `backend/api/routes_test_record_fee_dataset_preview.py`
- `backend/api/routes_test_record_fee_document_generation.py`
- `backend/api/routes_approval_package.py`

Surface includes:

- Section 2 completion preview
- Section 2 write-back
- test record / fee dataset preview
- test record / fee document generation
- approval package preview/execute

These are derived-output workflows. They do not own Matrix authority or Step identity.

## Project Output Records

Module:

- `backend/api/routes_project_output_records.py`

Surface:

- `POST /api/projects/{project_id}/output-records`
- `GET /api/projects/{project_id}/output-records`
- `GET /api/projects/{project_id}/output-records/status`

Output records track derived output freshness/status and do not mutate Matrix authority.

## Cleanup And Audit

Module:

- `backend/api/routes_cleanup.py`

Surface includes:

- dry-run cleanup audits
- explicit cleanup execution endpoints

Cleanup endpoints must remain explicit and must not physically delete project data unless a future approved task changes that policy.

## Runtime Projection

Modules:

- `backend/modules/runtime_projection/*`
- `backend/api/routes_runtime_projection_read_only.py`

Surface:

- `POST /api/runtime-projection/read-only-snapshot`

This route is read-only and adapter-focused:

- builds deterministic runtime projection snapshot output using existing projection builders/composition/consumer views
- does not introduce runtime engine or persistence
- does not mutate Matrix authority or Project lifecycle

Future runtime projection APIs must obey:

- Projection != Domain Identity
- Runtime Projection is not source of truth
- Projection composition must remain independently evolvable
- consumer-first slices before runtime engines or persistence

## Historical MVP Examples

The original MVP examples for manual project creation, intake parsing, precheck, LTR, and folder generation remain useful as historical context, but they are no longer complete API documentation.
