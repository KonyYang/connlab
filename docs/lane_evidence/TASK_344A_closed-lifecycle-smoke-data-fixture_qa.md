# TASK_344A QA Evidence

Status: complete - Integrator accepted with documented data gap
Task: TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE
Lane: closed-lifecycle-smoke-data-fixture
Role: QA / Smoke Owner
Date: 2026-06-28

## Summary

QA completed the approved closed-lifecycle smoke-data inspection without mutating product code, backend/API/schema, frontend source/tests, user data, public-drive files, Office files, LTR authority files, or `docs/task_board.md`.

Result: no safe existing closed completed/admin project data is present in the current local environment. The lane outcome is therefore a documented smoke-data gap, which is an accepted TASK_344A QA outcome under the approved plan.

QA gate: pass with documented data gap.

Recommended next role: Integrator packaging/readiness for TASK_344A evidence closeout. If the series requires repeatable closed completed/admin smoke data later, route a separate Developer fixture-planning lane before creating any fixture or local mutation flow.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md`

Relevant board state observed:

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- TASK_344B is complete/accepted.
- TASK_344A is the separate closed-row smoke-data planning residual.
- No backend/API/schema, Workbench lifecycle behavior, frontend implementation, or TASK_343A/B/C/TASK_344B changes are authorized for this QA pass.

## Environment

- Workspace: `D:\PythonProject\connlab`
- App URL: `http://localhost:5173/projects`
- Frontend server availability check: HTTP 200, response length 635 bytes.
- Browser smoke: temporary local headless Chrome via DevTools Protocol at 514 x 720 viewport.
- Screenshot artifact: `docs/lane_evidence/artifacts/TASK_344A_qa/01_projects_closed_view_empty_514.png`

## Read-Only Data Inspection

Command:

```powershell
Invoke-RestMethod -Uri 'http://localhost:5173/api/projects/registry' -Method Get
```

Observed registry result:

- Total registry rows: 44
- `cancelled`: 25
- `draft`: 6
- `ltr_registered`: 13
- Registry rows matching closed/archive/completed/admin terms: none

Command:

```powershell
$registry = @(Invoke-RestMethod -Uri 'http://localhost:5173/api/projects/registry' -Method Get | ForEach-Object { $_ })
foreach ($row in $registry) {
  Invoke-RestMethod -Uri "http://localhost:5173/api/projects/$($row.project_id)/lifecycle" -Method Get
}
```

Observed lifecycle overlay result:

- Expanded registry rows swept: 44
- Lifecycle overlays swept: 44
- `active`: 19
- `stopped`: 25
- `closed`: 0
- Closed lifecycle rows: `NO_CLOSED_LIFECYCLE_ROWS`

Representative active rows exposed allowed actions `stop,close`; stopped rows exist, but no row had `lifecycle_state = closed` or a completed/admin closure type.

## Browser Smoke

Procedure:

1. Started a temporary local Chrome instance with DevTools Protocol.
2. Opened `http://localhost:5173/projects`.
3. Set viewport to 514 x 720.
4. Changed the `Project view` selector to `Closed` through the DOM select change event.
5. Captured screenshot.
6. Inspected visible body text and action text.

Observed browser result:

- Project view selector value: `closed`
- Visible message: `No projects in this view`
- Row count in Closed view: 0
- `Open archive` count: 0
- `Open Workbench` count: 0
- `Stop` count: 0
- `Resume` count: 0
- `Close` count: 0

Screenshot artifact:

- `docs/lane_evidence/artifacts/TASK_344A_qa/01_projects_closed_view_empty_514.png`

## Safety And Disposability Decision

No existing local closed completed/admin project IDs were found.

QA did not create closed data because there is no approved TASK_344A fixture implementation, no confirmed disposable closed project source, and creating closed rows through UI/API would mutate the current local project data. Under the approved plan, that risk should be handled only by a separate planning-first fixture lane that proves local-only, disposable setup and cleanup.

No cleanup was required because QA did not create or mutate project data.

## Scope Verification

QA did not touch:

- `backend/**`
- `frontend/**` product source or tests
- API/schema/frontend API client
- Workbench lifecycle implementation
- TASK_343A/B/C or TASK_344B accepted implementation files
- production/user data
- public-drive files, Office documents, or LTR authority files
- `docs/task_board.md`
- merge/commit/push/destructive git operations

Known unrelated dirty files observed before evidence write:

- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

Those files were not read as implementation targets, edited, staged, reverted, or included in TASK_344A QA scope.

Final scope status also showed the TASK_344A task, plan, and Planner evidence files as untracked working-tree files from the upstream planning package:

- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md`

QA read those files as required sources but did not edit them.

## QA Result

QA gate: pass.

Blocking product behavior found: none.

Documented smoke-data gap: current local data has no closed completed/admin rows, so closed `Open archive` row behavior and closed Workbench archive controls cannot be exercised against real local closed data in this environment.

Recommended next role: Integrator packaging/readiness for this evidence closeout. Follow-up recommendation, if closed smoke must become repeatable: route a separate Developer fixture-planning lane for a local-only disposable closed completed/admin data fixture or documented safe UI/API setup/cleanup flow.

## Integrator Packaging Checkpoint

Status: `integrator_accepted`
Date: 2026-06-28

Integrator accepted TASK_344A as a QA/data/procedure evidence lane after Reviewer plan gate and QA gate passed.

Accepted package files:

- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md`
- `docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_qa.md`
- `docs/lane_evidence/artifacts/TASK_344A_qa/`
- `docs/task_board.md`

Excluded residuals:

- Current Workbench dirty files under `frontend/src/features/project-workbench/`.
- `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*` governance/orchestration residuals.
- Product code/backend/API/schema/frontend API client/root tests/TASK_343A/B/C/TASK_344B accepted implementation files.
- Production/user data, public-drive files, Office documents, and LTR authority files.

Integrator validation:

- Required TASK_344A task, plan, Planner evidence, QA evidence, and QA artifact exist.
- Package `git diff --check` passed with LF/CRLF working-copy warning only.
- Forbidden-scope checks confirmed no product/backend/frontend/test/API/client/Workbench/TASK_343A/B/C/TASK_344B files were staged for TASK_344A.
- Board closeout states the lane outcome as a documented smoke-data gap, not as closed-row smoke success.

Stop point: local controlled package/commit only. Remote push intentionally not performed. If repeatable closed completed/admin smoke data is required later, route a separate Developer fixture-planning lane before creating fixture data or local mutation flows.
