# TASK_343C Projects List Action Copy Routing Alignment Plan

Status: implementation complete - Integrator accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: projects-list-action-copy-routing-alignment
Role: Developer planning-first
Last Updated: 2026-06-27

## 1. Discovery Gate

### Current Phase, Task, Lane, Role

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: no active implementation lane. `docs/task_board.md` marks `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW` complete and accepted after Developer, Reviewer, QA, and Integrator gates.

Current role: Planner/Designer.

Why Planner is allowed: `docs/task_board.md` names TASK_343C as the next candidate only through formal Discovery Gate and approved lane creation, and the user explicitly requested TASK_343C formal planning-first lane creation/activation.

This pass is planning only. It does not implement frontend UI, backend behavior, tests, database changes, API changes, runtime routing, lifecycle writes, or Workbench behavior.

### User Goal Restatement

TASK_343C should align Projects list action copy and routing with the Workbench lifecycle actions delivered by TASK_343A and TASK_343B. The Projects list should remain a registry and routing surface, not a duplicate lifecycle mutation surface. Operators should understand whether to continue setup, resume from Workbench, or view a readonly archive, and then open the appropriate Workbench context. The lane must preserve TASK_339B lifecycle filters/categories and avoid backend/API changes unless a later approved task proves they are necessary.

### Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context from `PRODUCT.md` and `DESIGN.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- TASK_343A task, plan, developer evidence, and QA evidence
- TASK_343B task, plan, Planner evidence, developer evidence, and QA evidence
- TASK_339B task, plan, and developer evidence
- read-only source inspection of:
  - `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
  - `frontend/src/pages/ProjectListPage.tsx`
  - `frontend/src/api/client.ts`

### Confirmed By User

- TASK_343B is Integrator accepted in local commit `e0b0835306250e2d2cc43b601a6e31cd9706759c`.
- TASK_343C product goal is Projects list action copy/routing alignment.
- Lifecycle authority should stay in Workbench.
- Projects list should route users into the right Workbench context instead of exposing duplicate lifecycle mutation flows.
- Existing Projects list filtering/categories from TASK_339B must be preserved.
- Planner must not write product code, modify TASK_343A/TASK_343B implementation, commit, push, reset, or delete.

### Confirmed By Repository Evidence

- `docs/task_board.md` records TASK_343, TASK_343A, and TASK_343B complete/accepted, and names TASK_343C as the next formal lane candidate.
- Parent TASK_343 split explicitly named `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT` as the third implementation lane.
- TASK_339B implemented `On-going`, `Planning`, `Closed`, and `All` registry views and kept registry actions read/navigation-oriented with `Open` only.
- Current Projects registry implementation has:
  - `registryStatusLabel(...)`
  - `registryNextStepLabel(...)`
  - `registryLifecycleClassName(...)`
  - `ProjectListPage` row action label `Open`
- Current `frontend/src/api/client.ts` exposes lifecycle mutation helpers, but TASK_343C does not need to import or call them because lifecycle mutations belong to Workbench.
- TASK_343A/TASK_343B evidence records no Projects registry or `ProjectListPage` product changes.
- Current worktree has unrelated governance/orchestration residuals under `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*`; these are excluded from this lane.

### Inferred By Planner

- TASK_343C can remain frontend-only because the needed registry row and lifecycle overlay data are already consumed by TASK_339B.
- The likely implementation area is the existing Projects registry helper plus `ProjectListPage` row action copy/accessibility.
- `frontend/src/api/client.ts` should remain locked because TASK_343C needs no new API contract.
- QA may be useful if row action routing/accessibility copy changes are visible enough that component tests alone are not sufficient, but Reviewer can decide whether QA is required after implementation.

### Not Yet Confirmed

- Exact final English labels for every row action should be reviewed by Reviewer before Developer implementation.
- Whether browser control will be available for future QA is unknown. This does not block lane activation because component tests and source scans can cover the baseline, with browser smoke recorded if available.

These unknowns do not change May Touch, Must Not Touch, API ownership, or serial ordering, so they do not block Reviewer plan gate.

### Planning Risk

- The Projects list could accidentally become a second lifecycle action surface with Stop/Resume/Close buttons.
- The lane could drift into a registry redesign instead of a copy/routing alignment.
- Developer could touch Workbench lifecycle behavior or API client files even though TASK_343A/B and TASK_337A already own those areas.
- Raw backend enum language could leak into operator-facing registry copy.

### Continue Decision

Definition of Ready is satisfied for a formal TASK_343C planning-first lane because:

- user goal and operator scenario are clear.
- current board state and dependencies are verified.
- existing Projects registry behavior was checked from task/evidence files and read-only source inspection.
- dependencies and serialization constraints are explicit.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate are concrete.
- acceptance paths are testable through focused frontend tests, source scans, build, Reviewer, optional QA, and Integrator gates.
- non-goals explicitly exclude backend/API/schema, Workbench lifecycle behavior, lifecycle mutation controls in the registry, future scope, and unrelated residuals.

Planner gate: ready.

## 2. Product Contract

TASK_343C owns Projects list copy and route intent only.

The Projects list answers:

1. What state is this project in?
2. What should the operator do next?
3. Where should the operator go to do it?

It must not answer by adding lifecycle write controls. Stop, Resume, Close as completed, and Close administratively remain Workbench-owned actions.

## 3. State Copy Matrix

| State | Status copy | Next Step copy target | Row action copy target | Notes |
|---|---|---|---|---|
| Active formal/registered, Matrix needed | `Matrix Needed` or accepted active queue label | `Continue Matrix setup in Workbench` | `Open Workbench` | Matrix is the authority map. |
| Active formal/registered, folder created | `Folder Created` | `Continue setup in Workbench` | `Open Workbench` | Do not route to folder-only workflow. |
| Active temporary/no-LTR planning | `Planning` plus existing `Temporary Planning` badge | `Continue planning in Workbench` | `Open Workbench` | Completed close is not implied. |
| Stopped formal/registered | `Stopped` | `Resume or archive from Workbench` | `Open Workbench` | No registry Resume button. |
| Stopped temporary/no-LTR | `Stopped` with temporary identity context | `Resume or administratively archive from Workbench` | `Open Workbench` | No registry Close button. |
| Closed completed | `Closed: Completed` | `View readonly completed archive` | `Open archive` | No Resume or Close again. |
| Closed administrative | `Closed: Administrative` | `View readonly administrative archive` | `Open archive` | No Resume or close type conversion. |
| Closed legacy fallback | `Closed` | `View readonly archive` | `Open archive` | Keep business-readable fallback. |

Developer planning may adjust exact wording for consistency and width, but must keep these meanings.

## 4. Routing Contract

The current `onOpenProject(projectId)` path remains the default route into the Project Workbench unless Developer planning proves a pre-existing archive-specific route exists and is already accepted.

Allowed:

- change visible row action copy from generic `Open` to state-aware business copy, such as `Open Workbench` or `Open archive`.
- add accessible labels that include the project identifier and state.
- keep the same underlying route while clarifying copy.

Forbidden:

- direct calls to lifecycle mutation helpers from Projects registry code.
- new registry buttons or menus for `Stop project`, `Resume project`, `Close project`, `Close as completed`, or `Close administratively`.
- route targets that bypass the Workbench lifecycle action area for lifecycle changes.
- new backend/API routes or client functions.

## 5. File-Level Planning

Planner activation may update only governance/planning files:

- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- `docs/task_board.md`

After Reviewer plan gate pass, Developer planning-first may update only:

- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`

After explicit implementation approval, likely product files are:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css` only for small wrapping/accessible visual polish if needed

## 6. Validation Plan

Future Developer validation should include:

```powershell
npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx
npm run build
git diff --check -- frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.tsx frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md
rg -n "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle" frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css
```

Expected validation outcomes:

- focused tests pass for active, stopped, closed completed, closed administrative, temporary/no-LTR, matrix-needed, and folder-created copy.
- mutation-helper scan has no Projects registry or ProjectListPage matches.
- `frontend/src/api/client.ts`, backend, root tests, and Workbench implementation files remain unchanged.
- raw enum copy does not appear in operator-facing registry text.
- TASK_339B view categories remain intact.

## 6.1 Developer Planning-First Resolution

### Anti-Skip Confirmation

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current task/lane: `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT` / `projects-list-action-copy-routing-alignment`.

Current role: Developer planning-first.

Why allowed: Reviewer plan gate passed for TASK_343C with no blocking findings, and the user explicitly requested this Developer planning-first pass.

This pass is documentation/evidence only. It does not modify frontend product code, backend code, tests, frontend API client, Workbench behavior, Projects registry runtime behavior, board state, or git history.

### Read-Only Projects Registry Inspection

Current implementation facts:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts` already centralizes registry view classification, status labels, next-step labels, lifecycle badge class names, and compatibility fallbacks.
- `frontend/src/pages/ProjectListPage.tsx` already loads base rows through `listProjectRegistryRows()` and per-row lifecycle overlays through `getProjectLifecycle(project_id)`.
- `ProjectListPage` currently preserves TASK_339B views: `On-going`, `Planning`, `Closed`, and `All`.
- `ProjectListPage` currently renders a single row action button with visible copy `Open`, routed by `onOpenProject(row.project_id)`.
- A read-only mutation-helper scan found no `stopProjectLifecycle`, `resumeProjectLifecycle`, `closeProjectCompletedLifecycle`, or `closeProjectAdministrativeLifecycle` references in `frontend/src/features/projects-registry` or `frontend/src/pages/ProjectListPage.tsx`.
- No API/client change is needed. TASK_343C can use the already accepted base registry row data and lifecycle overlay data.

### Exact Implementation File List After Approval

Future implementation may touch only:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css` only if row action/next-step wrapping or accessible visual polish needs small registry-specific styling
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`

Locked for implementation:

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/`
- `frontend/src/features/project-lifecycle/`
- `frontend/src/workbench.css`
- TASK_343A/TASK_343B implementation files
- unrelated governance/orchestration residuals
- `docs/task_board.md`

### Copy And Routing Decisions

The Projects list remains routing-only. It may say where to go, but it must not perform lifecycle writes.

Future implementation should add display-only helper output for row action copy and accessible labels, for example `registryRowActionLabel(...)` and `registryRowActionAriaLabel(...)`, while keeping the underlying `onOpenProject(project_id)` route.

State-specific behavior:

| State | Status copy | Next Step copy | Row action copy | Route intent |
|---|---|---|---|---|
| Active formal/registered, Matrix needed | `Matrix Needed` | `Open Matrix authority` | `Open Workbench` | Workbench operational context |
| Active formal/registered, folder created | `Folder Created` | `Continue setup in Workbench` | `Open Workbench` | Workbench setup/Matrix context, not folder-only workflow |
| Active temporary/no-LTR planning | `Planning` plus existing temporary identity badge | `Continue planning in Workbench` | `Open Workbench` | Workbench planning context |
| Stopped formal/registered | `Stopped` | `Review or resume in Workbench` | `Open Workbench` | Workbench readonly/resume context |
| Stopped temporary/no-LTR | `Stopped` | `Resume or administratively archive from Workbench` | `Open Workbench` | Workbench readonly/resume/admin-close context |
| Closed completed | `Closed: Completed` | `View readonly completed archive` | `Open archive` | Workbench archive context |
| Closed administrative | `Closed: Administrative` | `View readonly administrative archive` | `Open archive` | Workbench archive context |
| Closed legacy fallback | `Closed` | `View readonly archive` | `Open archive` | Workbench archive context |

Copy rules:

- Keep labels business-readable and concise.
- Do not show raw backend tokens such as `closed_completed`, `closed_administrative`, `cancelled`, `lifecycle_state`, or `closure_type`.
- Do not expose future-scope language such as Report generation, StepInstance, AI, permissions, LAN/server, or multi-user.
- Do not add visible `Stop project`, `Resume project`, `Close project`, `Close as completed`, or `Close administratively` controls in the Projects list.

### TASK_343A / TASK_343B Preservation

- Stop/Resume remain Workbench-owned from TASK_343A.
- Close completed/admin confirmation flows remain Workbench-owned from TASK_343B.
- TASK_343C must not import, call, wrap, or re-label lifecycle mutation helpers from the registry.
- TASK_343C must not change Workbench selectors, Workbench model hooks, Workbench layout, close confirmation UI, or Workbench CSS.

### Focused Implementation Tests

Helper tests should cover:

- active registered/formal Matrix-needed row status, next-step, action label, and route intent.
- folder-created row keeps `Folder Created` status but routes operator to Workbench setup.
- active temporary/no-LTR row says planning and opens Workbench.
- stopped formal/registered row stays `On-going`, says `Stopped`, and points to Workbench resume/archive context.
- stopped temporary/no-LTR row stays `Planning`, says `Stopped`, and points to Workbench resume/admin archive context.
- closed completed row says `Closed: Completed`, next step `View readonly completed archive`, action `Open archive`.
- closed administrative row says `Closed: Administrative`, next step `View readonly administrative archive`, action `Open archive`.
- closed legacy fallback says `Closed`, next step `View readonly archive`, action `Open archive`.
- copy does not expose raw backend enum tokens or future-scope terms.

Component tests should cover:

- default `On-going` view still shows active operational rows.
- `Closed` view shows completed/admin/legacy archive rows with `Open archive`.
- `Planning` view shows temporary and stopped temporary rows with Workbench route intent.
- row action invokes the existing `onOpenProject(project_id)` callback.
- no Projects list Stop/Resume/Close/Delete lifecycle mutation buttons or menus render.
- lifecycle overlay failure keeps base rows visible with compatibility labels and no raw enum copy.

Recommended implementation validation:

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

Expected implementation validation results:

- focused registry tests pass.
- frontend build passes.
- mutation-helper scan has no matches.
- registry product copy has no lifecycle write action controls.
- future-scope scan has no product-code matches.
- backend, root tests, frontend API client, Workbench, lifecycle frontend model, Workbench CSS, and board remain unchanged by Developer implementation.

### Browser / QA Smoke Expectations

QA is optional unless Reviewer or Integrator requires it after implementation. If required, QA should cover:

- `/projects` default `On-going` view.
- closed completed/admin rows show archive intent and do not show Resume/Close controls.
- stopped rows show Workbench route intent and do not show direct Resume controls.
- temporary/no-LTR rows show planning route intent, not completed-close copy.
- keyboard focus reaches search, view selector, row action, and pagination in a predictable order.
- narrow width keeps row action copy readable without adding secondary mutation controls.

If browser tooling is unavailable, QA may record a non-blocking residual only after focused component tests, source scans, build, and Reviewer scope checks pass.

## 7. Reviewer Gate

Reviewer should block if:

- Projects list gains direct lifecycle mutation controls.
- plan permits backend/API/schema or Workbench behavior changes.
- TASK_343A/TASK_343B implementation can be changed by this lane.
- row action/routing copy conflicts with Workbench lifecycle authority.
- validation lacks a scan proving registry code does not call lifecycle mutation helpers.
- future scope appears.

## 8. QA Gate

QA is optional unless Reviewer or Integrator requires it after implementation.

If required, QA should cover:

- `/projects` default `On-going` view.
- stopped row shows Workbench route intent, not a direct Resume action.
- closed completed/admin row shows archive intent, not Resume or Close.
- temporary/no-LTR row points to Workbench setup/planning, not completed close.
- keyboard focus and narrow width do not make row actions ambiguous.

If browser tooling is unavailable, QA may record a non-blocking residual only if focused component tests, source scans, and build validation pass.

## 9. Merge Gate

Integrator may accept TASK_343C only after:

- Developer evidence records implementation and validation.
- Reviewer has no blocking findings.
- QA passes or records an accepted non-blocking residual if QA is required.
- package contains only approved TASK_343C task/plan/evidence, board updates, and approved Projects registry frontend files.
- no backend/API/schema/frontend API client, Workbench lifecycle behavior, TASK_343A/TASK_343B implementation, future scope, or unrelated governance residuals are included.

## 10. Unrelated Residuals

Existing dirty governance/orchestration residuals under `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*` are explicitly excluded from TASK_343C unless a separate governance lane owns them.

## 11. Stop Point

Stop after Integrator packaging/readiness acceptance and completion callback.

Recommended next role: User if the TASK_343 series is complete, or Planner only if another TASK_343 sublane is explicitly required.

Do not start backend changes, Workbench behavior changes, TASK_344 or later tasks, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, push, reset, delete, or unrelated cleanup.
