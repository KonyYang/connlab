# TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER

## Status

Planned. Awaiting user approval before implementation.

## Current Phase

`Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Current Active Task

`TASK_260_CONFIRMED_MATRIX_RUNTIME_PROJECTION_CONSUMER` is planned only.

## Why This Task Is Allowed Now

- `TASK_257` introduced immutable active Confirmed Matrix authority.
- `TASK_258` introduced revision flow and active confirmed supersession.
- `TASK_259` wired Matrix Editor revision actions and left the next controlled task as a confirmed-authority runtime consumer.
- Existing runtime projection infrastructure already accepts `SnapshotBuildInput`; the missing slice is a backend adapter that builds that input from active Confirmed Matrix authority instead of frontend draft-shaped request data.

## Objective

Expose a read-only backend consumer path that builds runtime projection snapshots from the active Confirmed Matrix authority for a project.

This task should make Confirmed Matrix the runtime projection input authority while preserving existing runtime projection DTOs and composition behavior.

## Scope

Allowed:

- Add an application service that:
  - loads the active Confirmed Matrix for a project
  - converts confirmed groups, rows, and sparse cells into existing `SnapshotBuildInput`
  - calls the existing `RuntimeProjectionReadOnlyService` or `build_runtime_projection_snapshot`
  - returns the existing read-only runtime projection snapshot shape
- Add a thin API route such as:
  - `GET /api/projects/{project_id}/runtime-projection/confirmed-matrix-snapshot`
  - optional query: `selected_token_reference`
- Reuse existing response DTOs from `routes_runtime_projection_read_only.py` where practical.
- Add dependency wiring through `backend/api/dependencies.py` and `backend/api/main.py`.
- Add focused unit and integration tests for:
  - active confirmed Matrix conversion into projection rows
  - selected-token passthrough
  - no active confirmed Matrix returns 404
  - unselected source groups are not reintroduced
  - route calls application service rather than repository directly
- Update `docs/task_board.md` after completion.

Forbidden:

- Creating StepInstance, execution records, lifecycle persistence, evidence/image records, report, fee, duration, equipment, AI review, LAN, permissions, or deployment work.
- Adding a new selected-groups authority model.
- Reintroducing unselected Source Matrix groups into runtime projection output.
- Treating runtime projection as source of truth.
- Changing Confirmed Matrix persistence semantics.
- Changing Matrix Editor UI or frontend Runtime Console consumption.
- Adding new projection DTOs unless the implementation plan proves existing DTOs are insufficient.
- Replacing or rewriting `backend/modules/runtime_projection`.
- Changing the existing `/api/runtime-projection/read-only-snapshot` request-body API contract.

## Design Boundary

Confirmed Matrix is the authority input.

Runtime Projection remains a read-only derived consumer.

The adapter should map only confirmed authority data:

- each confirmed group becomes runtime projection `group_identity` and `group_label`
- each confirmed non-sample row contributes row context
- each confirmed sparse cell contributes the raw step token value for its confirmed row/group pair
- missing cells become empty or omitted rows according to the existing projection builder behavior chosen in the plan

Unselected source groups must stay traceable through Source Matrix lineage only; they must not appear in runtime projection output.

## Acceptance Criteria

- A project with active Confirmed Matrix can request a runtime projection snapshot without sending Matrix rows in the request body.
- The snapshot `matrix_reference` is based on the active confirmed Matrix id/revision, not a draft id.
- The output contains only confirmed groups.
- Sparse non-empty confirmed cells produce the same step-token parsing behavior as the existing runtime projection adapter.
- A selected token reference is passed through and produces the existing Step Workspace response.
- No active confirmed Matrix returns a typed 404 response.
- Existing `/api/runtime-projection/read-only-snapshot` behavior remains unchanged.
- API route remains thin and calls application service only.
- No database schema migration is introduced.

## Validation

```powershell
py -m pytest tests\unit\test_confirmed_matrix_runtime_projection_service.py -q
```

```powershell
py -m pytest tests\integration\test_confirmed_matrix_runtime_projection_api.py tests\integration\test_runtime_projection_read_only_api.py -q
```

```powershell
py -m pytest tests\integration\test_api_default_dependencies.py -q
```

## Residual Risk Record

- This task does not wire the frontend Runtime Console to the new confirmed-authority endpoint.
- Runtime projection still has fake/static lifecycle/evidence/report-sync dimensions until later execution tasks provide real data.
- This task does not implement StepInstance or execution state.
