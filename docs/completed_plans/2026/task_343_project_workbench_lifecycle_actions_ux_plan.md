# TASK_343 Project Workbench Lifecycle Actions UX Plan

Status: complete/accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: project-workbench-lifecycle-actions-ux
Role: Planner/Designer
Last Updated: 2026-06-27

## 1. Discovery Gate

### Current State

Current active task/lane: no active implementation lane. `docs/task_board.md` marks TASK_342 complete and accepted after Reviewer, QA, and Integrator gates.

Why Planner is allowed: the user explicitly asked Planner to create or activate the next formal planning-first lane, `TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX`, after manual smoke found remaining lifecycle action UX gaps.

This pass is planning only. It does not implement frontend UI, backend behavior, tests, database changes, API changes, runtime routing, lifecycle writes, or registry code.

### User Goal Restatement

The next lifecycle/workbench step should close the operator-facing lifecycle action loop that remains after the first Workbench shell implementation. Stop, Resume, Close completed, and Close administrative should feel like coherent Project Workbench actions, not scattered or missing affordances. The plan must compare the original product rules with delivered TASK_337A through TASK_342 capability, decide whether to split TASK_343 into smaller implementation lanes, and define the first lane's gates. It must keep future scope out of the product surface.

### Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- TASK_337A task, plan, and developer evidence
- TASK_337B task, plan, and developer evidence
- TASK_338 task, plan, and developer evidence
- TASK_339A task, plan, and developer evidence
- TASK_339B task, plan, and developer evidence
- TASK_340 task, plan, and planner evidence
- TASK_341 task, plan, developer evidence, and QA evidence
- TASK_342 task, plan, developer evidence, and QA evidence
- `$impeccable` product context, including `PRODUCT.md`, `DESIGN.md`, and product-register guidance

### Confirmed By User

- Original product rules:
  - Stop project means pause and may Resume.
  - Stopped is readonly and does not allow draft editing or writes.
  - Resume project restores continued progress.
  - Close supports completed and administrative closure.
  - Current ConnLab has no StepInstance, so close completed v1 uses manual confirmation, output status summary, close note, and confirmation.
  - Closed projects are readonly archives and cannot Resume.
- Manual smoke found remaining gaps in Workbench Stop/Resume/Close loop, close confirmation flow, Active Matrix lifecycle action area, and Projects list action copy/routing alignment.
- Planner must not write product code or start Developer implementation.

### Confirmed By Repository Evidence

- TASK_337A implemented backend lifecycle/API shape, including:
  - `GET /api/projects/{project_id}/lifecycle`
  - `POST /api/projects/{project_id}/lifecycle/stop`
  - `POST /api/projects/{project_id}/lifecycle/resume`
  - `POST /api/projects/{project_id}/lifecycle/close-completed`
  - `POST /api/projects/{project_id}/lifecycle/close-administrative`
  - completed close stores `signals` and `output_status_summary`
  - lifecycle conflicts return stable business fields, including `allowed_actions`
- TASK_337B classified lifecycle actions, readonly previews, and writes.
- TASK_338 implemented the first backend write-guard slice and preserved non-mutating previews.
- TASK_339A implemented frontend readonly model and blocked/suppressed writes in stopped and closed states.
- TASK_339B implemented registry lifecycle views and explicitly did not add lifecycle write actions from the registry.
- TASK_340 defined the Unified Workbench Shell IA, state-specific behavior, and lifecycle action model.
- TASK_341 implemented the first Workbench shell slice, but explicitly did not invent Resume/Close action controls where wiring was not already present.
- TASK_342 closed the TASK_339A through TASK_342 series, with non-blocking residual browser narrow-viewport/tab-order follow-up and no product source/test changes.
- `docs/task_board.md` records no active implementation lane.

### Inferred By Planner

- TASK_337A API is probably sufficient for TASK_343A frontend action placement and Stop/Resume action wiring.
- Completed/admin close confirmation UX should be its own implementation lane because it contains confirmation dialogs, required note/reason rules, output summary acknowledgement, and post-close refresh behavior.
- Projects registry action copy/routing alignment should be its own smaller lane because TASK_339B intentionally avoided lifecycle write actions and kept row action read/navigation oriented.
- QA should be required for implementation lanes that alter main Workbench lifecycle workflow, because component tests alone may miss operator flow and layout affordance issues.

### Not Yet Confirmed

- Whether the current frontend already exposes every lifecycle API helper needed for close completed/admin forms. This does not block TASK_343 planning. TASK_343B Developer planning must verify it before product code.
- Whether browser automation will be available for future QA. This does not block TASK_343 planning, but future QA must record browser/manual smoke or an explicit residual disposition.

### Planning Risk

The main risk is turning one UX gap into a broad Workbench rewrite. A second risk is mixing backend API changes into a frontend action-placement lane even though TASK_337A already provides lifecycle endpoints. A third risk is adding close completed UI for temporary/no-LTR projects in a way that violates the accepted contract.

### Continue Decision

Definition of Ready is satisfied for a planning-first TASK_343 lane. Dependencies are complete, the user goal is explicit, source evidence exists, non-goals are clear, and unresolved questions can be isolated to later Developer planning for TASK_343A or TASK_343B.

Planner gate: ready.

## 2. Gap Review

| Original product rule | Delivered capability from TASK_337A-TASK_342 | Remaining gap | Recommended lane |
|---|---|---|---|
| Stop project means pause and may Resume. | TASK_337A added stop/resume API. TASK_339A added readonly model. TASK_341 shell shows lifecycle state. | Workbench action area does not yet complete the operator loop for Stop and Resume across active/stopped shell states. | TASK_343A |
| Stopped is readonly and cannot edit drafts or write. | TASK_338 guards first write slice. TASK_339A suppresses/disables frontend writes. TASK_341 keeps readonly shell visible. | Action area should make "Resume before editing" the visible path while keeping read surfaces available. | TASK_343A |
| Resume project restores continued progress. | TASK_337A restores compatibility status from lifecycle event metadata and rejects unsafe legacy resume. | Workbench needs business-readable Resume affordance, loading/error/refresh behavior, and success routing. | TASK_343A |
| Close supports completed and administrative closure. | TASK_337A added close-completed and close-administrative endpoints. TASK_340 documented close UX expectations. | Confirmation flows are not fully implemented in Workbench. | TASK_343B |
| Close completed v1 is manual confirmation because no StepInstance exists. | TASK_337A persists close summary signals and output status summary. TASK_336/TASK_340 document no-StepInstance boundary. | Workbench needs a dialog that shows current output status summary, requires note and acknowledgement, and avoids claiming automated test completion. | TASK_343B |
| Close completed defaults to formal/registered projects. Temporary/no-LTR defaults to administrative close. | TASK_336 and TASK_337A define this boundary. | UI must enforce and explain eligibility instead of making completed close the default for temporary planning projects. | TASK_343B |
| Close administrative requires reason. | TASK_336 and TASK_337A define required reason. | Workbench needs required reason form, submit behavior, and archive refresh. | TASK_343B |
| Closed projects are readonly archives and cannot Resume. | TASK_338/TASK_339A/TASK_341 enforce/display readonly archive behavior and no Resume in closed shell. | Post-close state should consistently remove Stop/Resume/Close controls and show close summary/reason. | TASK_343B, then TASK_343A regression coverage |
| Projects list should align labels, Next Step, and Open routing with Workbench states. | TASK_339B implemented On-going, Planning, Closed, All views and business labels. | Manual smoke found action copy/routing alignment still needs a focused follow-up after Workbench actions land. | TASK_343C |
| Active Matrix workspace should remain primary while lifecycle actions are reachable. | TASK_341 keeps Matrix primary and Outputs secondary. | Active Matrix workspace lacks a stable lifecycle action area that does not outrank Matrix. | TASK_343A |

## 3. Split Decision

TASK_343 should be a Planner/UX contract lane, not a single implementation lane.

Recommended split:

1. `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`
   - First implementation lane.
   - Frontend-only by default.
   - Adds a Workbench lifecycle action area, Stop and Resume action UX, action visibility rules, and state refresh behavior using existing TASK_337A/TASK_339A contracts.
   - Withholds every Close affordance until TASK_343B or another approved functional close lane exists.
2. `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW`
   - Second implementation lane.
   - Adds close completed and close administrative confirmation forms, output summary acknowledgement, required note/reason validation, and post-close refresh/archive behavior.
3. `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`
   - Third implementation lane.
   - Aligns Projects list classification copy, Next Step copy, and Open button/routing language with the accepted Workbench lifecycle states after 343A/343B settle the Workbench action contract.

Rationale:

- Stop/Resume action placement is a smaller Workbench shell enhancement and should land before close-specific dialogs.
- Close confirmation flow has enough UX and business-rule weight to deserve its own validation gate.
- Showing a disabled, reserved, non-functional, or routed Close control before TASK_343B would expose future/unavailable product action and blur implementation ownership.
- Registry copy/routing should follow the final Workbench action language rather than inventing separate wording.
- A single implementation package would make Reviewer/QA scope too broad.

## 4. Backend Touch Decision

Default decision: no backend touch for TASK_343A.

TASK_337A already provides the lifecycle API shape and close summary fields. TASK_338 already provides the first write-guard primitive. TASK_339A already provides frontend lifecycle readonly model and API consumption paths.

Backend touch is not approved for TASK_343A. If Developer planning finds a missing lifecycle API helper, DTO field, or close summary gap, the correct response is to stop and ask Planner to create a separate backend/API follow-up or move that need into TASK_343B planning. Do not expand TASK_343A.

## 5. Workbench State Behavior Contract

| State/workspace | Top lifecycle banner | Primary action | Stop/Resume/Close operations | Readonly behavior | Allowed actions | Forbidden actions |
|---|---|---|---|---|---|---|
| Active Matrix workspace | `Active` with formal identity and `Active Matrix` marker. Keep Matrix first. | Continue current Matrix authority work or highest current blocker. | TASK_343A: Stop available in lifecycle action area; Resume hidden; all Close controls withheld. TASK_343B: Close may be introduced only with functional confirmation flow. | Not readonly. | Current active Workbench reads/writes allowed by existing business rules. Readonly previews allowed where current feature supports them. | Closed/archive actions, Resume, any Close placeholder or non-functional Close route in TASK_343A, future Report/StepInstance/AI/permissions controls. |
| Registered setup, no active Matrix | `Active` with registered/formal identity and `No Matrix` or `Candidate Matrix`. | Open Matrix authority setup. | TASK_343A: Stop available; Resume hidden; all Close controls withheld. TASK_343B: Completed/Admin close may be introduced only with functional confirmation flow and eligibility rules. | Not readonly. | Matrix setup and current registered setup writes allowed by existing rules. | Resume, closed archive actions, any Close placeholder or non-functional Close route in TASK_343A, future scope. |
| Temporary planning/no LTR | `Active` with temporary planning identity and no formal completion implication. | Continue planning or Matrix/Fee preparation where current features support it. | TASK_343A: Stop available; Resume hidden; all Close controls withheld. TASK_343B: Administrative close may be introduced with functional reason flow; completed close remains ineligible by default. | Not readonly. | Current temporary planning writes allowed by existing rules. | Close as completed by default, any Close placeholder or non-functional Close route in TASK_343A, Resume, formal completion copy, future scope. |
| Stopped | `Stopped project`: `This project is paused. Resume it before making changes.` | Resume project. | TASK_343A: Resume primary; Stop hidden; all Close controls withheld. TASK_343B: Close may be introduced only with functional confirmation flow. | Readonly. Keep read and preview surfaces visible when non-mutating. | Read project data, readonly previews, lifecycle Resume. | Draft edits, Matrix/Fee/Basic Information/Folder/Required Forms/Public Drive writes, Stop again, any Close placeholder or non-functional Close route in TASK_343A, Delete temporary project unless separately approved. |
| Closed completed | `Closed: Completed`: archived as completed and readonly. | View archive/status. | No Stop, Resume, or Close again. | Readonly archive. Completed close note and output summary should be visible once TASK_343B lands. | Read project data, lifecycle history/summary where current data exists, non-mutating previews. | Any write action, Resume, Stop, close again, completed/admin conversion, future scope. |
| Closed administrative | `Closed: Administrative`: archived administratively and readonly. | View archive/status. | No Stop, Resume, or Close again. | Readonly archive. Administrative reason should be visible once TASK_343B lands. | Read project data, lifecycle history/reason where current data exists, non-mutating previews. | Any write action, Resume, Stop, close again, closure-type conversion, future scope. |

## 6. Close Completed V1 Flow Contract

TASK_343B should implement this flow, not TASK_343A.

TASK_343A must not expose this flow as a visible button, disabled placeholder, reserved menu item, routing target, or non-functional affordance.

1. Eligibility:
   - Active or stopped formal/registered project.
   - Temporary/no-LTR planning projects default to administrative close.
   - Closed projects cannot close again.
2. Open confirmation:
   - Entry point from Workbench lifecycle action area.
   - Dialog or inline confirmation may be used, but it must behave like a guarded confirmation, not a casual button.
3. Summary display:
   - Show current output status summary from existing lifecycle response data or current output status source.
   - Clearly state that ConnLab has no StepInstance yet and this is manual completion confirmation.
   - Do not claim all tests are complete automatically.
4. Required input:
   - `close_note` required.
   - `output_summary_acknowledged` required.
5. Submit:
   - Use existing `POST /api/projects/{project_id}/lifecycle/close-completed`.
   - Show loading and business-readable error states.
6. Success:
   - Refresh lifecycle state, Workbench model, and registry-visible state.
   - Render closed completed archive state with no Resume/Stop/Close controls.

## 7. Close Administrative Flow Contract

TASK_343B should implement this flow, not TASK_343A.

TASK_343A must not expose this flow as a visible button, disabled placeholder, reserved menu item, routing target, or non-functional affordance.

1. Eligibility:
   - Active or stopped project, including temporary/no-LTR planning projects.
   - Closed projects cannot close again.
2. Open confirmation:
   - Entry point from Workbench lifecycle action area.
   - Copy should distinguish administrative archive from completed work.
3. Required input:
   - `reason` required.
4. Submit:
   - Use existing `POST /api/projects/{project_id}/lifecycle/close-administrative`.
   - Show loading and business-readable error states.
5. Success:
   - Refresh lifecycle state, Workbench model, and registry-visible state.
   - Render closed administrative archive state with reason emphasis and no Resume/Stop/Close controls.

## 8. Projects List Alignment Contract

TASK_343C should refine the registry after Workbench action language stabilizes.

| Registry state | View | Status label | Next Step copy | Open button/routing copy |
|---|---|---|---|---|
| Active temporary/no-LTR | Planning | `Active` or `Planning` depending current TASK_339B helper naming | `Continue planning` | `Open Workbench` |
| Active registered without active Matrix | On-going | `Active` | `Open Matrix authority` | `Open Workbench` |
| Active registered with active Matrix | On-going | `Active` | `Continue in Matrix` or `Open Workbench` after TASK_343A chooses final action copy | `Open Workbench` |
| Stopped temporary/no-LTR | Planning | `Stopped` | `Review or resume in Workbench` | `Open Workbench` |
| Stopped registered/formal | On-going | `Stopped` | `Review or resume in Workbench` | `Open Workbench` |
| Closed completed | Closed | `Closed: Completed` | `Open completed archive` | `View archive` |
| Closed administrative | Closed | `Closed: Administrative` | `Open administrative archive` | `View archive` |

Registry constraints:

- Keep Projects list read/navigation oriented.
- Do not add Stop, Resume, Close, Delete, or lifecycle write actions from the registry unless a later approved task explicitly changes that rule.
- Do not render raw enum words such as `cancelled`, `closed_completed`, `closed_administrative`, `lifecycle_state`, or `closure_type`.
- If a row opens a closed project, route to the same Workbench shell in archive mode rather than a separate closed page.

## 9. First Implementation Lane: TASK_343A

### Lane Identity

Task: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`

Lane: `workbench-lifecycle-actions-ux`

Recommended next role after TASK_343 Reviewer pass and user approval: Frontend Developer planning-first.

### Goal

Add a coherent Workbench lifecycle action area for current supported actions, especially Stop and Resume, while preserving TASK_341 shell hierarchy and keeping Matrix as the primary workspace when active Matrix authority exists.

TASK_343A must withhold Close controls entirely. It must not implement, display, disable, reserve, route, or otherwise expose `Close project`, Close as completed, or Close administratively. Close UI, confirmation dialog, output summary, close note, administrative reason, acknowledgement checkbox, post-close archive transition, and close API calls remain TASK_343B only unless a separate approved functional close lane exists before TASK_343A implementation.

### May Touch

Frontend Developer planning may touch:

- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md` if TASK_343A is later created
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md` if TASK_343A is later created

Frontend Developer implementation may touch only files explicitly confirmed in the approved TASK_343A plan, likely:

- `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.tsx` only if needed to call existing lifecycle refresh/action helpers
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts` only for action copy helpers, with tests, if existing model cannot express action availability
- `frontend/src/api/client.ts` only if existing TASK_337A lifecycle helpers are missing from the frontend client; no API contract change
- `frontend/src/workbench.css`
- TASK_343A evidence

### Must Not Touch

- backend code
- database migrations
- API contract or backend DTO shape
- root `tests/` outside frontend tests
- Projects registry implementation, except read-only reference to TASK_339B behavior
- close completed/admin confirmation forms
- visible Close controls, disabled Close placeholders, reserved Close buttons, Close menu items, Close routing targets, non-functional Close affordances, output summary acknowledgement, close note/reason fields, or close API calls
- Matrix/Fee/Folder/Basic Information/LTR/Required Forms/Public Drive business rules
- Report generation
- StepInstance or execution persistence
- AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residuals

### Locked Paths

- `backend/`
- `tests/`
- `docs/project_management/`
- `.agents/skills/`
- `AGENTS.md`
- prior TASK_336 through TASK_342 task/plan/evidence files, except read-only reference
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`

### Evidence File

Recommended future evidence:

`docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`

### Validation Gate

TASK_343A validation must prove:

- Active Matrix workspace keeps Matrix primary and lifecycle action area does not outrank Matrix.
- Active registered setup exposes Stop and no Close controls.
- Active temporary planning exposes Stop and no Close controls.
- Stopped workspace shows readonly reason, Resume as primary lifecycle action, and no write controls.
- Closed completed/admin workspaces show archive state and no Stop, Resume, or Close again.
- Stop and Resume use existing lifecycle API/client helpers, refresh Workbench lifecycle state, and show loading/error states.
- TASK_343A renders no `Close project`, Close as completed, Close administratively, disabled Close placeholder, Close menu item, Close route, output summary acknowledgement, close note/reason field, or close API call.
- Readonly previews remain available only where TASK_337B/TASK_338 classify them as non-mutating.
- Raw enum copy is not visible.
- No Report, StepInstance, AI, permissions, LAN/server, or multi-user controls appear.
- Focus order and narrow layout for lifecycle action area are covered by component/static tests and, if available, browser/manual QA.

Recommended commands:

```powershell
cd frontend
npm test -- --run src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts
npm run build
```

```powershell
git diff --check -- frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
git status --short -- backend tests docs/project_management .agents AGENTS.md
```

### Reviewer Gate

Reviewer must check:

- TASK_343A did not implement or expose TASK_343B close dialogs, close buttons, disabled placeholders, reserved menu items, routing targets, output summaries, close note/reason fields, acknowledgement controls, or close API calls.
- backend/API contract was not changed.
- action copy follows TASK_336/TASK_340 product semantics.
- stopped/closed readonly behavior remains intact.
- active Matrix workspace remains primary.
- no future scope appears.

### QA Gate

QA is required because lifecycle actions alter the main Workbench operator flow.

QA should smoke:

- active temporary/no-LTR state
- active registered/no active Matrix state
- active registered/active Matrix state
- stopped state with Resume visible
- active and stopped states have no visible Close controls or Close placeholders
- closed completed state has no Stop, Resume, Close again, or close-type conversion controls
- closed administrative state has no Stop, Resume, Close again, or close-type conversion controls
- narrow viewport action area wrapping
- keyboard order through header, lifecycle action area, banner, Matrix/primary workspace, Outputs, and archive/history summary where present

If browser tooling is unavailable, QA must record a clear residual-risk disposition and justify whether component/static coverage is sufficient.

### Merge Gate

Integrator may accept TASK_343A only after:

- Developer evidence is ready.
- Reviewer has no blocking findings.
- QA passes or records an accepted non-blocking residual.
- package contains only approved TASK_343A files.
- no TASK_343B close UI, placeholder, route, form, summary, note/reason field, acknowledgement control, or close API call is included.
- backend/tests/governance residuals are not mixed into the product package.

## 10. TASK_343 Planner Lane Gates

### May Touch

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- `docs/task_board.md`

### Must Not Touch

- `frontend/`
- `backend/`
- root `tests/`
- TASK_343A/B/C task files unless separately approved
- runtime behavior
- unrelated governance/orchestration residuals

### Locked Paths

- `frontend/`
- `backend/`
- `tests/`
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- TASK_336 through TASK_342 source/evidence files, except read-only reference

### Evidence

`docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`

### Validation Gate

- Planning files and board row exist.
- Discovery Gate separates user facts, repo evidence, and Planner assumptions.
- Gap review table exists.
- Split decision exists.
- First implementation lane gates exist.
- No product code changed.

### Merge Gate

No product merge. TASK_343 must pass Reviewer plan gate before Planner/user creates or approves TASK_343A.

## 11. Unrelated Residuals

Current dirty governance/orchestration residuals under `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*` are explicitly excluded from TASK_343 and all recommended TASK_343A/B/C product implementation packages unless a separate governance lane owns them.

## 12. Stop Point

Stop after updating TASK_343 Planner evidence and notifying Orchestrator.

Do not start Developer implementation, TASK_343A, TASK_343B, TASK_343C, backend guard changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, or unrelated governance cleanup.
