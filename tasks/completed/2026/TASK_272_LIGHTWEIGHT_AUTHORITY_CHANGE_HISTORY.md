# TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY

## Status

Complete.

## Current Execution Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current product direction: `Matrix-driven Laboratory Execution Phase`
- Current task status: `TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY`
- Allowed reason: `TASK_271_TEST_RECORD_WORD_GENERATION_V1` is complete, `docs/task_board.md` has no active implementation task, and this task is the next guideline-aligned slice from `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`.

## Source Guideline

Reference: `docs/post_phase11_matrix_driven_laboratory_execution_workflow_guideline.md`

Guideline intent:

```text
Record matrix authority changes after project execution starts.
```

This task adds a lightweight read-only history of ConfirmedMatrix authority revisions so the operator can see when the active Matrix changed and whether a derived Test Record draft may need regeneration.

## Objective

Expose a minimal authority change history derived from existing immutable ConfirmedMatrix versions and snapshots.

The implementation must remain a lightweight visibility slice. It must not introduce permission control, approval workflow, StepInstance persistence, execution records, report engine, regeneration ledger, or a separate Matrix history subsystem.

## Baseline

Current completed baseline:

- TASK_257 created immutable ConfirmedMatrix authority snapshots.
- TASK_258 added Matrix revision draft creation and confirmation with atomic supersession.
- TASK_263 exposes active ConfirmedMatrix Test Record preview.
- TASK_269 and TASK_270 render the Project Workbench read-only Matrix projection and step workspace.
- TASK_271 generates a Word Test Record draft from active ConfirmedMatrix only.
- `confirmed_matrix_versions` already stores revision number, active/superseded status, confirmation actor/time, and supersession metadata.

## Scope

In scope:

- Add a backend read-only service that lists project ConfirmedMatrix authority versions in revision order.
- Derive lightweight change summaries by comparing adjacent confirmed snapshots:
  - source snapshot changed
  - selected group changes
  - step/test row changes
  - token/cell changes at summary-count level
  - confirm/revision event metadata
- Add a `record_regeneration_recommended` flag with explicit semantics:
  - `is_active_authority == false` -> `true`
  - `is_active_authority == true` and source/group/step/token content differs from the previous revision -> `true`
  - otherwise -> `false`
- Add a typed read-only API endpoint for the authority history.
- Add a minimal Project Workbench history view near the confirmed Matrix projection.
- Add unit, integration, frontend, and static guard tests.
- Update task and board status after implementation.

Out of scope:

- Permission model.
- Approval workflow.
- Multi-user review.
- StepInstance or execution persistence.
- LLCR runtime persistence.
- Formal TestRecord aggregate.
- Evidence upload or image management.
- Report engine.
- Fee engine.
- AI review or recommendation.
- Equipment assignment.
- Test Record generation history or managed artifact ledger.
- Mutating Matrix authority from Project Workbench.
- Rebuilding existing Matrix revision confirmation behavior.
- Full diff viewer or Excel-like comparison table.
- Multi-Matrix append/merge history.

## Expected File Changes

Create:

- `backend/application/confirmed_matrix_authority_history_service.py`
- `backend/api/routes_confirmed_matrix_authority_history.py`
- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.tsx`
- `frontend/src/features/project-workbench/AuthorityChangeHistoryPanel.test.tsx`
- `tests/unit/test_confirmed_matrix_authority_history_service.py`
- `tests/integration/test_confirmed_matrix_authority_history_api.py`

Modify:

- `backend/infrastructure/storage/repositories/confirmed_matrix_authority.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`
- `docs/task_board.md`
- `docs/task_plan_index.md`
- `tasks/TASK_272_LIGHTWEIGHT_AUTHORITY_CHANGE_HISTORY.md`

No database migration is expected because history can be derived from existing immutable ConfirmedMatrix version and snapshot tables.

## API Contract

Add a new endpoint:

```text
GET /api/projects/{project_id}/confirmed-matrix/authority-history
```

Response shape:

```json
{
  "project_id": "project-id",
  "entries": [
    {
      "confirmed_matrix_id": "cmv-...",
      "confirmed_revision": 2,
      "is_active_authority": true,
      "status": "confirmed",
      "confirmed_by": "operator",
      "confirmed_at": "2026-05-26T00:00:00+00:00",
      "superseded_at": null,
      "superseded_reason": null,
      "source_snapshot_changed": false,
      "group_change_count": 1,
      "step_change_count": 2,
      "token_change_count": 3,
      "record_regeneration_recommended": true,
      "change_summary": "Revision 2 changed 1 group, 2 steps, and 3 matrix tokens."
    }
  ]
}
```

Behavior:

- Returns `200` with `entries: []` when the project has no confirmed Matrix history.
- Returns entries ordered by `confirmed_revision` descending for operator readability.
- Repository history reads are ordered by `confirmed_revision.asc()` for deterministic adjacent comparison; the service must reverse to descending before API output.
- Uses only ConfirmedMatrix authority snapshots as source.
- Does not create, mutate, or approve anything.
- Does not compare against generated Word files because TASK_271 intentionally has no generation history.

## UI / UX Requirements

- ConnLab register: `product`.
- Physical scene: a lab coordinator on a daytime Windows workstation checks whether the current authority changed after a draft Test Record may have been generated.
- The view must be read-only and compact.
- The view must use operational copy such as:
  - `Authority Change History`
  - `Current authority`
  - `Record draft may need regeneration`
  - `No confirmed authority history yet`
- The view must not render mutation controls or `<button>` elements.
- The view must not expose approval, permission, report, fee, AI, equipment, or execution-data actions.
- API calls must stay in `frontend/src/api/client.ts`.

## Data Contract

The history service must consume existing domain snapshots:

```py
ConfirmedMatrixSnapshot
ConfirmedMatrixVersion
ConfirmedMatrixGroup
ConfirmedMatrixRow
ConfirmedMatrixCell
```

The repository should add a read-only project listing method if needed:

```py
def list_by_project(self, project_id: str) -> tuple[ConfirmedMatrixSnapshot, ...]:
    ...
```

No ORM model should be returned directly from API routes.

## Acceptance Criteria

- User can see ConfirmedMatrix authority history for a project.
- User can see when the active Matrix changed.
- User can understand whether a Test Record draft may need regeneration.
- History is derived from immutable ConfirmedMatrix snapshots and revision metadata.
- First confirmation is shown as an initial authority event.
- Subsequent revisions show lightweight group/step/token change counts.
- No permission, approval, StepInstance, execution persistence, report, fee, AI, equipment, or generation-history scope is introduced.
- Existing TASK_257 to TASK_271 behavior remains intact.
- Relevant unit, integration, frontend, and static guard tests pass.

## Validation Plan

Required commands after implementation:

```powershell
py -m pytest tests\unit\test_confirmed_matrix_authority_history_service.py -q
py -m pytest tests\unit\test_confirmed_matrix_authority_repository.py -q
py -m pytest tests\integration\test_confirmed_matrix_authority_history_api.py -q
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
```

```powershell
cd frontend
npm test -- --run AuthorityChangeHistoryPanel
npm test -- --run ProjectWorkbenchMatrixProjectionPanel
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task272 or task271 or project_workbench"
git diff --check
```

## Risks

- There is no execution-start state yet. TASK_272 must phrase the feature as ConfirmedMatrix authority history, not as a real execution lifecycle audit trail.
- There is no TASK_271 generation ledger. `record_regeneration_recommended` can only indicate that superseded authority or active authority changes mean a previously exported draft may be stale; UI copy must say "may need regeneration" and must not claim to know whether a draft exists.
- Snapshot comparison should stay lightweight and deterministic. Avoid building a full diff engine or exposing row-by-row mutable history UI.
- Existing Project Workbench is already dense. The history view should remain compact and read-only so it does not compete with the Matrix projection.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task.

Reason:

- The task is a bounded read-only backend/API/frontend integration slice using existing ConfirmedMatrix authority snapshots.
- It requires careful scope control and deterministic comparison logic, but does not require database migration, Office automation, multi-user workflow design, or a broad runtime engine.
- Medium reasoning is sufficient if the implementation follows the existing repository, application service, API route, and Project Workbench patterns.

Recommended mode:

- `GPT-5.3-codex` with medium reasoning.
- Use `superpowers:executing-plans` for implementation after user approval.

## Implementation Summary

- Added lightweight read-only ConfirmedMatrix authority history service derived from immutable snapshots.
- Added repository `list_by_project(project_id)` ordered by `confirmed_revision.asc()` and converted to descending order in service/API output.
- Added read-only API endpoint `GET /api/projects/{project_id}/confirmed-matrix/authority-history`.
- Added Project Workbench `Authority Change History` panel with compact loading/empty/error/ready states and `may need regeneration` advisory copy.
- Added unit, integration, frontend, and static guard tests for TASK_272 boundaries.

## Validation Results

- `py -m pytest tests\unit\test_confirmed_matrix_authority_history_service.py -q` -> `3 passed`
- `py -m pytest tests\unit\test_confirmed_matrix_authority_repository.py -q` -> `6 passed`
- `py -m pytest tests\integration\test_confirmed_matrix_authority_history_api.py -q` -> `2 passed`
- `py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q` -> `1 passed`
- `cd frontend; npm test -- --run AuthorityChangeHistoryPanel` -> `3 passed`
- `cd frontend; npm test -- --run ProjectWorkbenchMatrixProjectionPanel` -> `5 passed`
- `cd frontend; npm run build` -> `passed`
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task272 or task271 or project_workbench"` -> `4 passed`
- `git diff --check` -> passed (CRLF working-copy warnings only)
