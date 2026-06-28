# QA Evidence - TASK_344B Projects List Narrow Width Action Visibility

Status: `qa_pass`
Task: `TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY`
Lane: `projects-list-narrow-width-action-visibility`
Role: QA / Smoke Owner
Last updated: 2026-06-28

## Role Boundary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task/lane: `TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY` / `projects-list-narrow-width-action-visibility`.
- Why this QA gate is allowed: Orchestrator delegated QA after Reviewer implementation gate passed.
- QA boundary: validation and QA evidence/checkpoint only.
- Stop point: do not modify product source/tests, backend/API/schema/frontend API client, Workbench lifecycle implementation, TASK_343A/B/C implementation, TASK_344A fixture/procedure files, `docs/task_board.md`, merge/commit/push, or start Integrator.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`
- Browser control skill instructions for local browser/manual smoke
- Read-only source inspection of:
  - `frontend/src/pages/ProjectListPage.tsx`
  - `frontend/src/pages/ProjectListPage.test.tsx`
  - `frontend/src/project-dashboard.css`

## Environment

- Workspace: `D:\PythonProject\connlab`
- Shell: Windows PowerShell with explicit UTF-8 output
- Frontend URL: `http://localhost:5173/projects`
- Local app availability: `Invoke-WebRequest http://localhost:5173/projects` returned `STATUS 200`
- Browser smoke path:
  - In-app browser control was attempted first but could not create/attach a tab: `Timed out waiting for the Browser webview to attach for this browser-use page`; follow-up tab listing returned no active tabs.
  - QA then used installed system Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`) with headless Chrome DevTools Protocol at `514x720`.
  - This provided real browser rendering, screenshots, keyboard Tab focus, select change, and route-click verification without installing Chromium or modifying product code.

## Screenshot Artifacts

- `docs/lane_evidence/artifacts/TASK_344B_qa/01_projects_514_ongoing_cdp.png`
- `docs/lane_evidence/artifacts/TASK_344B_qa/02_projects_514_planning_cdp.png`
- `docs/lane_evidence/artifacts/TASK_344B_qa/03_projects_514_closed_cdp.png`
- `docs/lane_evidence/artifacts/TASK_344B_qa/04_projects_514_route_after_click_cdp.png`
- Additional initial Chrome screenshot: `docs/lane_evidence/artifacts/TASK_344B_qa/projects_514_ongoing_chrome.png`

## Validation Commands And Results

### Focused Frontend Tests

Command run from `D:\PythonProject\connlab\frontend`:

```powershell
npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx
```

Observed result:

- Passed.
- `2` test files passed.
- `14` tests passed.

Coverage includes TASK_339B filters, TASK_343C row action copy/routing, no registry lifecycle write controls, closed fixture behavior, and TASK_344B narrow-row structural markers.

### Frontend Build

Command run from `D:\PythonProject\connlab\frontend`:

```powershell
npm run build
```

Observed result:

- Passed.
- Vite transformed `111` modules.
- Existing non-blocking Vite chunk-size warning remained.

### Static Safety Scans

Mutation-helper scan:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|deleteProject|removeProject|onStop|onResume|onClose|onDelete" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
```

Observed result:

- No matches.

Registry write-action / future-scope scan:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "Stop project|Resume project|Close project|Close as completed|Close administratively|Delete project|StepInstance|Report generation|AI review|permissions|LAN/server|multi-user" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/project-dashboard.css
```

Observed result:

- No matches.

Diff check:

```powershell
git diff --check -- frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
```

Observed result:

- Passed.
- Git printed LF/CRLF working-copy warnings only.

Trailing whitespace scan:

```powershell
rg -n "[ \t]$" frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
```

Observed result:

- No matches.

Forbidden-scope status check:

```powershell
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md docs/task_board.md
```

Observed result:

```text
 M docs/task_board.md
?? docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md
?? docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md
?? tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md
```

Interpretation:

- No backend, root tests, frontend API client, Workbench, project-lifecycle, Workbench CSS, or TASK_343A/B/C files are modified in this scope check.
- `docs/task_board.md` and TASK_344A planning files are known external planning/board residuals and were not edited by QA.

Package-scope status check before QA evidence:

```powershell
git status --short -- frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_qa.md
```

Observed result:

```text
 M frontend/src/pages/ProjectListPage.test.tsx
 M frontend/src/pages/ProjectListPage.tsx
 M frontend/src/project-dashboard.css
?? docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
```

QA added this QA evidence file and screenshot artifacts only.

## Real Browser Smoke - 514px Chrome CDP

Chrome command strategy:

- Launched system Chrome headless with `--window-size=514,720` and Chrome DevTools Protocol.
- Loaded `http://localhost:5173/projects`.
- Captured screenshots.
- Read real rendered cell rectangles and viewport widths.
- Sent Tab key events for keyboard focus.
- Clicked visible `Open Workbench` route action and verified URL/navigation.
- Changed `Project view` select to `Planning` and `Closed` through browser DOM events and captured screenshots/state.

### On-going View

Observed at effective `innerWidth: 488`:

- `documentElement.clientWidth: 488`
- `documentElement.scrollWidth: 473`
- No page-level horizontal overflow.
- First active row visible stacked order:
  - `Project ID`: `DL-2026-01-002`
  - `Status`: `Matrix Needed`
  - `Next Step`: `Open Matrix authority`
  - `Action`: `Open Workbench`
  - `Sample Description`
  - `Test Item`
- First stopped row visible stacked order:
  - `Project ID`: `dl-2026-04-001`
  - `Status`: `Stopped`
  - `Next Step`: `Review or resume in Workbench`
  - `Action`: `Open Workbench`
- For the first five On-going rows, each `Project ID`, `Status`, `Next Step`, and `Action` cell had `visible: true` within the viewport width.
- The remaining scrollers were the visually hidden `registry-control-sr-only` spans and visually hidden table `thead`; not the row content path.

### Keyboard Focus

Chrome CDP sent Tab key events from the page. The focus trail reached visible route action buttons:

- `Open Workbench for DL-2026-01-002, project workspace`
- `Open Workbench for dl-2026-04-001, project workspace`
- Additional visible row action buttons after that

Result: keyboard focus can reach visible route action buttons at the target width.

### Route Action Click

Chrome CDP clicked the first visible `Open Workbench` button:

- Before click:
  - URL: `http://localhost:5173/projects`
  - Button: `Open Workbench`
  - ARIA: `Open Workbench for DL-2026-01-002, project workspace`
  - Visible at click point
- After click:
  - URL: `http://localhost:5173/projects/ce15026d119f408f80970ea7077f6e41`
  - Heading: `Project workbench`

Result: route action remains functional and routes into Workbench.

### Planning View

Chrome CDP changed `Project view` to `Planning`.

Observed first Planning rows:

- `TMP-16BA322A`
  - `Temporary Planning`
  - `Status`: `Stopped`
  - `Next Step`: `Resume or administratively archive from Workbench`
  - `Action`: `Open Workbench`
- Additional temporary stopped rows used the same Workbench route action.

Result: planning/stopped temporary rows remain discoverable and route-oriented at 514px.

### Closed View

Chrome CDP changed `Project view` to `Closed`.

Observed result:

- Closed view rendered successfully at 514px.
- Current data shows `No projects in this view`.
- A read-only lifecycle API sweep returned `NO_CLOSED_LIFECYCLE_ROWS`.

Interpretation:

- Real `Open archive` closed-row smoke is blocked by missing TASK_344A closed completed/admin data.
- This is a TASK_344A data dependency and does not block TASK_344B because TASK_344B UI did not regress and focused tests cover closed completed/admin/legacy row action copy.

## Source/CSS Inspection

`ProjectListPage.tsx` now renders stable narrow-layout markers:

- `tr.project-registry-row`
- `data-label="Project ID"`
- `data-label="Status"`
- `data-label="Next Step"`
- `data-label="Action"`
- priority classes:
  - `registry-project-id-cell`
  - `registry-status-cell`
  - `registry-next-step-cell`
  - `registry-action-cell`
  - `registry-sample-cell`
  - `registry-test-item-cell`
- action button still calls `onOpenProject(row.project_id)`

`project-dashboard.css` contains the narrow media query:

- `@media (max-width: 640px)`
- `.project-table-wrap { overflow-x: visible; }`
- `.project-table { min-width: 0; }`
- row stack order:
  - `registry-project-id-cell`: order `1`
  - `registry-status-cell`: order `2`
  - `registry-next-step-cell`: order `3`
  - `registry-action-cell`: order `4`
  - `registry-sample-cell`: order `5`
  - `registry-test-item-cell`: order `6`
- `.registry-action-cell .row-action { width: 100%; }`

## QA Coverage Result

1. 514px real browser Status / Next Step / Action visibility: pass.
2. No horizontal scroll required to discover Project ID, Status, Next Step, and Action in On-going rows: pass.
3. Keyboard focus reaches visible route action button: pass.
4. Active/stopped rows still show and route `Open Workbench`: pass.
5. Planning/stopped temporary rows still show and route `Open Workbench`: pass.
6. Folder-created rows: current environment has `folder_created: 0`; focused tests cover folder-created `Open Workbench` behavior and narrow markers.
7. Closed rows: current environment has no closed lifecycle data; focused tests cover `Open archive`, and missing real data is recorded as TASK_344A dependency.
8. Projects list remains routing-only: pass; no direct Stop/Resume/Close/Delete controls or lifecycle mutation helper calls found.
9. TASK_339B filters remain usable: pass for On-going, Planning, Closed; All remains covered by unchanged selector/options and focused tests.
10. Build/static validation: pass.
11. Forbidden scope: pass; no backend/API/schema/frontend API client/Workbench/TASK_343A/B/C changes observed in targeted status.

## Residual Risk

- Real closed completed/admin `Open archive` browser smoke could not be performed because current data contains no closed lifecycle rows. This remains a TASK_344A smoke-data dependency.
- The in-app browser tool was not usable due webview attach timeout, but system Chrome CDP successfully provided real 514px browser rendering and interaction coverage.

## Decision

QA gate: pass.

No TASK_344B blocking finding was found.

Recommended next role: Integrator packaging/readiness.

## Stop Point

Stop after QA evidence and completion callback. Do not modify product source/tests, update `docs/task_board.md`, merge, commit, push, start Integrator, or start TASK_344A from this QA role.
