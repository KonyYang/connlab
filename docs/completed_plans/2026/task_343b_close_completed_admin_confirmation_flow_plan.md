# TASK_343B Close Completed/Admin Confirmation Flow Plan

Status: implementation complete - Integrator accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: workbench-close-completed-admin-ux
Role: Developer planning-first
Last Updated: 2026-06-27

## 1. Discovery Gate

### Current State

Current active task/lane: no active implementation lane. `docs/task_board.md` marks `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` complete and accepted after Developer, Reviewer, QA, and Integrator gates.

Current role: Planner/Designer.

Why Planner is allowed: the accepted parent TASK_343 split explicitly reserves close completed/admin confirmation flow for TASK_343B, TASK_343A completed Stop/Resume and withheld every Close control, and the user explicitly requested TASK_343B formal planning-first lane creation/activation.

This pass is planning only. It does not implement frontend UI, backend behavior, tests, database changes, API changes, runtime routing, lifecycle writes, or registry code.

### User Goal Restatement

TASK_343B should add the missing Workbench close UX contract after Stop/Resume landed in TASK_343A. Close as completed must be a manual v1 flow because ConnLab has no StepInstance execution authority yet: it shows current output status summary, requires a close note and explicit acknowledgement, then archives the project as completed. Close administratively must require an explicit reason and archive the project without implying testing completion. Closed projects remain readonly archives and cannot Resume. This lane must not reopen TASK_343A implementation, change backend/API by default, or start TASK_343C registry alignment.

### Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context from `PRODUCT.md` and `DESIGN.md`
- `$impeccable` product register reference
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- TASK_336 task and contract plan
- TASK_337A task, plan, and developer evidence
- TASK_338 plan and developer evidence
- TASK_339A plan and developer evidence
- TASK_340 task and plan
- TASK_341 task, plan, and developer evidence
- TASK_342 task and plan
- parent TASK_343 task, plan, and Planner evidence
- TASK_343A task, plan, developer evidence, and QA evidence
- read-only API/client snippets for existing close DTOs and helpers

### Confirmed By User

- `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` is Integrator accepted in local commit `27de54907f9f46f8c15669822328b49f07059969`.
- TASK_343A Stop/Resume must not be reimplemented.
- TASK_343B product goal is Close as completed / Close administratively UX.
- Current stage has no StepInstance, so Close as completed v1 uses manual confirmation, current output status summary, required close note, and confirmation.
- Close administratively requires explicit confirmation/reason/note and results in readonly archive.
- This Planner pass must not modify product code, merge, commit, push, reset, delete, or clean unrelated residuals.

### Confirmed By Repository Evidence

- `docs/task_board.md` marks TASK_343A complete/accepted and proposes TASK_343B only through formal Discovery Gate and approved lane.
- Parent TASK_343 split names `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW` as the second implementation lane.
- TASK_343A task/plan/evidence confirm no Close controls, close dialogs, output summary acknowledgement, close note/reason fields, or close API calls were added.
- TASK_336 contract fixes close semantics:
  - completed close v1 defaults to formal/registered projects.
  - temporary/no-LTR planning projects default to administrative close.
  - completed close note is required.
  - administrative close reason is required.
  - closed projects are readonly archives and cannot Resume.
  - no StepInstance means ConnLab must not claim automatic testing completion.
- TASK_337A implemented backend routes:
  - `POST /api/projects/{project_id}/lifecycle/close-completed`
  - `POST /api/projects/{project_id}/lifecycle/close-administrative`
- `frontend/src/api/client.ts` already exports:
  - `closeProjectCompletedLifecycle(projectId, input)`
  - `closeProjectAdministrativeLifecycle(projectId, input)`
- Existing frontend DTOs include:
  - `ProjectLifecycleCloseCompletedRequest` with `close_note`, `manual_completion_confirmed`, and `output_summary_acknowledged`
  - `ProjectLifecycleCloseAdministrativeRequest` with required `reason`
  - `ProjectLifecycleResponse.completion_summary`
  - `ProjectLifecycleResponse.allowed_actions`
- TASK_338/TASK_339A/TASK_341 establish stopped/closed readonly behavior and non-mutating read/preview preservation.
- TASK_340 shell plan requires lifecycle state to be visible, Matrix to remain primary, and closed archive states to expose no Resume.
- Remaining dirty workspace paths before this Planner pass are unrelated governance/orchestration residuals only: `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*`.

### Inferred By Planner

- TASK_343B can remain frontend-only by default because backend endpoints and frontend API helpers already exist.
- Developer planning should verify whether `ProjectLifecycleResponse.completion_summary` already contains enough current output status summary for the dialog. If not, the lane must stop and request a separate approved API/backend scope change instead of improvising backend behavior.
- The likely implementation area is `frontend/src/features/project-workbench/`, reusing the TASK_343A lifecycle action area and Workbench model refresh pattern.
- `frontend/src/api/client.ts` should stay locked because the needed client helpers already exist.
- QA should be required because closing archives a project and changes the main Workbench state.

### Not Yet Confirmed

- Exact UI component decomposition for the close confirmation surface.
- Whether implementation should use a modal dialog, inline disclosure, or dedicated confirmation panel. Product guidance discourages modals as a first thought, so Developer planning must justify the chosen pattern.
- Whether browser tooling will be available for QA. If unavailable, QA must record a residual-risk disposition after focused tests/build/source scans.

These unknowns do not block creating the formal planning lane because they can be resolved in Reviewer plan gate or Developer planning-first without changing scope boundaries.

### Planning Risk

- Close UX could become a broad Workbench rewrite instead of a focused lifecycle action flow.
- Completed close might be exposed for temporary/no-LTR projects, violating TASK_336/TASK_337A.
- The UI might imply ConnLab has verified test completion automatically even though StepInstance does not exist.
- Developer could modify backend/API/schema despite existing close API readiness.
- TASK_343C registry copy/routing alignment could be mixed into close UX.

### Continue Decision

Definition of Ready is satisfied for TASK_343B planning-first activation:

- user goal and operator scenario are clear.
- current board state and dependencies are verified.
- existing close backend routes and frontend client helpers are confirmed.
- task/lane has formal task, plan, evidence, and board updates.
- dependencies and serialization constraints are explicit.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, and Merge Gate are concrete.
- acceptance paths are testable through focused frontend tests, build, Reviewer, QA, and Integrator gates.
- non-goals explicitly exclude backend/API/schema, TASK_343A reimplementation, TASK_343C, StepInstance, Report, AI, permissions, LAN/server, multi-user, and unrelated residuals.

Planner gate: ready.

## 2. Scope Contract

TASK_343B owns only Workbench close completed/admin UX.

It may introduce functional Close project controls only when the current lifecycle response indicates close is allowed. It must not add non-functional placeholders.

It must use current ConnLab product tone:

- state before action.
- Matrix remains primary when active.
- close actions are deliberate and business-readable.
- user-facing copy must not expose backend enum names.
- no decorative UI, side stripes, gradient text, glassmorphism, or future-feature showcase.

## 3. State Rules

| Workbench state | TASK_343B close behavior |
|---|---|
| Active formal/registered with active Matrix | Close controls may be reachable from the lifecycle action area but must remain visually secondary to Matrix. Completed close may be offered only with confirmation and output summary. Administrative close may be offered as the explicit non-completion path. |
| Active formal/registered setup without active Matrix | Completed close may be available only if backend `allowed_actions` permits close and the UI can show output summary. Copy must not imply Matrix/test execution is complete. Administrative close remains available when allowed. |
| Active temporary/no-LTR planning | Completed close must be hidden or blocked with administrative-close guidance. Administrative close may be offered when allowed. |
| Stopped formal/registered | Resume remains the primary recovery path from TASK_343A. Close can be offered as an explicit secondary archive path. Completed close requires the same completed confirmation contract. Administrative close requires reason. |
| Stopped temporary/no-LTR | Resume remains the primary recovery path. Completed close remains unavailable by default. Administrative close may be offered when allowed. |
| Closed completed | No Stop, Resume, Close again, close type conversion, or write action. Show readonly archive state and completed close summary when available. |
| Closed administrative | No Stop, Resume, Close again, close type conversion, or write action. Show readonly archive state and administrative reason when available. |

## 4. Completed Close Flow

Completed close is v1 manual confirmation because StepInstance does not exist.

Minimum flow:

1. Operator selects a functional `Close as completed` action only where allowed.
2. Workbench shows a confirmation surface with:
   - lifecycle state and project identity.
   - current output status summary from `completion_summary.output_status_summary` or available lifecycle response data.
   - explicit warning that testing completion is manually confirmed in this phase.
   - required acknowledgement for manual completion confirmation.
   - required acknowledgement that the output summary was reviewed.
   - required close note.
3. Submit calls `closeProjectCompletedLifecycle(projectId, { close_note, manual_completion_confirmed: true, output_summary_acknowledged: true })`.
4. On success, Workbench refreshes lifecycle/project state and shows closed completed readonly archive.
5. On 409 or validation error, Workbench shows business-readable guidance and does not change local state optimistically.

Completed close must not:

- claim ConnLab verified all tests automatically.
- require StepInstance.
- probe Office files, public-drive state, or output files from frontend.
- permit temporary/no-LTR completed close by default.

## 5. Administrative Close Flow

Administrative close archives a project without asserting test completion.

Minimum flow:

1. Operator selects a functional `Close administratively` action only where allowed.
2. Workbench shows a confirmation surface with:
   - lifecycle state and project identity.
   - concise explanation that the project will be archived readonly and cannot Resume.
   - required administrative reason.
3. Submit calls `closeProjectAdministrativeLifecycle(projectId, { reason })`.
4. On success, Workbench refreshes lifecycle/project state and shows closed administrative readonly archive.
5. On validation or lifecycle conflict, Workbench shows business-readable guidance and keeps the current state.

Administrative close must not imply completed testing.

## 6. UX Placement

TASK_343A created the Stop/Resume lifecycle action area. TASK_343B should extend that area rather than create a separate close page.

Recommended shape for Developer planning:

- One `Close project` secondary action can open a compact, explicit choice between completed and administrative close only when both are available.
- If completed close is ineligible, do not show it as a disabled future-looking action unless the disabled reason is necessary to explain why administrative close is the only current path.
- If administrative close is the only valid path for temporary/no-LTR planning, the UI should say that plainly.
- Confirmation should be a focused workbench surface. A modal is allowed only if Developer planning explains why inline/progressive confirmation would be less safe for this irreversible archive action.

## 7. May Touch

Planner activation may touch:

- `tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md`
- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_planner.md`
- `docs/task_board.md`

Reviewer plan gate may touch only a reviewer evidence/checkpoint if created, or report findings in thread.

Future Developer planning-first may touch only after Reviewer plan gate pass and routing:

- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md`

Future implementation may touch only after explicit approval of the Developer planning pass. Likely candidates:

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- new focused Workbench close component/test files under `frontend/src/features/project-workbench/` if Developer planning justifies them
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md`

## 8. Must Not Touch

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts` by default
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- TASK_343A implementation behavior except necessary close placement integration after explicit approval
- TASK_343C files
- TASK_336 through TASK_342 files except read-only reference
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

## 9. Locked Paths

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts`
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_*`
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- TASK_336 through TASK_342 task/plan/evidence files except read-only reference

## 10. Validation Plan

Developer planning-first must define exact validation before implementation.

Minimum implementation validation:

- active formal/registered project can open completed close confirmation when backend action state allows.
- completed close confirmation shows current output status summary or a clear unavailable-summary state without blocking the manual close contract.
- completed close requires non-empty close note, manual completion confirmation, and output summary acknowledgement.
- completed close submit calls `closeProjectCompletedLifecycle(...)` with the existing DTO.
- temporary/no-LTR planning project does not present completed close as an available default path and points to administrative close when close is allowed.
- active/stopped project can open administrative close confirmation when allowed.
- administrative close requires non-empty reason.
- administrative close submit calls `closeProjectAdministrativeLifecycle(...)` with the existing DTO.
- successful close refreshes Workbench state into closed completed/admin readonly archive.
- closed completed/admin states show no Stop, Resume, Close again, or close type conversion controls.
- stopped readonly write controls remain blocked through existing TASK_338/TASK_339A behavior.
- Matrix remains primary in active Matrix workspace.
- no backend/API/schema/frontend API client changes occur.
- TASK_343C Projects list copy/routing remains untouched.
- focused frontend tests pass.
- frontend build passes or unrelated build blocker is recorded with evidence.
- QA smoke covers active formal close completed, temporary administrative-only guidance, stopped close path, and closed archive no-action state. If browser tooling is unavailable, QA must record residual-risk disposition.

Suggested source scans:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "StepInstance|Report generation|AI review|permissions|LAN/server|multi-user" frontend/src/features/project-workbench frontend/src/workbench.css
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md
```

## 11. Reviewer / QA / Merge Gates

Reviewer plan gate is required now.

Reviewer should block if:

- plan expands into backend/API/schema without a separate blocker and explicit user approval path.
- plan permits completed close for temporary/no-LTR projects by default.
- plan implies automatic test completion.
- plan hides closed readonly/archive constraints.
- plan mixes TASK_343C Projects list alignment.
- plan lacks testable validation for completed/admin close flows.

After Reviewer plan gate pass, the recommended next role is Developer planning-first. Developer must refine exact component/file list, confirmation pattern, data derivation, and tests before product code is written, unless the user explicitly approves implementation in the same routed task.

QA gate is required after implementation.

Integrator may accept only after:

- Developer evidence records completed implementation and validation.
- Reviewer has no blocking findings.
- QA passes or records an accepted non-blocking residual.
- package contains only approved TASK_343B files plus task/plan/evidence/board updates.
- no backend/API/schema/frontend API client changes are included unless a separate approved lane or approved scope change exists.
- no TASK_343C, Report, StepInstance, AI, permissions, LAN/server, multi-user, or unrelated governance residuals are mixed in.

## 12. Unrelated Residuals

Current dirty governance/orchestration residuals under `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*` are explicitly excluded from TASK_343B product implementation and packaging unless a separate governance lane owns them.

## 13. Planner Validation Commands

```powershell
Test-Path tasks\TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md
Test-Path docs\task_343b_close_completed_admin_confirmation_flow_plan.md
Test-Path docs\lane_evidence\TASK_343B_workbench-close-completed-admin-ux_planner.md
Select-String -Path docs\task_board.md -Pattern 'workbench-close-completed-admin-ux' -Encoding UTF8
Select-String -Path docs\task_343b_close_completed_admin_confirmation_flow_plan.md -Pattern 'Planner gate: ready' -Encoding UTF8
Select-String -Path docs\task_343b_close_completed_admin_confirmation_flow_plan.md -Pattern 'formal/registered' -Encoding UTF8
git diff --check -- tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md docs/task_343b_close_completed_admin_confirmation_flow_plan.md docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_planner.md docs/task_board.md
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx
```

## 14. Developer Planning-First Resolution

### Anti-Skip Confirmation

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current task/lane: `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW` / `workbench-close-completed-admin-ux`.

Allowed reason: Reviewer plan gate passed for TASK_343B with no blocking findings, and the user explicitly routed this Developer planning-first pass. This pass updates only this plan and TASK_343B Developer evidence. Product code, tests, backend/API/schema, frontend API client, TASK_343C, and board closeout remain locked until a later approved implementation gate.

### Actual Code Inspection Summary

Read-only frontend inspection confirmed:

- `frontend/src/api/client.ts` already exports `closeProjectCompletedLifecycle(...)`, `closeProjectAdministrativeLifecycle(...)`, `ProjectLifecycleCloseCompletedRequest`, and `ProjectLifecycleCloseAdministrativeRequest`.
- `ProjectLifecycleCloseCompletedRequest` already has the required `close_note`, `manual_completion_confirmed`, and `output_summary_acknowledged` fields. `ProjectLifecycleCloseAdministrativeRequest` already has required `reason`.
- `ProjectLifecycleResponse` already exposes `allowed_actions`, `lifecycle_state`, `closure_type`, `readonly`, and optional `completion_summary`.
- `frontend/src/api/client.ts` also already exposes `getProjectOutputStatusSummary(...)` and `ProjectOutputStatusSummary`. No API-client change is needed for TASK_343B planning.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` already owns `outputStatusSummary`, refreshes it from `getProjectOutputStatusSummary(...)`, and owns Stop/Resume lifecycle handlers from TASK_343A.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts` currently derives Stop/Resume action visibility and keeps `canClose: false` from TASK_343A. TASK_343B should be the first lane allowed to replace that fixed false close action model with completed/admin close eligibility.
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` currently owns the compact lifecycle management panel and inline confirmation pattern for Stop/Resume. TASK_343B should extend this action area or extract a focused close confirmation component rather than creating a new page.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` already passes lifecycle actions, lifecycle busy/error state, Stop/Resume callbacks, and `runtimeModel.outputStatusSummary` through the Workbench shell. TASK_343B can keep Matrix primary and add close actions without route-level changes.

No implementation blocker was found that requires backend/API/schema or `frontend/src/api/client.ts` changes.

### Exact Implementation File List After Approval

After explicit implementation approval, TASK_343B may touch only:

- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md`

Do not touch `frontend/src/api/client.ts`; the required close helpers and DTOs already exist. Do not touch backend, root tests, Projects registry files, TASK_343A reimplementation, TASK_343C files, or TASK_336 through TASK_342 files during Developer implementation.

### Close Action Derivation

Extend the Workbench lifecycle action model in `projectWorkbenchLifecycleSelectors.ts` without exposing raw backend enum tokens to operators.

The selector should derive:

- `canCloseCompleted`: true only when lifecycle is active or stopped, `allowed_actions` includes `close`, project is formal/registered, and the project is not already closed.
- `canCloseAdministrative`: true only when lifecycle is active or stopped, `allowed_actions` includes `close`, and the project is not already closed.
- `preferredClosePath`: `completed` for formal/registered active or stopped projects when completed close is eligible; `administrative` for temporary/no-LTR or non-completion close.
- business-readable close labels and helper copy.
- no close action at all for closed completed/admin states.

Formal/registered eligibility should use existing frontend state: project number and/or LTR records already present in the Workbench model. If lifecycle data is unavailable, do not guess. Hide close actions and keep read surfaces visible.

### Close Completed UX

Recommended implementation pattern:

1. Show `Close as completed` only for eligible formal/registered active or stopped projects where lifecycle `allowed_actions` includes `close`.
2. Use a compact inline confirmation surface in the lifecycle action area or a focused `ProjectWorkbenchCloseConfirmation` component. Do not create a new route.
3. Display project identity and current output status summary using `runtimeModel.outputStatusSummary`.
4. If the output summary is unavailable, show a clear unavailable-summary state and still require explicit acknowledgement of the available status information.
5. Require a non-empty close note.
6. Require manual completion confirmation because current scope has no StepInstance execution authority.
7. Require output status summary acknowledgement.
8. Submit through `closeProjectCompletedLifecycle(projectId, { close_note, manual_completion_confirmed: true, output_summary_acknowledged: true, operator: null })`.
9. On success, refresh lifecycle, project identity/status, and output status summary, clear local confirmation state, and render the closed completed readonly archive.
10. After closed completed, show no Stop, Resume, Close again, conversion, or edit action.

### Close Administrative UX

Recommended implementation pattern:

1. Show `Close administratively` for active or stopped projects where lifecycle `allowed_actions` includes `close`.
2. Make administrative close the default path for temporary/no-LTR planning projects. Do not present completed close as the default or equal path for temporary/no-LTR projects.
3. Require a non-empty administrative reason.
4. Use copy that says the project is archived without implying test completion.
5. Submit through `closeProjectAdministrativeLifecycle(projectId, { reason, operator: null })`.
6. On success, refresh lifecycle, project identity/status, and output status summary, clear local confirmation state, and render the closed administrative readonly archive.
7. After closed administrative, show no Stop, Resume, Close again, conversion, or edit action.

### TASK_343A Preservation

Do not redesign Stop/Resume. TASK_343B should reuse the existing lifecycle action area, busy/error pattern, and model refresh approach from TASK_343A. Existing Stop/Resume tests must continue to pass, and close UI must not make stopped readonly write controls writable.

### Test Plan For Implementation Pass

Focused selector tests:

- formal/registered active project with `allowed_actions=["stop", "close"]` derives Stop and completed/admin close eligibility.
- temporary/no-LTR active project with `allowed_actions=["stop", "close"]` derives administrative close as the default and does not derive completed close.
- stopped formal/registered project with `allowed_actions=["resume", "close"]` derives Resume and completed/admin close eligibility.
- closed completed/admin projects derive no Stop, Resume, Close, conversion, or close-again action.
- lifecycle unavailable or missing `close` action derives no close action.
- user-facing labels do not expose `lifecycle_state`, `closure_type`, `closed_completed`, `closed_administrative`, or `cancelled`.

Focused model tests:

- completed close trims and sends required `close_note`, `manual_completion_confirmed: true`, `output_summary_acknowledged: true`, and `operator: null`.
- completed close rejects blank note before API call.
- completed close success refreshes lifecycle, project identity/status, and output status summary.
- administrative close trims and sends required `reason` and `operator: null`.
- administrative close rejects blank reason before API call.
- administrative close success refreshes lifecycle, project identity/status, and output status summary.
- no backend/API-client helper shape change is required.

Focused component tests:

- active formal/registered Workbench shows `Close as completed` when allowed, renders output status summary acknowledgement, requires close note and both acknowledgements, then calls the completed close handler.
- temporary/no-LTR Workbench shows administrative close guidance and does not show completed close as the default path.
- stopped readonly Workbench preserves readonly reason and Resume while also allowing close only when lifecycle data allows it.
- closed completed/admin Workbench shows readonly archive state and no Stop, Resume, Close again, or conversion control.
- TASK_343A Stop/Resume inline confirmation remains available in the states covered by TASK_343A.
- Projects registry copy/routing is not changed by TASK_343B.

### Validation Commands For Implementation Pass

Run from `frontend/`:

```powershell
npm test -- --run src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/useProjectWorkbenchModel.test.tsx src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
npm run build
```

Run from repository root:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md
rg -n "[ \t]$" frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md docs/task_board.md
```

Production future-scope scan:

```powershell
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "StepInstance|Report generation|AI review|permissions|LAN/server|multi-user" frontend/src/features/project-workbench frontend/src/workbench.css
```

Expected implementation result:

- focused tests pass
- frontend build passes or unrelated blocker is documented
- `frontend/src/api/client.ts`, backend, root tests, Projects registry, TASK_343C, and `docs/task_board.md` are not changed by Developer implementation
- closed states remain readonly archives with no Stop, Resume, Close again, or conversion controls

### Browser / Manual Smoke Expectations

QA is required after Reviewer pass because TASK_343B changes the main Workbench lifecycle action flow.

QA should smoke:

- formal/registered active Workbench: completed close confirmation opens, output status summary/acknowledgement is visible, and close note is required.
- temporary/no-LTR active Workbench: administrative close is the available default close path; completed close is not presented as the default path.
- stopped Workbench: readonly reason remains visible; Resume remains available when allowed; close path is available only when backend action data allows it.
- closed completed archive: no Stop, Resume, Close again, or conversion control.
- closed administrative archive: no Stop, Resume, Close again, or conversion control.
- narrow viewport: close confirmation surface wraps without overlapping Project State, Matrix, Outputs, or readonly archive copy.
- keyboard order reaches header, lifecycle action area, close confirmation controls, primary workspace, and Outputs in a logical order.

If browser tooling is unavailable, QA may record a non-blocking residual only if focused tests, static scans, and build validation pass.

### Planning-First Validation

Planning pass validation:

```powershell
Test-Path docs\task_343b_close_completed_admin_confirmation_flow_plan.md
Test-Path docs\lane_evidence\TASK_343B_workbench-close-completed-admin-ux_developer.md
git diff --check -- docs/task_343b_close_completed_admin_confirmation_flow_plan.md docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md
rg -n "[ \t]$" docs/task_343b_close_completed_admin_confirmation_flow_plan.md docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx docs/task_board.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md
```

Expected planning-pass scope:

- only `docs/task_343b_close_completed_admin_confirmation_flow_plan.md` and `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md` are edited by Developer.
- no `frontend/`, `backend/`, or `tests/` product files are edited.
- `docs/task_board.md` may remain dirty from external Planner/Integrator residuals, but Developer does not edit it in this pass.

Developer planning gate: complete. Implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness completed on 2026-06-27.

## 15. Stop Point

Developer planning gate: ready.

Stop after Integrator packaging/readiness acceptance and completion callback. Do not start TASK_343C, backend changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, push, reset, delete, or unrelated cleanup.
