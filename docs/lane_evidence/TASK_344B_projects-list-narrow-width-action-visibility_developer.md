# TASK_344B Developer Evidence

Status: complete - Integrator accepted
Task: TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY
Lane: projects-list-narrow-width-action-visibility
Role: Developer
Date: 2026-06-28

## Summary

Developer implementation pass completed for the `/projects` narrow-width action visibility lane.

The implementation keeps the desktop Projects registry table, adds stable row/cell markers for narrow layouts, and switches the table to a compact stacked row treatment under a narrow media query. The narrow row order is Project ID, Status, Next Step, Action, then lower-priority Sample Description and Test Item details.

The Projects list remains routing-only. No direct Stop, Resume, Close, Delete, lifecycle mutation helper call, backend/API/schema/client change, Workbench lifecycle change, TASK_343A/B/C behavior change, TASK_344A smoke-data fixture/procedure change, board update, merge, commit, or push was performed.

Developer implementation gate: ready for review.

Recommended next role: Reviewer implementation gate.

## Required Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` product context and product reference expectations
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md`
- `tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md`
- `docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md`
- TASK_343C task, plan, Developer evidence, and QA evidence as routing-only reference
- read-only source inspection of `frontend/src/pages/ProjectListPage.tsx`
- read-only source inspection of `frontend/src/project-dashboard.css`
- read-only source inspection of `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- read-only source inspection of `frontend/src/pages/ProjectListPage.test.tsx`

## Board And Scope Check

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current task/lane: `TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY` / `projects-list-narrow-width-action-visibility`.

Allowed reason: user delegated a Developer planning-first pass after Reviewer plan gate passed. The board row defines TASK_344B as a post-acceptance smoke follow-up for `/projects` narrow-width Status / Next Step / Action visibility.

Scope boundary:

- TASK_344B owns only `/projects` narrow-width action/status/next-step discoverability.
- TASK_343C routing-only semantics must remain: Projects list row actions route to Workbench/archive context only.
- TASK_339B On-going / Planning / Closed / All views must remain intact.
- TASK_344A closed smoke data/procedure is separate and read-only for this pass.
- Backend, API/schema, frontend API client, Workbench lifecycle implementation, TASK_343A/B/C accepted implementation, future scope, and unrelated governance residuals are excluded.

## Read-Only Findings

- `frontend/src/project-dashboard.css` currently sets `.project-table { min-width: 1060px; }`.
- `.project-table-wrap` currently uses `overflow-x: auto`.
- `ProjectListPage` renders `Status`, `Next Step`, and `Action` as right-side table columns after Project ID, Sample Description, and Test Item.
- `ProjectListPage` already routes the row button through `onOpenProject(row.project_id)`.
- `projectRegistryLifecycleViews.ts` already supplies business-readable status, next-step, action label, and aria label copy without exposing raw backend enum tokens.
- Existing focused tests cover TASK_339B filters, TASK_343C route copy, no registry write actions, and lifecycle overlay fallback, but do not structurally prove a narrow-width layout.

## Planned Implementation Shape

Later implementation should use a small responsive table treatment rather than a broad registry redesign.

Exact first implementation file list:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`

Implementation details to use later:

- Add stable `data-label` attributes and priority class names to table cells.
- Keep one route button per row and keep it wired to `onOpenProject(row.project_id)`.
- At narrow width, set the table to a compact stacked row presentation.
- Order narrow row content as Project ID, Status, Next Step, Action, then Sample Description and Test Item.
- Use business-readable labels already produced by TASK_343C helper functions.
- Keep desktop table behavior unchanged outside the narrow media query.

Helper files not planned for the first implementation:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`

Those remain optional only if implementation discovers a real accessibility or copy-shape blocker. No backend/API/client changes are needed.

## Planned Tests And QA

Future Developer tests should cover:

- narrow row structural markers: `data-label="Status"`, `data-label="Next Step"`, and `data-label="Action"`.
- `Open Workbench` remains the action for active, stopped, planning, and folder-created rows.
- `Open archive` remains the action for closed completed/admin/legacy fallback rows where lifecycle fixtures are available.
- `On-going`, `Planning`, `Closed`, and `All` view filters still work.
- no direct Stop, Resume, Close, Delete, or lifecycle mutation controls are present in Projects list.
- action click still calls `onOpenProject(project_id)`.

Future QA/browser smoke should verify a viewport around 514px:

- Project ID, Status, Next Step, and Action are discoverable without horizontal scroll.
- keyboard focus reaches the visible route action.
- active/stopped rows still route with `Open Workbench`.
- closed rows route with `Open archive` if TASK_344A data is available.

If browser tooling or closed data is unavailable, QA should record the specific blocker. TASK_344A remains the owner for closed completed/admin smoke data.

## Files Updated In This Planning Pass

- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`

## Validation

Planned and executed after docs edits:

```powershell
Test-Path docs/task_344b_projects_list_narrow_width_action_visibility_plan.md
Test-Path docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
git diff --check -- docs/task_344b_projects_list_narrow_width_action_visibility_plan.md docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
rg -n "[ \t]$" docs/task_344b_projects_list_narrow_width_action_visibility_plan.md docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
git status --short -- frontend backend tests docs/task_board.md tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md
```

Observed results:

- `Test-Path` returned `True` for the TASK_344B plan and Developer evidence files.
- `git diff --check` passed for the two TASK_344B Developer planning files.
- trailing whitespace scan returned no matches. Exit code `1` means `rg` found no trailing whitespace.
- forbidden-scope status showed no `frontend/`, `backend/`, or root `tests/` product changes from this planning pass.
- targeted status showed:

```text
 M docs/task_board.md
?? docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md
?? docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
?? docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md
?? docs/task_344b_projects_list_narrow_width_action_visibility_plan.md
?? tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md
?? tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md
```

Interpretation:

- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md` is the new Developer evidence created by this pass.
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md` is the TASK_344B plan refined by this pass.
- `docs/task_board.md`, TASK_344A files, and TASK_344B task/planner artifacts are external Planner/board residuals already present in the lane package context and were not edited by this Developer planning-first pass.

## Implementation Pass

Allowed reason: Orchestrator delegated the Developer implementation pass after Reviewer implementation-readiness gate passed. The user prompt explicitly authorized the approved TASK_344B strategy and May Touch list.

Changed files in this implementation pass:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`

Files not touched:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/api/client.ts`
- backend, root tests, Workbench lifecycle files, TASK_343A/B/C implementation, TASK_344A fixture/procedure files

Implementation details:

- Added `project-registry-row` to each Projects registry table row.
- Added stable `data-label` attributes to Project ID, Sample Description, Test Item, Status, Next Step, and Action cells.
- Added priority cell class markers: `registry-project-id-cell`, `registry-status-cell`, `registry-next-step-cell`, `registry-action-cell`, `registry-sample-cell`, and `registry-test-item-cell`.
- Added a `max-width: 640px` media query in `project-dashboard.css` that removes the 1060px table minimum, visually hides the header, stacks row cells, and orders the narrow row as Project ID, Status, Next Step, Action, Sample Description, Test Item.
- Kept the single row route button and existing `onOpenProject(row.project_id)` callback.
- Kept TASK_343C `Open Workbench` / `Open archive` helper copy and TASK_339B views unchanged.

Focused test added:

- `ProjectListPage` now verifies narrow-width row structural markers, `data-label` coverage for Status / Next Step / Action, single route button placement, no Stop/Resume/Close/Delete registry controls, and the `onOpenProject(project_id)` callback.

## Implementation Validation

Focused frontend tests:

```powershell
cd frontend
npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx
```

Result:

- Passed.
- `2` test files passed.
- `14` tests passed.

Frontend build:

```powershell
cd frontend
npm run build
```

Result:

- Passed.
- Existing Vite chunk-size warning only.

Diff check:

```powershell
git diff --check -- frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
```

Result:

- Passed.
- Only LF/CRLF working-copy warnings for frontend files.

Trailing whitespace scan:

```powershell
rg -n "[ \t]$" frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
```

Result:

- No matches. Exit code `1` means `rg` found no trailing whitespace.

Lifecycle mutation-helper scan:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|deleteProject|removeProject|onStop|onResume|onClose|onDelete" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
```

Result:

- No matches. Exit code `1` means Projects registry production code and `ProjectListPage` do not import/call lifecycle mutation helpers or direct delete/remove callbacks.

Registry write-action and future-scope scan:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "Stop project|Resume project|Close project|Close as completed|Close administratively|Delete project|StepInstance|Report generation|AI review|permissions|LAN/server|multi-user" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/project-dashboard.css
```

Result:

- No matches. Exit code `1` means no direct Stop/Resume/Close/Delete action copy or future-scope copy was added to Projects list production code.

UI anti-pattern scan:

```powershell
rg -n "border-left:\s*[2-9]px|border-right:\s*[2-9]px|background-clip:\s*text|linear-gradient" frontend/src/project-dashboard.css
```

Result:

- No matches. Exit code `1` means this implementation did not add thick side stripes, gradient text, or gradients in `project-dashboard.css`.

Forbidden-scope status check:

```powershell
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md docs/task_board.md
```

Observed output:

```text
 M docs/task_board.md
?? docs/lane_evidence/TASK_344A_closed-lifecycle-smoke-data-fixture_planner.md
?? docs/task_344a_closed_lifecycle_smoke_data_fixture_plan.md
?? tasks/TASK_344A_CLOSED_LIFECYCLE_SMOKE_DATA_FIXTURE.md
```

Interpretation:

- No backend, root tests, frontend API client, Workbench, project-lifecycle, Workbench CSS, or TASK_343A/B/C task files were modified by this pass.
- `docs/task_board.md` and TASK_344A planning files are known external board/planning residuals and were not edited by this implementation pass.

Package-scope status check:

```powershell
git status --short -- frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts
```

Observed output:

```text
 M frontend/src/pages/ProjectListPage.test.tsx
 M frontend/src/pages/ProjectListPage.tsx
 M frontend/src/project-dashboard.css
?? docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md
```

Interpretation:

- TASK_344B implementation package is limited to the approved page, test, CSS, and evidence files.
- Projects registry helper files were not modified.

## Browser Smoke

Browser tooling attempt:

- Vite preview was started from `frontend` on `127.0.0.1:4173` after `npm run build`.
- Playwright package import succeeded through `node_repl`.
- Headless Chromium launch failed because the local Playwright browser executable is missing:

```text
browserType.launch: Executable doesn't exist at C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe
Please run: npx playwright install
```

Cleanup:

- The preview server parent process and the remaining listening child process on port `4173` were stopped.
- A follow-up port check showed no listener remaining on `127.0.0.1:4173`.

Result:

- 514px browser smoke could not be completed in this thread due to missing Playwright browser binary.
- QA should run real browser/manual smoke at around 514px as the next validation gate.

## Risks And Follow-Ups

- JSDOM tests prove markup and routing behavior but cannot prove actual 514px visual layout. QA/browser smoke remains required because Playwright browser executable is unavailable in this thread.
- Closed `Open archive` real smoke still depends on TASK_344A data availability.
- Existing uncommitted board/TASK_344A/TASK_344B planning residuals may appear in status and must be packaged by Integrator separately from this Developer planning pass.

## Stop Point

Stop after implementation validation, evidence update, and completion callback. Do not start Reviewer, QA, Integrator, TASK_344A fixture work, board updates, merge, commit, push, reset, delete, or unrelated cleanup from this Developer implementation pass.

## Integrator Packaging Checkpoint

Status: `integrator_accepted`
Date: 2026-06-28

Integrator accepted TASK_344B after Reviewer implementation gate and QA gate passed.

Accepted package files:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css`
- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_developer.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_qa.md`
- `docs/lane_evidence/artifacts/TASK_344B_qa/`
- `docs/task_board.md`

Excluded residuals:

- TASK_344A closed lifecycle smoke-data fixture task/plan/evidence files.
- `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*` governance/orchestration residuals.
- backend/API/schema/frontend API client, Workbench lifecycle implementation, TASK_343A/B/C implementation, and future-scope product paths.

Integrator validation:

- Focused registry/list tests passed: `2` files / `14` tests.
- Frontend build passed with the existing non-blocking Vite chunk-size warning only.
- Package `git diff --check` passed with LF/CRLF working-copy warnings only.
- Mutation-helper, registry write-action, future-scope, thick side-stripe, and forbidden-scope checks passed.
- QA real browser smoke at `514x720` via system Chrome CDP passed and screenshot artifacts were packaged.

Stop point: local controlled package/commit only. Remote push intentionally not performed. Separate TASK_344A planning residuals remain outside this package and must be routed through their own legal gate if pursued.
