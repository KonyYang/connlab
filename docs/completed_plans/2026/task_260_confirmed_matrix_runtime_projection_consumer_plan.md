# TASK_260 Confirmed Matrix Runtime Projection Consumer Plan

## 0) Anti-Skip Protocol

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task for this plan: `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER`
- Why this task is allowed now:
  - `TASK_259` is complete.
  - `docs/task_board.md` recommends opening `TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER`.
  - Confirmed Matrix authority exists and needs a backend runtime projection consumer path.

This document is a plan only. No implementation should start until user approval.

## 1) Goal

Add a backend read-only consumer that builds existing runtime projection snapshots from the active Confirmed Matrix authority for a project.

The task does not create runtime execution state. It only adapts confirmed authority data into the existing projection adapter.

## 2) File-Level Change Plan

1. Application service
   - Add `backend/application/confirmed_matrix_runtime_projection_service.py`.
   - Define a small command/input with:
     - `project_id`
     - `selected_token_reference`
   - Depend on a confirmed Matrix store protocol with `get_active_by_project(project_id)`.
   - Convert confirmed Matrix aggregate into existing `SnapshotBuildInput`.
   - Call existing runtime projection read-only service or projection builder.

2. API route
   - Add `backend/api/routes_confirmed_matrix_runtime_projection.py`.
   - Add `GET /api/projects/{project_id}/runtime-projection/confirmed-matrix-snapshot`.
   - Accept optional `selected_token_reference` query parameter.
   - Reuse existing runtime projection response mapping if practical; otherwise extract shared response helpers without changing response schema.
   - Do not import private mapping helpers directly from another route module; route-to-route coupling is not allowed.
   - If mapping reuse is needed, extract mapper/helpers into a neutral module and use it from both routes.
   - Map:
     - no active confirmed Matrix -> 404
     - invalid confirmed Matrix projection input -> 422
     - unexpected -> 500
   - Error shape policy:
     - Keep FastAPI default `HTTPException(detail=...)` error body for 404/422 in this task.
     - Do not introduce new error DTO models.

3. Dependency wiring
   - Add a provider in `backend/api/dependencies.py`.
   - Register the route in `backend/api/main.py`.
   - Route must call application service only.

4. Tests
   - Add unit tests for conversion from confirmed Matrix to projection snapshot.
   - Add integration tests for the new endpoint.
   - Add dependency smoke coverage if needed.
   - Preserve existing runtime projection read-only API tests.

5. Documentation
   - Mark task complete in `tasks/TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER.md`.
   - Update `docs/task_board.md` with deliverables, validation, and next recommendation.

## 3) Mapping Rules

- `project_reference`: project id.
- `matrix_reference`: active confirmed Matrix id plus confirmed revision, for example `<confirmed_matrix_id>:r<confirmed_revision>`.
- `group_identity`: confirmed group key.
- `group_label`: confirmed group label.
- row context:
  - `test_item_label`: confirmed row `test_item`
  - `section`: confirmed row `source_section` or empty string
  - `method`: confirmed row `method` or empty string
  - `condition`: confirmed row `condition` or empty string
  - `requirement`: confirmed row `requirement` or empty string
- `raw_step_token_value`: confirmed sparse cell value for the row/group pair.

Rows without a cell in a confirmed group should be omitted from runtime projection input. This task must not generate synthetic empty row/group inputs only to produce missing-token warnings. This keeps projection output token-driven and aligned to confirmed sparse authority cells.

## 4) Scope Guards

- Do not create or persist StepInstance.
- Do not persist runtime projection snapshots.
- Do not add execution status, evidence status, report sync status, or operator assignment.
- Do not add frontend consumption in this task.
- Do not add new projection DTOs unless current DTO insufficiency is documented first.
- Do not modify Confirmed Matrix authority creation or revision behavior.
- Do not reintroduce unselected Source Matrix groups.

## 5) Acceptance Tests

- Service returns a projection snapshot for an active confirmed Matrix with two groups and sparse cells.
- Snapshot omits source/unselected groups because only confirmed groups are loaded.
- `matrix_reference` uses confirmed Matrix id/revision.
- Selected token reference is passed through to Step Workspace.
- Missing active confirmed Matrix raises not-found and API returns 404.
- Existing `/api/runtime-projection/read-only-snapshot` tests still pass.

## 6) Validation Plan

```powershell
py -m pytest tests\unit\test_confirmed_matrix_runtime_projection_service.py -q
```

```powershell
py -m pytest tests\integration\test_confirmed_matrix_runtime_projection_api.py tests\integration\test_runtime_projection_read_only_api.py -q
```

```powershell
py -m pytest tests\integration\test_api_default_dependencies.py -q
```

## 7) Review Checklist

- API route calls application service only.
- Existing runtime projection response contract is reused.
- Confirmed Matrix remains source authority; Runtime Projection remains derived output.
- No schema migration is introduced.
- No frontend/UI scope is introduced.
- No StepInstance or execution persistence is introduced.
