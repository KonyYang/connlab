# TASK_343A Workbench Lifecycle Actions UX Plan

Status: implementation complete - Integrator accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: workbench-lifecycle-actions-ux
Role: Frontend Developer planning-first
Last Updated: 2026-06-27

## 1. Discovery Gate

### Current State

Current active task/lane: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` / `workbench-lifecycle-actions-ux`.

Current role: Planner creating and activating the formal planning-first lane.

Why allowed: parent TASK_343 passed Reviewer plan gate, Reviewer accepted the B1 fix that withholds all Close controls from TASK_343A, and the user explicitly requested creation/activation of TASK_343A.

### User Goal Restatement

Create the first implementation lane for Workbench lifecycle action UX. The lane should cover Stop and Resume only, using existing lifecycle API and frontend readonly/shell foundations. It must not expose Close controls in any form, and it must not change backend/API/schema behavior. The first Developer handoff is planning-first only, so Developer must refine this plan and evidence before any product code is written.

### Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- TASK_337A plan/evidence
- TASK_338 plan/evidence
- TASK_339A plan/evidence
- TASK_340 plan
- TASK_341 plan/evidence
- read-only `rg` scan for frontend lifecycle client and Workbench files
- `$impeccable` product context already loaded in this session

### Confirmed By User

- Parent TASK_343 Reviewer plan gate passed.
- B1 was fixed and accepted: TASK_343A withholds all Close controls entirely.
- TASK_343A scope is Stop/Resume UX only.
- Do not start Developer implementation.
- Do not modify product code, backend, frontend, tests, or unrelated governance residuals during Planner activation.

### Confirmed By Repository Evidence

- `frontend/src/api/client.ts` already exports `stopProjectLifecycle(...)` and `resumeProjectLifecycle(...)`.
- TASK_337A defines lifecycle Stop/Resume endpoints and optional reason DTOs.
- TASK_338 and TASK_339A establish stopped/closed readonly behavior and write blocking.
- TASK_340 requires lifecycle-changing actions to use confirmation in implementation lanes.
- TASK_341 implemented the first shell slice and did not invent Resume/Close controls.
- Parent TASK_343 task/plan/evidence now state that TASK_343A must withhold all Close controls.
- Current worktree has unrelated governance/orchestration residuals that must not be packaged into product implementation scope.

### Inferred By Planner

- TASK_343A can stay frontend-only because the needed stop/resume client functions already exist.
- The likely implementation area is `frontend/src/features/project-workbench/`, with supporting readonly/action derivation in `frontend/src/features/project-lifecycle/`.
- `frontend/src/api/client.ts` should remain locked for TASK_343A because the needed client functions already exist.
- Developer planning-first should inspect current `ProjectLifecycleManagementPanel`, `ProjectWorkbenchLayout`, `ProjectWorkbenchLifecycleSections`, `projectWorkbenchShellModel`, `projectWorkbenchLifecycleSelectors`, and `useProjectWorkbenchModel` before proposing exact file changes.

### Not Yet Confirmed

- Exact component shape for confirmation UI. This is a Developer planning-first decision, but the contract requires guarded confirmation for lifecycle-changing Stop/Resume actions.
- Whether browser tooling will be available for QA. This is a QA-time residual-risk decision, not a blocker to lane activation.

### Planning Risk

Risks:

- Stop/Resume UX expands into Close UX despite Reviewer B1.
- Developer starts coding without first refining and getting approval for the implementation plan.
- Frontend action placement changes accidentally demote Matrix in the Active Matrix workspace.
- Existing stopped/closed readonly suppression regresses while adding Resume.

### Definition Of Ready

Satisfied for approved planning-first lane activation:

- user goal and scenario are clear
- parent TASK_343 passed Reviewer plan gate
- current board state and dependencies are verified
- existing stop/resume API client functions are present
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate are concrete
- acceptance paths are testable through focused frontend tests, build, Reviewer, QA, and Integrator gates
- non-goals explicitly exclude Close, backend/API/schema, future scope, and unrelated residuals

Planner gate: ready.

## 2. Objective

Implement, after Developer planning approval, a focused Workbench lifecycle action area for Stop and Resume only.

UX intent:

- Active operators can pause a project from the Workbench with clear confirmation and optional reason.
- Stopped operators see the readonly reason and can Resume from the Workbench with clear intentional action and optional reason.
- The Workbench refreshes lifecycle state after Stop/Resume without sending the operator to a separate stopped page.
- Matrix remains the authority workspace when active Matrix exists.
- Closed projects remain archive-only and do not show Resume or Close controls.

## 3. Scope Contract

### In Scope

- Workbench action model for Stop and Resume.
- Stop confirmation with optional reason.
- Resume intentional action pattern with optional reason.
- Loading/success/error state for Stop and Resume.
- Local lifecycle refresh after successful Stop/Resume.
- Business-readable action copy and disabled/read-only guidance.
- Focused tests for active, stopped, and closed states.
- QA smoke expectations for Active Matrix workspace and registered setup.

### Out Of Scope

- Close as completed.
- Close administratively.
- `Close project` button, placeholder, menu item, route target, reserved control, or non-functional affordance.
- Output status summary acknowledgement.
- Close note/reason fields.
- Post-close archive transition behavior.
- Close API calls.
- Backend/API/schema/write guard changes.
- Projects list copy/routing alignment.
- Report generation.
- StepInstance/execution persistence.
- AI, permissions, LAN/server, or multi-user scope.
- unrelated governance/orchestration residuals.

## 4. UX Contract

### Active Project

- Show `Stop project` only when lifecycle state is active and the action is allowed by current lifecycle data.
- Use a guarded confirmation pattern before sending Stop.
- Stop reason is optional.
- On submit, call existing `stopProjectLifecycle(projectId, { reason })`.
- On success, refresh lifecycle state and Workbench runtime model, then show stopped readonly state.
- Do not show any Close control.

### Stopped Project

- Show readonly reason using existing TASK_339A/TASK_341 readonly copy.
- Show `Resume project` as the primary lifecycle action only when lifecycle state is stopped and action is allowed.
- Resume reason is optional.
- Resume must be an intentional action. Developer planning may choose a compact confirmation, inline confirm, or direct action with clear label and loading state, but must justify the choice.
- On submit, call existing `resumeProjectLifecycle(projectId, { reason })`.
- On success, refresh lifecycle state and Workbench runtime model, then restore active project progression.
- Do not show any Close control.

### Closed Completed / Closed Administrative

- Do not show Stop.
- Do not show Resume.
- Do not show Close.
- Keep readonly archive shell behavior from TASK_341.

### Active Matrix Workspace

- Matrix stays visually and structurally primary.
- Lifecycle action area must be compact and subordinate to Project State, not a competing work surface.
- Stop action must not displace Matrix controls or Outputs rail hierarchy.

### Registered Setup / Temporary Planning

- Registered setup may show Stop when active.
- Temporary planning may show Stop when active.
- Neither state may show Close controls in TASK_343A.

## 5. Developer Planning-First Requirements

Before coding, Developer must update this plan and evidence with:

- exact files to change
- current component/hook inspection summary
- chosen Stop confirmation pattern
- chosen Resume intentional action pattern
- exact data refresh path after Stop/Resume
- exact no-Close enforcement strategy
- focused test list and expected assertions
- QA smoke list
- any implementation risk or blocker

Developer must then stop for user approval. No product code may be changed in the planning-first pass.

## 6. May Touch

Planner activation may touch:

- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- `docs/task_board.md`

Developer planning-first may touch:

- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`

Implementation may touch only after explicit user approval of the Developer planning pass, likely:

- `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`

## 7. Must Not Touch

- `backend/`
- backend API contracts, DTOs, routes, services, schema, migrations, or write guards
- `frontend/src/api/client.ts`
- root `tests/`
- Projects registry implementation
- TASK_343B/TASK_343C files unless separately approved
- any Close controls or Close flows
- Matrix/Fee/Folder/Basic Information/LTR/Required Forms/Public Drive business rules
- Report generation
- StepInstance/execution persistence
- AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residuals

## 8. Locked Paths

- `backend/`
- `tests/`
- `frontend/src/api/client.ts`
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- parent TASK_343 task/plan/evidence files for Developer/QA/product implementation changes
- TASK_336 through TASK_342 task/plan/evidence files, except read-only reference

Planner cleanup note, 2026-06-27: Integrator may include parent TASK_343 task/plan/evidence files as Planner-owned prerequisite/source-consistency inputs when packaging TASK_343A with `docs/task_board.md`. This is not a Developer/QA/product implementation allowance and does not authorize Close controls, TASK_343B/TASK_343C, backend/API/schema changes, or unrelated governance/orchestration residuals.

## 9. Validation Plan

Developer planning must refine exact commands, but the expected validation floor is:

```powershell
cd frontend
npm test -- --run src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts
npm run build
```

Expected assertions:

- active registered setup shows Stop and no Close controls
- active temporary planning shows Stop and no Close controls
- active Matrix workspace shows lifecycle action area without demoting Matrix
- Stop confirmation accepts blank optional reason
- Stop success refreshes lifecycle and renders stopped readonly state
- stopped state shows readonly reason and Resume
- Resume success refreshes lifecycle and renders active progression
- stopped readonly write controls remain blocked/suppressed
- closed completed/admin states show no Stop, no Resume, and no Close controls
- no close API function is called by TASK_343A code paths

QA smoke expectations:

- Active Matrix workspace: Matrix remains primary; Stop is reachable; no Close control appears.
- Registered setup: Matrix setup remains primary; Stop is reachable; no Close control appears.
- Stopped state: readonly reason and Resume are visible; write controls stay blocked.
- Closed completed/admin states: no Stop, Resume, or Close controls.
- Narrow viewport: lifecycle action area wraps without overlapping Project State, Matrix, or Outputs.
- Keyboard order reaches header, lifecycle action area, banner, Matrix/primary workspace, and Outputs in a logical order.

## 10. Reviewer / QA / Merge Gates

Reviewer gate is required after implementation.

Reviewer must block if:

- TASK_343A adds any Close control or close API call
- backend/API/schema/write guards are changed
- Matrix ceases to be primary in Active Matrix workspace
- stopped/closed readonly behavior regresses
- Developer skipped planning-first approval
- future scope is exposed

QA gate is required after Reviewer pass.

Integrator may accept only after Reviewer and QA gates pass, product implementation package scope is clean, parent TASK_343 source files are included only as Planner-owned prerequisite/source-consistency inputs or otherwise waived by Planner without unresolved board references, and no unrelated residuals or TASK_343B/TASK_343C work are mixed in.

## 11. Developer Planning-First Resolution

### Anti-Skip Confirmation

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` / `workbench-lifecycle-actions-ux`.

Allowed reason: `docs/task_board.md` marks TASK_343A as approved for Frontend Developer planning-first only, and the user explicitly requested this Developer planning pass. This pass updates only this plan and the TASK_343A developer evidence. No product code is authorized until this planning pass is reviewed and explicitly approved.

### Code Inspection Summary

Relevant current frontend facts:

- `frontend/src/api/client.ts` already exports `ProjectLifecycleResponse`, `ProjectLifecycleActionRequest`, `getProjectLifecycle(...)`, `stopProjectLifecycle(...)`, and `resumeProjectLifecycle(...)`. It also exports close lifecycle helpers, but those remain locked for TASK_343A.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` currently imports and calls the legacy `stopProject(...)` helper, uses browser `prompt` and `confirm`, then calls `onBack()` after Stop. TASK_343A implementation should replace that path with the accepted lifecycle API helpers and keep the operator in the Workbench.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` already exposes `onRefreshLifecycle()`, but that refresh currently reloads lifecycle data only. Resume can leave `project.status` stale as legacy `cancelled` unless the implementation also refreshes the project identity/status after Stop/Resume.
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` owns the existing `ProjectLifecycleManagementPanel`, which renders Stop but has no Resume path and no allowed-action gate.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts` owns stage and tab derivation. It should also own display-only lifecycle action availability so JSX does not scatter `allowed_actions` checks.
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts` already derives stopped/closed readonly state and exposes `canResume`; no backend DTO or API-client change is needed.
- Active Matrix workspace currently keeps Matrix primary, but its command/action area does not provide a stable Stop affordance. TASK_343A should add a compact lifecycle action area without competing with Matrix.

### Exact Implementation File List

After user approval, TASK_343A implementation may touch only:

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`

Do not touch `frontend/src/api/client.ts`; the required client functions already exist. Do not touch backend, root tests, Projects registry files, parent TASK_343 files, TASK_343B/TASK_343C files, or TASK_336 through TASK_342 files during Developer product implementation. Parent TASK_343 files may be included later by Integrator only as Planner-owned prerequisite/source-consistency inputs.

### API And DTO Usage

Use only existing frontend API client exports:

- `stopProjectLifecycle(projectId, { reason, operator: null })`
- `resumeProjectLifecycle(projectId, { reason, operator: null })`
- `ProjectLifecycleResponse.allowed_actions`
- `ProjectLifecycleResponse.lifecycle_state`
- `ProjectLifecycleResponse.readonly`
- `ProjectLifecycleResponse.stopped_reason`

Do not import or call:

- `closeProjectCompletedLifecycle(...)`
- `closeProjectAdministrativeLifecycle(...)`

Do not add frontend API DTOs, backend DTOs, routes, schema fields, migrations, or write-guard behavior.

### Lifecycle Action Model

Add a small display-only helper in `projectWorkbenchLifecycleSelectors.ts`, for example `deriveProjectWorkbenchLifecycleActions(...)`.

The helper should derive:

- `canStop`: true only when lifecycle exists, `lifecycle_state === "active"`, `readonly === false`, and `allowed_actions` includes `stop`.
- `canResume`: true only when lifecycle state is stopped or the readonly view is stopped, and `allowed_actions` includes `resume`.
- `readonlyReason`: stopped/closed business-readable reason from the readonly model.
- `primaryAction`: `stop`, `resume`, or `none`.
- No `close` action output in TASK_343A, even when `allowed_actions` includes `close`.

If lifecycle data is temporarily unavailable, do not guess. Hide Stop/Resume and keep current read surfaces visible.

### Stop UX Pattern

Use a compact inline confirmation panel, not `window.prompt`, not `window.confirm`, and not a modal as the first implementation.

Recommended flow:

1. Show `Stop project` only when `canStop` is true.
2. Clicking `Stop project` opens an inline confirmation area in the lifecycle action panel.
3. The confirmation area shows concise copy: stopping pauses the project and keeps it available for review.
4. Provide an optional `Reason` textarea or compact input.
5. Provide `Confirm stop project` and `Cancel`.
6. Submit calls `stopProjectLifecycle(projectId, { reason: trimmedReason || null, operator: null })`.
7. Disable the action while pending and show a business-readable error on failure.
8. On success, refresh Workbench lifecycle and project identity/status, clear local reason/confirmation state, and keep the operator in the Workbench.

### Resume UX Pattern

Use the same compact inline intentional action pattern.

Recommended flow:

1. Stopped project shows the existing readonly reason.
2. Show `Resume project` only when `canResume` is true.
3. Clicking `Resume project` opens an inline confirmation area.
4. The confirmation area states that editing and project work continue after resume.
5. Provide an optional `Reason` textarea or compact input.
6. Provide `Confirm resume project` and `Cancel`.
7. Submit calls `resumeProjectLifecycle(projectId, { reason: trimmedReason || null, operator: null })`.
8. Disable the action while pending and show a business-readable error on failure.
9. On success, refresh lifecycle and project identity/status so legacy `Project.status='cancelled'` compatibility does not leave the Workbench in a stale stopped branch.

### Refresh Path

Update the Workbench model rather than routing away from the page.

Implementation should add or adjust model-level lifecycle action handlers in `useProjectWorkbenchModel.ts`:

- `onStopLifecycle(reason?: string | null): Promise<void>`
- `onResumeLifecycle(reason?: string | null): Promise<void>`

Each handler should:

- call the existing lifecycle client action
- store the returned lifecycle response immediately
- refresh `getProject(projectId)` to update compatibility `Project.status`
- clear `lifecycleError` on success
- leave Matrix, previews, and output panels in place

`onRefreshLifecycle()` may be expanded to refresh both lifecycle and project status, or a private helper may do that work. If the implementation chooses a private helper, expose only the minimal callbacks needed through `ProjectRuntimeConsoleModel`.

### No-Close Enforcement

TASK_343A implementation must not render, disable, reserve, import, or route any Close control.

Specific enforcement points:

- Do not show `Close project`, `Close as completed`, or `Close administratively`.
- Do not add disabled Close placeholders or menu items.
- Do not add close note, administrative reason, output summary acknowledgement, completed close summary, or close confirmation UI.
- Do not call close lifecycle client functions.
- If `allowed_actions` includes `close`, ignore it in TASK_343A and leave it for TASK_343B.

### State Coverage Required In Implementation Tests

Add or update focused tests covering:

- Active temporary planning with `allowed_actions=["stop", "close"]`: Stop visible, no Close text/control, Delete temporary behavior preserved.
- Active registered setup without active Matrix: Stop visible only when `allowed_actions` includes `stop`; no Close text/control.
- Active registered setup without `stop` in `allowed_actions`: Stop hidden or unavailable with no guessed action.
- Active Matrix workspace: Matrix remains before Outputs and primary workspace content remains visible; compact Stop action is reachable and does not displace Matrix controls.
- Stop confirmation accepts blank optional reason and calls `stopProjectLifecycle` with `reason: null`.
- Stop success refreshes lifecycle and project status through the Workbench model and does not call `onBack()`.
- Stopped readonly with `allowed_actions=["resume", "close"]`: readonly reason and Resume are visible; Stop and Close are not.
- Resume confirmation accepts blank optional reason and calls `resumeProjectLifecycle` with `reason: null`.
- Resume success refreshes lifecycle and project status, restoring active progression instead of staying in legacy cancelled state.
- Closed completed and closed administrative: no Stop, no Resume, no Close controls.
- Stopped readonly write controls remain blocked/suppressed through existing TASK_339A behavior.

### Validation Commands For Implementation Pass

Run from `frontend/`:

```powershell
npm test -- --run src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/useProjectWorkbenchModel.test.tsx src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
npm run build
```

Then run from repository root:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
git status --short -- backend tests frontend/src/api/client.ts docs/task_board.md tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md
```

Static no-Close review:

```powershell
rg -n "closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|Close project|Close as completed|Close administratively|output_summary_acknowledged|close_note" frontend/src/features/project-workbench frontend/src/workbench.css
```

Any matches must be justified as pre-existing tests or explicit negative assertions; production TASK_343A code must not render or call Close.

### Browser / Manual QA Smoke Expectations

QA is required after Reviewer pass because this changes the main Workbench operator flow.

QA should cover:

- Active Matrix workspace: Matrix remains primary; Stop is reachable in a compact lifecycle action area; no Close control appears.
- Registered setup: Matrix setup remains primary; Stop appears only when lifecycle `allowed_actions` includes `stop`.
- Temporary planning: Stop appears when allowed; existing temporary delete behavior is not widened by TASK_343A.
- Stopped state: readonly reason is visible; Resume is reachable when allowed; write controls stay blocked.
- Closed completed/admin: no Stop, Resume, or Close controls.
- Narrow viewport: lifecycle action panel wraps without overlapping Project State, Matrix, or Outputs.
- Keyboard order: header, lifecycle action area, lifecycle banner, Matrix/primary workspace, Outputs.

If browser tooling is unavailable, QA must record a residual-risk disposition and rely on focused component/static/CSS evidence only if all automated tests and build pass.

## 12. Planning-First Validation

Planning pass validation:

```powershell
Test-Path docs\task_343a_workbench_lifecycle_actions_ux_plan.md
Test-Path docs\lane_evidence\TASK_343A_workbench-lifecycle-actions-ux_developer.md
git diff --check -- docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
rg -n "[ \t]$" docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
git status --short -- frontend backend tests docs/task_board.md docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md
```

Expected planning-pass scope:

- Only `docs/task_343a_workbench_lifecycle_actions_ux_plan.md` and `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md` are edited by Developer.
- `docs/task_board.md` and the TASK_343A task file may already be dirty from Planner activation, but Developer must not edit them in this pass.
- No `frontend/`, `backend/`, or root `tests/` files change.

## 13. Current Stop Point

Stop after Integrator packaging/readiness acceptance and completion callback.

Developer planning gate: complete. Implementation, Reviewer re-gate, QA gate, and Integrator packaging/readiness completed on 2026-06-27.

Do not start TASK_343B or TASK_343C, do not push remote, and do not perform unrelated governance cleanup from this lane.
