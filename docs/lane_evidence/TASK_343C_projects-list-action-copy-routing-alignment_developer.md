# Developer Evidence - TASK_343C Projects List Action Copy/Routing Alignment

Status: integrator accepted
Task: `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`
Lane: `projects-list-action-copy-routing-alignment`
Role: Developer implementation
Last updated: 2026-06-27

## Role Boundary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`.
- Current lane: `projects-list-action-copy-routing-alignment`.
- Why allowed: Reviewer plan gate passed with no blocking findings, and the user explicitly requested Developer planning-first.
- This pass is documentation/evidence only.
- Stop point: do not implement frontend product code, do not modify tests, do not update `docs/task_board.md`, do not merge/commit/push, and do not start TASK_344 or any future scope.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context from `PRODUCT.md` and `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- TASK_343A task/plan/developer/QA evidence as needed
- TASK_343B task/plan/developer/QA evidence as needed
- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- TASK_339B task/plan/developer evidence
- read-only source inspection of current Projects registry helper, `ProjectListPage`, and focused registry tests

## Read-Only Code Inspection

Inspected without product-code edits:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`

Findings:

- Registry classification and copy are already centralized in `projectRegistryLifecycleViews.ts`.
- `ProjectListPage` already loads base rows with `listProjectRegistryRows()` and lifecycle overlays with `getProjectLifecycle(project_id)`.
- Current registry views remain `On-going`, `Planning`, `Closed`, and `All`.
- Current row action is a single routing button with visible copy `Open` and existing `onOpenProject(row.project_id)` behavior.
- The current registry code does not import or call `stopProjectLifecycle`, `resumeProjectLifecycle`, `closeProjectCompletedLifecycle`, or `closeProjectAdministrativeLifecycle`.
- TASK_343C can remain frontend-only and does not need `frontend/src/api/client.ts`, backend/API/schema, or Workbench changes.

## Plan Updates

Updated `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md` with:

- Developer planning-first anti-skip confirmation.
- read-only Projects registry inspection findings.
- exact implementation file list for a later implementation pass.
- locked paths for frontend API client, backend, Workbench, project-lifecycle frontend model, Workbench CSS, board, and future scope.
- state-specific status, next-step, row action, and route-intent copy matrix.
- confirmation that Projects list remains routing-only with no lifecycle mutation controls.
- TASK_343A/TASK_343B preservation rules.
- focused helper and component test plan.
- validation commands, mutation-helper scan, lifecycle write-action copy scan, future-scope scan, and forbidden-scope status checks.
- browser/QA smoke expectations and unavailable-browser residual handling.

## Future Implementation Scope After Approval

Future implementation may touch only:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css` only if small registry-specific wrapping/accessibility styling is needed
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`

Explicitly excluded:

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/`
- `frontend/src/features/project-lifecycle/`
- `frontend/src/workbench.css`
- TASK_343A/TASK_343B implementation files
- Projects list Stop/Resume/Close/Delete mutation controls
- Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residuals
- `docs/task_board.md`

## Implementation Requirements Captured

Projects list behavior:

- active formal/registered Matrix-needed rows: show operational Matrix/Workbench route intent.
- folder-created rows: preserve `Folder Created` status but route next step to Workbench setup, not folder-only action.
- active temporary/no-LTR rows: show planning route intent.
- stopped formal/registered rows: remain in `On-going`, show `Stopped`, and route to Workbench.
- stopped temporary/no-LTR rows: remain in `Planning`, show `Stopped`, and route to Workbench resume/admin archive context.
- closed completed/admin rows: remain in `Closed`, show archive status/copy, and use `Open archive`.
- closed legacy fallback: show `Closed`, `View readonly archive`, and `Open archive`.

Forbidden behavior:

- no direct registry Stop, Resume, Close project, Close as completed, Close administratively, Delete, menu, placeholder, route target, or lifecycle write helper call.
- no backend enum tokens in operator-facing copy.
- no Workbench lifecycle behavior changes.
- no API client changes.

## Validation Results

Commands run from `D:\PythonProject\connlab` after planning/evidence edits:

```powershell
Test-Path docs\task_343c_projects_list_action_copy_routing_alignment_plan.md
Test-Path docs\lane_evidence\TASK_343C_projects-list-action-copy-routing-alignment_developer.md
rg -n "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
rg -n "Stop project|Resume project|Close project|Close as completed|Close administratively|Delete project" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "StepInstance|Report generation|AI review|permissions|LAN/server|multi-user" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/project-dashboard.css
git diff --check -- docs/task_343c_projects_list_action_copy_routing_alignment_plan.md docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
rg -n "[ \t]$" docs/task_343c_projects_list_action_copy_routing_alignment_plan.md docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
git status --short -- frontend backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css docs/task_board.md docs/task_343c_projects_list_action_copy_routing_alignment_plan.md docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
```

Observed results:

- TASK_343C plan and Developer evidence files exist.
- read-only mutation-helper scan over Projects registry and `ProjectListPage` returned no matches.
- read-only Projects list lifecycle write-action copy scan returned no matches.
- read-only Projects registry future-scope scan returned no matches.
- `git diff --check` passed for the two TASK_343C Developer planning docs.
- trailing whitespace scan returned no matches; `rg` exit code `1` means no trailing whitespace was found.
- forbidden-scope status showed no `frontend/`, `backend/`, `tests/`, frontend API client, Workbench, project-lifecycle, or Workbench CSS changes from this planning-first pass.
- `docs/task_board.md` remains a known external board residual and was not edited by this pass.

## Risks And Follow-Ups

- Exact row action copy should be checked in Reviewer implementation-readiness and implementation review because it changes visible operator wording.
- Browser tooling availability remains uncertain. If unavailable, QA may record a non-blocking residual only after focused tests, source scans, build, and Reviewer scope checks pass.
- If registry volumes make per-row lifecycle overlays too slow, that should become a later backend/API registry lifecycle summary task, not an expansion of TASK_343C.
- Existing unrelated governance/orchestration residuals must be excluded from TASK_343C packaging.

## Decision

Developer planning gate: ready.

Recommended next role: Reviewer implementation-readiness gate.

## Stop Point

Stop after planning validation and completion callback. Do not start implementation, backend/API/schema changes, frontend API client changes, Workbench behavior changes, tests, board update, merge, commit, push, reset, delete, TASK_344, or unrelated cleanup.

---

## Implementation Pass - 2026-06-27

Status: implementation complete - pending Reviewer implementation gate

Allowed reason:

- Reviewer implementation-readiness gate passed with no blocking findings.
- User explicitly routed TASK_343C to Developer implementation pass.
- Implementation remained limited to Projects list action copy/routing alignment.

Changed files:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`

No `frontend/src/project-dashboard.css` change was needed.

Implementation summary:

- Added registry row action copy helpers for `Open Workbench` and `Open archive`.
- Added business-readable accessible row action labels while preserving the existing `onOpenProject(project_id)` route.
- Updated active temporary/no-LTR next-step copy to `Continue planning in Workbench`.
- Updated folder-created next-step copy to `Continue setup in Workbench`, so it routes to Workbench setup context rather than folder-only workflow.
- Kept stopped registered/formal copy as `Review or resume in Workbench`.
- Updated stopped temporary/no-LTR copy to `Resume or administratively archive from Workbench`.
- Updated closed completed/admin/legacy next-step copy to readonly archive language.
- Preserved TASK_339B views: `On-going`, `Planning`, `Closed`, and `All`.
- Preserved Projects list routing-only behavior. No Stop/Resume/Close/Delete mutation controls were added.
- Did not modify `frontend/src/api/client.ts`, backend, Workbench, project-lifecycle frontend model, or board files.

TDD red result:

Initial focused tests failed before implementation, as expected:

- missing `registryRowActionLabel(...)` / `registryRowActionAriaLabel(...)`.
- active planning still said `Continue planning`.
- folder-created still said `Open project folder`.
- closed rows still said `Open completed archive` / `Open administrative archive`.
- page row action still rendered generic `Open`.

Focused test coverage added/updated:

- active registered/formal and folder-created Workbench route intent.
- active temporary/no-LTR planning route intent.
- stopped formal/registered Workbench route intent.
- stopped temporary/no-LTR resume/admin-archive route intent.
- closed completed/admin/legacy archive copy and action labels.
- row action invokes the existing `onOpenProject(project_id)` callback.
- registry page renders no Stop/Resume/Close/Delete lifecycle mutation controls.
- lifecycle overlay failure keeps rows visible and uses compatibility labels without raw enum copy.

Validation commands run from `D:\PythonProject\connlab`:

```powershell
cd frontend
npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx
npm run build
```

```powershell
git diff --check -- frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
rg -n "[ \t]$" frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
rg -n "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
rg -n "Stop project|Resume project|Close project|Close as completed|Close administratively|Delete project" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "StepInstance|Report generation|AI review|permissions|LAN/server|multi-user" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/project-dashboard.css
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css docs/task_board.md
```

Observed results:

- Focused frontend tests passed: `2` files / `13` tests.
- `npm run build` passed; Vite reported only the existing chunk-size warning.
- `git diff --check` passed; Git printed only LF/CRLF normalization warnings.
- trailing whitespace scan returned no matches.
- lifecycle mutation-helper scan returned no matches.
- Projects list lifecycle write-action copy scan returned no matches.
- future-scope production scan returned no matches.
- forbidden-scope status output showed only `M docs/task_board.md`; this is a pre-existing external board residual and was not edited by this Developer implementation pass.

Scope proof:

- No backend/API/schema/write guard files were modified.
- `frontend/src/api/client.ts` was not modified.
- Workbench lifecycle behavior and TASK_343A/TASK_343B implementation files were not modified.
- `frontend/src/features/project-lifecycle/` and `frontend/src/workbench.css` were not modified.
- No Projects list direct Stop, Resume, Close, Close as completed, Close administratively, Delete, menu, placeholder, or mutation helper call was added.
- No StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope was added.
- `docs/task_board.md` was not edited by this pass.
- No merge, commit, push, reset, delete, or unrelated cleanup was performed.

Residual risks / follow-ups:

- Browser/narrow viewport and tab-order smoke can be handled by QA if Reviewer decides this visible row action copy change needs manual confidence. If browser tooling is unavailable, focused component tests, source scans, build, and Reviewer scope checks should be enough to record a non-blocking residual.
- If real registry volume makes per-row lifecycle overlay fetching too costly, that should be handled by a later backend/API registry lifecycle summary task, not by expanding TASK_343C.

Recommended next role: Reviewer implementation gate.

Stop point: stop after evidence update, validation, and completion callback. Do not proceed to QA, Integrator, TASK_344, board update, merge, commit, or push.

---

## Integrator Packaging Readiness - Accepted

Date: 2026-06-27

### Integrator Gate Result

Integrator gate: accepted.

### Package Boundary

TASK_343C package files included:

- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_qa.md`
- `docs/task_board.md`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`

Excluded unrelated dirty paths:

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/`
- `.agents/skills/connlab-planner/`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

### Validation Summary

- Reviewer implementation gate: pass.
- QA gate: pass.
- Focused Projects registry/list tests: passed, `2` files / `13` tests.
- Frontend build: passed, with existing non-blocking Vite chunk-size warning only.
- Package `git diff --check`: passed with LF/CRLF working-copy warnings only.
- Trailing whitespace scan: no matches.
- Mutation-helper scan: no matches.
- Registry write-action copy scan: no matches.
- Future-scope production scan: no matches.
- Forbidden scope status: no backend/API/schema/frontend API client/Workbench/TASK_343A/TASK_343B/TASK_343D/future-scope product changes.

### Stop Point

TASK_343C is locally accepted by Integrator. Remote push was intentionally not performed.

Recommended next role: User if the TASK_343 series is complete, or Planner only if another TASK_343 sublane is explicitly required.
