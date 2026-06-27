# QA Evidence - TASK_343C Projects List Action Copy/Routing Alignment

Status: `qa_pass`
Task: `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`
Lane: `projects-list-action-copy-routing-alignment`
Role: QA / Smoke Owner
Last updated: 2026-06-27

## Role Boundary

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current active task: `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`.
- Current lane: `projects-list-action-copy-routing-alignment`.
- Why this QA gate is allowed: delegated Reviewer result states `reviewer_pass`; Reviewer implementation gate passed with no blocking findings and QA is required because TASK_343C changes visible Projects list operator action copy/routing intent.
- QA boundary: run validation and write QA evidence/checkpoint only.
- Stop point: do not modify product code, do not update `docs/task_board.md`, do not merge/commit/push, and do not start Integrator.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- TASK_343A task, plan, Developer evidence, and QA evidence
- TASK_343B task, plan, Developer evidence, and QA evidence
- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`
- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`
- Read-only source inspection of:
  - `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
  - `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
  - `frontend/src/pages/ProjectListPage.tsx`
  - `frontend/src/pages/ProjectListPage.test.tsx`

## Environment

- Workspace: `D:\PythonProject\connlab`
- Shell: Windows PowerShell with explicit UTF-8 output
- Frontend working directory: `D:\PythonProject\connlab\frontend`
- Date: 2026-06-27
- Browser tooling: no direct browser navigation/screenshot tool was exposed. Tool discovery exposed `send_message_to_thread` and Node REPL/Figma tools; local `frontend/node_modules` does not contain `playwright` or `@playwright/test`.

## Validation Commands And Results

### Focused Projects Registry/List Tests

Command run from `D:\PythonProject\connlab\frontend`:

```powershell
npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx
```

Observed result:

- `2` test files passed.
- `13` tests passed.
- No failing tests.

Coverage included stopped formal/temporary classification, active planning and folder-created Workbench routing copy, closed completed/admin archive copy, closed legacy fallback archive copy, raw enum hiding, default `On-going`, `Planning`, `Closed`, route callback behavior, no registry lifecycle write controls, and lifecycle overlay failure fallback.

### Frontend Build

Command run from `D:\PythonProject\connlab\frontend`:

```powershell
npm run build
```

Observed result:

- TypeScript/Vite build passed.
- Vite transformed `111` modules and completed successfully.
- Existing non-blocking Vite chunk-size warning remained for a post-minification JS chunk over `500 kB`.

### Diff Whitespace Check

Command run from `D:\PythonProject\connlab`:

```powershell
git diff --check -- frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
```

Observed result:

- Passed with no whitespace errors.
- Git printed LF/CRLF working-copy warnings only.

### Trailing Whitespace Scan

Command run from `D:\PythonProject\connlab`:

```powershell
rg -n "[ \t]$" frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
```

Observed result:

- No matches.
- Exit code `1` means `rg` found no trailing whitespace.

### Mutation Helper Scan

Command run from `D:\PythonProject\connlab`:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|deleteProject|removeProject|onStop|onResume|onClose|onDelete" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
```

Observed result:

- No matches.
- Exit code `1` means Projects registry production code and `ProjectListPage` do not import/call lifecycle mutation helpers or direct delete/remove callbacks.

### Registry Write-Action Copy Scan

Command run from `D:\PythonProject\connlab`:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "Stop project|Resume project|Close project|Close as completed|Close administratively|Delete project" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
```

Observed result:

- No matches.
- Exit code `1` means no direct Stop/Resume/Close/Delete action copy was added to Projects list production code.

### Future-Scope Production Scan

Command run from `D:\PythonProject\connlab`:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "StepInstance|Report generation|AI review|permissions|LAN/server|multi-user|execution persistence|Report|AI|permission|LAN" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
```

Observed result:

- No matches.
- Exit code `1` means no TASK_343C registry production future-scope copy/control was found.

### Forbidden-Scope Status Check

Command run from `D:\PythonProject\connlab`:

```powershell
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css docs/task_board.md frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx
```

Observed result:

```text
 M docs/task_board.md
 M frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts
 M frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts
 M frontend/src/pages/ProjectListPage.test.tsx
 M frontend/src/pages/ProjectListPage.tsx
```

Interpretation:

- Product changes are limited to the approved TASK_343C Projects registry/list frontend files.
- No backend, root tests, frontend API client, Workbench, project-lifecycle model, or Workbench CSS changes appear in this scope check.
- `docs/task_board.md` remains the known external residual and was not edited by QA.

Additional task/doc status check:

```powershell
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css tasks docs/task_board.md
```

Observed result:

```text
 M docs/task_board.md
?? tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md
```

Interpretation:

- The untracked TASK_343C task file is a lane governance artifact, not product code.
- No forbidden product scope appeared.

## Static / Source Inspection Findings

- `ProjectListPage` imports `registryRowActionLabel(...)` and `registryRowActionAriaLabel(...)`.
- Row action still invokes `onOpenProject(row.project_id)`.
- Visible row action copy is state-aware only:
  - active/stopped/planning/folder-created rows use `Open Workbench`.
  - closed completed/admin/legacy rows use `Open archive`.
- TASK_339B view categories remain present: `On-going`, `Planning`, `Closed`, and `All`.
- Tests/source cover these state cases:
  - active formal/registered rows route to Workbench.
  - folder-created rows keep `Folder Created` status and use `Continue setup in Workbench`.
  - temporary/no-LTR rows use planning Workbench route copy.
  - stopped registered rows stay in `On-going` and open Workbench.
  - stopped temporary rows stay in `Planning` and open Workbench.
  - closed completed rows show `Closed: Completed`, readonly archive next-step copy, and `Open archive`.
  - closed administrative rows show `Closed: Administrative`, readonly archive next-step copy, and `Open archive`.
  - closed legacy fallback rows show `Closed`, `View readonly archive`, and `Open archive`.
- Raw enum tokens such as `closed_completed`, `closed_administrative`, `cancelled`, `lifecycle_state`, and `closure_type` are covered by tests as not user-facing copy.

## QA Coverage Result

1. Focused Projects registry/list tests: pass, `2` files / `13` tests.
2. Frontend build: pass, with existing Vite chunk-size warning only.
3. `git diff --check`: pass, LF/CRLF warnings only.
4. Trailing whitespace scan: pass, no matches.
5. Mutation-helper scan: pass, no matches.
6. Registry write-action copy scan: pass, no matches.
7. Future-scope production scan: pass, no matches.
8. Projects list remains routing-only: pass. No direct Stop/Resume/Close/Delete controls or lifecycle mutation helper calls were found; row action still calls `onOpenProject(project_id)`.
9. Action copy/routing state cases: pass by focused tests and source inspection for active formal/registered, folder-created, temporary/no-LTR, stopped formal/temporary, closed completed/admin, and closed legacy fallback.
10. TASK_339B categories/filtering preserved: pass by tests and source inspection of `On-going`, `Planning`, `Closed`, and `All`.
11. Forbidden-scope status: pass. No backend/API/schema/frontend API client/Workbench/TASK_343A/TASK_343B/TASK_343D/future-scope product changes were observed. Known residuals are `M docs/task_board.md` and the untracked TASK_343C task file.
12. Browser `/projects` smoke: not executed because no reliable direct browser control/screenshot tool or local Playwright dependency was available in this thread.

## Residual Risk

Real browser `/projects` smoke for row action labels/routing, narrow viewport, and keyboard focus was not performed because browser automation was unavailable. This is accepted as a non-blocking residual because component tests, static/source checks, build validation, mutation-helper scans, write-action scans, and forbidden-scope status checks passed.

## Decision

QA gate: pass.

No QA-blocking finding was found.

Recommended next role: Integrator packaging/readiness.

## Stop Point

Stop after QA evidence and completion callback. Do not modify product code, update board, merge, commit, push, start Integrator, or start TASK_343D from this QA role.
