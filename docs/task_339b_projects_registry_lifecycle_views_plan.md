# TASK_339B Projects Registry Lifecycle Views Planner Discovery

Last Updated: 2026-06-27
Status: implementation complete - Integrator accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: projects-registry-lifecycle-views
Role: Frontend Developer planning-first

## 1. Discovery Gate

### Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

### Current Active Task/Lane

No active implementation lane. `TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL` is complete and accepted.

### Current Role

Planner.

### Why Planner Is Allowed

The user explicitly asked Planner to create or activate the next formal planning-first lane for `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS` after TASK_339A acceptance. Planner may update governance/planning files only and must not write product code.

## 2. User Goal Restatement

Create the next lifecycle/workbench series lane for Projects registry lifecycle views.

The lane should be formal and planning-first, with May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, Merge Gate, and Reviewer/QA/Integrator gates defined.

The lane must stay limited to Projects registry lifecycle views and must not implement Workbench shell, TASK_341, TASK_342, backend guard changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.

The user also required Planner to read TASK_340 task and plan as series background only, not to re-implement TASK_340.

## 3. Evidence Read

Read successfully:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- `$impeccable` product context from `PRODUCT.md` and `DESIGN.md`
- current Projects registry frontend entry `frontend/src/pages/ProjectListPage.tsx`
- current frontend lifecycle DTO/helper references through read-only search

Initially missing from the current worktree, then restored by Planner from `stash@{0}^3` on 2026-06-27:

- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`

## 4. Confirmed By User

- Create or activate a formal planning-first lane for `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS`.
- Run Discovery Gate and Definition of Ready first.
- Do not skip requirements confirmation.
- Only handle TASK_339B in this turn.
- TASK_339B boundary is Projects registry lifecycle views only.
- Do not implement Workbench shell, TASK_341, TASK_342, backend guard changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, or multi-user scope.
- Allowed file changes are governance/planning docs only for this Planner lane.

## 5. Confirmed By Repository Evidence

- `docs/task_board.md` reports no active implementation lane.
- `docs/task_board.md` reports TASK_339A complete and accepted after Reviewer pass and Integrator packaging/readiness gate.
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md` records `Integrator gate: accepted`.
- Latest local commit is `74dd366 feat(frontend): complete TASK_339A readonly model`.
- TASK_339B task, plan, and evidence files did not exist before this Planner turn.
- TASK_341 and TASK_342 formal task files do not exist.
- Existing Projects registry entry is `frontend/src/pages/ProjectListPage.tsx`.
- TASK_339A added lifecycle API types/client helpers and `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`, which TASK_339B can consume after activation.
- Board declares TASK_340 complete/accepted.
- TASK_340 task, plan, and evidence files were restored from the reliable stash source `stash@{0}^3` without applying unrelated stash files.

## 6. Inferred By Planner

- TASK_339B should be a frontend-only registry visibility lane that uses already accepted lifecycle semantics.
- TASK_339B should not introduce lifecycle write actions from the registry in its first slice.
- TASK_339B should make stopped and closed projects findable without crowding the active operational queue.
- TASK_339B likely needs to update `ProjectListPage.tsx`, registry helper logic, registry tests, and possibly CSS.
- If registry DTOs already expose lifecycle fields, no backend work is needed. If they do not, backend DTO changes must become a separate contract/backend lane or an explicitly approved scope change.

## 7. Not Yet Confirmed

- Whether Projects registry lifecycle views should use only current registry DTO fields or wait for a backend registry summary enhancement if lifecycle fields are missing.
- Whether closed projects should appear in a separate Archived view or inside the existing `Completed`/`All` views only.

## 8. Planning Risk

The main product risk is over-expanding a registry visibility task into Projects registry redesign, backend DTO work, or Workbench shell IA. Another risk is hiding closed projects too deeply or crowding the active work queue with archived rows.

## 9. Definition Of Ready

Current status: satisfied for approved planning-first lane activation.

Satisfied:

- User goal is narrow enough for a formal approved planning-first lane.
- Current board state and TASK_339A dependency are verified.
- Existing registry entry point is identified.
- May Touch, Must Not Touch, Locked Paths, evidence, validation, and merge gates can be defined.
- Non-goals are explicit.
- TASK_340 source mismatch has been closed by restoring the missing task/plan/evidence files from `stash@{0}^3`.

Still to resolve during Developer planning before frontend code:

- The registry lifecycle data source should be confirmed during Developer planning before any code implementation.

## 10. Decision

Activate TASK_339B as a formal `approved` planning-first lane.

Route only to Frontend Developer planning first. Developer must review/update this plan and stop for user approval before frontend product code changes.

## 11. Proposed Implementation Scope After Activation

May touch after activation and explicit plan approval:

- `frontend/src/pages/ProjectListPage.tsx`
- frontend registry helper/test files explicitly listed in the approved TASK_339B plan
- `frontend/src/api/client.ts` only for typed consumption of already-available registry lifecycle fields explicitly listed in the approved plan
- frontend CSS files explicitly listed in the approved plan for registry lifecycle badges/views
- focused frontend tests explicitly listed in the approved plan
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`

Must not touch:

- frontend product code before lane activation and plan approval
- backend implementation
- TASK_338 backend write guards
- Unified Workbench Shell implementation
- Project Workbench shell layout or navigation IA
- Office gateway internals
- Matrix/Fee business rules
- Project Folder backend behavior
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- public-drive authority replacement
- unrelated governance/orchestration residual files

Locked paths:

- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`
- frontend registry files explicitly listed in the approved TASK_339B plan

Validation gate:

- plan approved by user before frontend product code changes
- active/stopped/closed completed/closed administrative registry views covered
- registry copy uses business labels and does not expose raw enum names
- default registry view remains operational for active work
- archived closed projects remain findable without crowding the active work queue
- focused frontend tests pass
- frontend build passes

Merge gate:

- Reviewer pass required
- QA required if the approved plan calls for browser/manual smoke or if registry filtering cannot be covered by component tests alone
- Integrator gate required before global board completion
- Merge blocked if backend code, Workbench shell, TASK_341/TASK_342, lifecycle write actions, or future scope are mixed in

## 12. Open Planning Questions For Developer Plan

1. Should TASK_339B remain strictly frontend-only using current registry DTO fields, or should Developer propose a separate backend DTO follow-up if lifecycle fields are insufficient?
2. For the registry operator workflow, should closed projects live in a dedicated `Archived` view, or should the first slice keep them findable through existing `Completed` and `All` views only?

## 13. Frontend Developer Planning Resolution

### Anti-Skip Statement

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current approved lane: `projects-registry-lifecycle-views` / `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS`.

Allowed role in this pass: Frontend Developer planning first.

This pass does not authorize frontend product code. Frontend implementation remains blocked until the user explicitly approves this updated plan.

### Read-Only Reconnaissance Findings

Current registry entry:

- `frontend/src/pages/ProjectListPage.tsx`

Current registry data source:

- `listProjectRegistryRows()` in `frontend/src/api/client.ts`
- `ProjectRegistryRow` currently includes project identity, registered LTR marker, compatibility `status`, progress, notes, and temporary project fields.
- `ProjectRegistryRow` does not currently expose `lifecycle_state`, `closure_type`, `stopped_at`, or `closed_at`.

Current lifecycle frontend source from TASK_339A:

- `ProjectLifecycleResponse`
- `getProjectLifecycle(projectId)`
- `deriveProjectLifecycleReadonlyView(...)`

Current registry behavior to replace:

- `ProjectListPage.tsx` uses `status === "cancelled"` to label `Stopped`.
- `rowsForView(...)` currently places `status === "cancelled"` rows in the `completed` view.
- The view key is currently `completed`, with user label `Completed`.

### Data Source Decision

TASK_339B implementation should remain frontend-only by using the accepted TASK_339A lifecycle API:

1. Load base registry rows with `listProjectRegistryRows()`.
2. Load lifecycle overlays for registry rows with existing `getProjectLifecycle(project_id)`.
3. Classify rows from lifecycle overlay first.
4. Use compatibility `status` only as fallback while lifecycle overlay is loading or unavailable.

No backend DTO change is planned in this lane. If per-row lifecycle fetching becomes too slow or unreliable for real registry volumes, create a later backend/API registry lifecycle summary task rather than expanding TASK_339B.

### Registry View Contract

Use these views:

- `On-going`
- `Planning`
- `Closed`
- `All`

Default view:

- `On-going`

Classification:

- `Closed`: lifecycle state `closed`, including `Closed: Completed` and `Closed: Administrative`.
- `On-going`: lifecycle state `active` or `stopped` with registered LTR or formal project identity.
- `Planning`: lifecycle state `active` or `stopped` without registered LTR/formal identity.
- `All`: all visible projects.

Compatibility fallback only when lifecycle overlay is unavailable:

- `status === "cancelled"` maps to `Stopped` and remains in `On-going` or `Planning` based on registered/formal identity, not `Closed`.
- `status === "closed"` maps to closed archive with unknown closure type.
- `status === "folder_created"` remains an operational status, not a lifecycle close signal.

### Registry Copy Contract

Row lifecycle labels:

- `Active`
- `Stopped`
- `Closed: Completed`
- `Closed: Administrative`
- `Closed`

Row next-step copy:

- Active planning row: `Continue planning`
- Active formal row without Matrix authority signal: `Open Matrix authority`
- Stopped row: `Review or resume in Workbench`
- Closed completed row: `Open completed archive`
- Closed administrative row: `Open administrative archive`

Do not render backend enum tokens such as `closed_completed`, `closed_administrative`, `cancelled`, `lifecycle_state`, or `closure_type` as user-facing copy.

TASK_339B must not add Stop, Resume, Close, Delete, or lifecycle write actions from the registry. The row action remains read/navigation oriented, e.g. `Open`.

### Implementation File Plan After Explicit Approval

Create:

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
  - Pure classification, label, next-step, and view filtering helpers.

- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
  - Pure tests for lifecycle classification, labels, fallback behavior, and raw enum copy prevention.

- `frontend/src/pages/ProjectListPage.test.tsx`
  - Component tests with mocked registry rows and lifecycle overlays.

Modify:

- `frontend/src/pages/ProjectListPage.tsx`
  - Move registry lifecycle classification out of page-local helpers into `features/projects-registry`.
  - Load lifecycle overlays with `getProjectLifecycle(project_id)`.
  - Replace `Completed` view with `Closed`.
  - Keep default `On-going` and session-storage normalization.
  - Keep row action as `Open`.

- `frontend/src/project-dashboard.css`
  - Add minimal registry lifecycle badge/view styling only if existing table classes cannot express the states clearly.

Do not modify:

- `frontend/src/api/client.ts`, unless implementation discovers a type-only export/import adjustment is required for already-existing `ProjectLifecycleResponse` or `getProjectLifecycle`.
- Backend files.
- Tests outside the explicit TASK_339B frontend test files.
- TASK_340 shell files.

### Focused Test Plan

Pure selector tests:

- active temporary/no-LTR project classifies as `Planning`
- active registered/formal project classifies as `On-going`
- stopped temporary/no-LTR project remains in `Planning`
- stopped registered/formal project remains in `On-going`
- closed completed project classifies as `Closed` with `Closed: Completed`
- closed administrative project classifies as `Closed` with `Closed: Administrative`
- legacy `cancelled` fallback maps to `Stopped` but not `Closed`
- user-facing labels do not expose raw enum tokens

Component tests:

- default view is `On-going`
- `Closed` view contains closed completed and closed administrative rows
- `Planning` view includes stopped temporary rows
- `On-going` view includes stopped registered rows
- row action remains `Open`; no Stop/Resume/Close action appears
- lifecycle overlay load failure shows business-readable guidance and keeps base registry rows visible with compatibility labels

Validation after implementation:

```powershell
cd frontend
npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx
npm run build
```

Whitespace/scope checks:

```powershell
git diff --check -- frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md
git status --short -- backend docs/task_board.md tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md docs/task_340_unified_project_workbench_shell_plan.md docs/lane_evidence/TASK_340_unified-shell-plan_planner.md
```

Expected:

- focused tests pass
- frontend build passes
- no backend files changed
- `docs/task_board.md` unchanged by Developer implementation
- TASK_340 files unchanged by Developer implementation

### Risks And Mitigations

Risk: per-row lifecycle overlay fetch creates extra API calls.

Mitigation: keep the implementation simple for this first registry view slice, use the existing accepted endpoint, and record a separate backend/API summary follow-up if real registry volume needs batching.

Risk: lifecycle overlay fetch fails and hides projects.

Mitigation: keep base registry rows visible, show a business-readable lifecycle status warning, and fall back to compatibility labels without presenting closed completed/administrative certainty.

Risk: registry work expands into Projects redesign.

Mitigation: keep the existing table, toolbar, search, sorting, pagination, and `Open` row action. Only lifecycle views, labels, and badges change.

Risk: registry exposes lifecycle write actions.

Mitigation: TASK_339B forbids registry Stop/Resume/Close actions. Lifecycle changes stay in Workbench/lifecycle surfaces approved by other lanes.

## 14. Stop Point

TASK_339B implementation is complete and accepted.

Reviewer implementation gate passed. QA was not required because the approved registry filtering, copy, and no-write-action behavior is covered by focused helper/component tests. Integrator packaging/readiness gate accepted the package on 2026-06-27.

Stop here. Do not start TASK_341, TASK_342, Workbench shell implementation, or Projects registry redesign beyond lifecycle views until Planner/Integrator creates or activates a separate approved lane.
