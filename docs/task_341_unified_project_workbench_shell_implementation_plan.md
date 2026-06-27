# TASK_341 Unified Project Workbench Shell Implementation Plan

Last Updated: 2026-06-27
Status: implementation complete - Integrator accepted
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: unified-workbench-shell-implementation
Role: Frontend Developer planning-first

## 1. Discovery Gate

Current active task/lane: no active implementation lane. `docs/task_board.md` marks TASK_339A, TASK_339B, and TASK_340 complete/accepted.

Why Planner is allowed: the user explicitly asked Planner to create or activate the missing formal planning-first lane `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION`. The board says the next step is Planner creation or activation before any implementation continues.

User goal restatement:

- Create the formal TASK_341 lane for the next lifecycle/workbench series step.
- Use TASK_340 only as accepted shell planning input, not as runtime implementation.
- Keep the lane planning-first and gated before product code.
- Define concrete May Touch, Must Not Touch, Locked Paths, evidence, validation, and merge gates.
- Do not start TASK_342, backend guard changes, or future-scope features.

Confirmed by user:

- TASK_339A is complete/accepted.
- TASK_339B is complete/accepted after Reviewer and Integrator gates.
- TASK_340 is complete/accepted as planning output only.
- TASK_341/TASK_342 formal files are currently missing.
- External governance/orchestration dirty residuals must not be mixed into TASK_341 product implementation scope.

Confirmed by repository evidence:

- `docs/task_board.md` reports no active implementation lane and TASK_339B complete/accepted.
- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md` exists and has `Status: complete`.
- `docs/task_340_unified_project_workbench_shell_plan.md` has `Status: accepted` and defines the shell regions, state-specific behavior, serial order, and smoke checklist.
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md` has `Status: complete` and records no product code changes.
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md` records `Integrator gate: accepted`.
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md` records `Integrator gate: accepted`.
- The expected TASK_341 and TASK_342 formal files do not exist before this Planner turn.
- Current Workbench shell frontend files are under `frontend/src/features/project-workbench/`, with `ProjectWorkbenchPage.tsx` and `frontend/src/workbench.css` as likely shell entry/style surfaces.
- Frontend architecture rules require pages to compose feature components, selectors to own display/disabled/next-action decisions, and API calls to stay centralized.

Inferred by Planner:

- TASK_341 should be a frontend-only Workbench shell implementation lane.
- Because the implementation affects the main operator flow, QA should be mandatory after Reviewer pass.
- Because TASK_340 is accepted but broad, Developer should first update or confirm the implementation plan and stop for user approval before product code.

Not yet confirmed:

- The exact first implementation slice and exact frontend file list must be confirmed by the Developer planning pass and user review.

Planning risk:

- Without a planning-first stop, TASK_341 could become a broad Workbench rewrite.
- Without explicit gates, output panels may visually outrank Matrix, undermining the accepted product principle.
- Without QA, layout and state behavior regressions could slip through component tests.

Recommendation:

Continue with explicit assumptions and activate TASK_341 as `approved` for Developer planning first only. Product code remains blocked until the Developer plan is updated and user-approved.

## 2. Definition Of Ready

Definition of Ready is satisfied for a planning-first lane:

- user goal and scenario are clear: implement the accepted Unified Project Workbench Shell first slice
- board state and dependencies are verified from files
- existing behavior was checked from TASK_340 evidence and current Workbench frontend entry files
- formal task, plan, evidence, and board lane are created by this Planner action
- dependencies and serialization constraints are explicit
- May Touch, Must Not Touch, Locked Paths, evidence, validation, and merge gates are concrete
- acceptance path is testable through focused frontend tests, build, Reviewer, QA smoke, and Integrator packaging
- non-goals prevent TASK_342, backend, Report, StepInstance, AI, permissions, LAN/server, multi-user, and registry redesign scope creep
- unresolved exact-file assumptions are documented as Developer planning output, not implementation approval

Planner gate: ready.

## 3. Implementation Direction

TASK_341 should implement one controlled Workbench shell slice from the accepted TASK_340 plan:

```text
Project Workbench Shell
  Project lifecycle header
  Lifecycle state banner
  Primary authority workspace
  Supporting output rail
  History and evidence surface, if feasible within the approved slice
```

The first slice must preserve existing feature components where practical. It should reshape shell composition and state hierarchy, not rewrite Matrix, Fee, Project Folder, Basic Information, LTR, or lifecycle APIs.

## 4. Required Developer Planning Output

Developer must update this plan before product code and define:

- exact UI slice
- exact file list
- exact tests
- how current `ProjectWorkbenchLayout`, `projectWorkbenchLifecycleSelectors`, and existing Workbench components will be changed
- how TASK_339A readonly model is consumed
- how TASK_339B registry output remains background only
- how TASK_340 shell regions map to current components
- QA smoke checklist and any browser/manual prerequisites

## 5. May Touch

Planner/Integrator may touch:

- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/task_board.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`

Frontend Developer planning may touch:

- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`

Frontend Developer implementation may touch only after user approval of the Developer plan:

- `frontend/src/features/project-workbench/**` files explicitly listed in the approved TASK_341 plan
- `frontend/src/pages/ProjectWorkbenchPage.tsx` only if explicitly listed in the approved TASK_341 plan
- `frontend/src/workbench.css` only for Workbench shell styles explicitly listed in the approved TASK_341 plan
- `frontend/src/api/client.ts` only for consuming already-accepted DTOs, with no API contract change, and only if explicitly listed in the approved TASK_341 plan
- focused frontend tests explicitly listed in the approved TASK_341 plan
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`

## 6. Must Not Touch

- frontend product code before Developer plan approval
- backend implementation
- TASK_338 backend write guards
- database migrations or schema files
- Office gateway internals
- public-drive/LTR authority paths
- Matrix/Fee business rules
- Project Folder backend behavior
- Projects registry implementation beyond accepted TASK_339B context
- TASK_342 task, plan, evidence, QA, or closeout scope
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residual files

## 7. Locked Paths

- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
- frontend Workbench files explicitly listed in the approved TASK_341 plan

## 8. Validation Gate

Before review:

- Developer plan is approved by the user before frontend product code changes.
- Active temporary, active registered without Matrix, active registered with Matrix, stopped, closed completed, and closed administrative shell states are covered.
- Matrix remains the primary authority workspace when active Matrix exists.
- Supporting output surfaces remain compact status/entry surfaces and do not outrank Matrix.
- Stopped and closed states are readonly with visible lifecycle reasons.
- Closed states do not expose Resume.
- Readonly preview/read controls remain available only where TASK_337B/TASK_338 classify them as non-mutating.
- No raw enum words such as `cancelled`, `closed_completed`, or `closed_administrative` appear as user-facing shell copy.
- Current shell does not expose StepInstance, Report generation, AI, permissions, LAN/server, or multi-user controls.
- Narrow viewport preserves lifecycle label, readonly reason, and primary action without overlapping text.
- Keyboard focus order reaches header, banner, primary workspace, supporting outputs, and history/evidence surface in a logical order where those regions exist.
- Focused frontend tests pass.
- Frontend build passes.

## 9. Merge Gate

Reviewer, QA, and Integrator gates are required.

QA is required because this lane changes the main Workbench shell operator flow. QA must include reproducible smoke coverage for active, stopped, closed completed, and closed administrative shell states. Browser/manual smoke may be used if automated coverage cannot inspect layout and workflow behavior sufficiently.

Integrator must exclude external governance/orchestration residuals from TASK_341 packaging unless a separate governance lane explicitly owns them.

## 10. Recommended Developer Stop Point

Next role: Frontend Developer.

Developer should update this plan and evidence, then stop for user approval. Do not write frontend product code in the first Developer pass.

## 10.1 Frontend Developer Planning-First Resolution

### Anti-Skip Statement

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current approved lane: `unified-workbench-shell-implementation` / `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION`.

Allowed role in this pass: Frontend Developer planning first.

This pass does not authorize frontend product code. Frontend implementation remains blocked until the user explicitly approves this updated plan.

### Read-Only Reconnaissance Findings

Current Workbench entry and shell files:

- `frontend/src/pages/ProjectWorkbenchPage.tsx` is a thin route page that loads `useProjectWorkbenchModel(projectId)`, selects `ProjectRuntimeConsoleModel`, and composes `ProjectWorkbenchLayout`.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` currently owns the route-level shell composition, topbar actions, lifecycle readonly banner, non-active-Matrix stage banner/mode surfaces, active Matrix workspace handoff, and project-folder conflict/progress dialogs.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts` already derives temporary planning, registered setup, package preparation, execution console, and readonly lifecycle modes.
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` already contains `WorkbenchStageBanner`, `WorkbenchModeTabs`, `TemporaryPlanningMode`, `RegisteredSetupMode`, and lifecycle management controls.
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` already keeps Matrix as the active workspace and places current Folder Action plus Basic Information summary in a right-side rail.
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts` from TASK_339A already derives business-readable lifecycle readonly copy.
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts` from TASK_339B is registry-only background and should not be imported into Workbench shell implementation.
- `frontend/src/workbench.css` already contains shell, stage banner, active Matrix, lifecycle, and responsive styles.

Current shell gaps to address in TASK_341:

- The topbar shows identity and actions, but not a durable lifecycle header with lifecycle badge, formal identity marker, Matrix authority marker, and timestamp/reason context.
- The active Matrix path jumps directly into the Matrix workspace and only shows readonly lifecycle banner when stopped/closed. It lacks the TASK_340 shell grammar of `Project State`, `Matrix`, `Outputs`, and current evidence/history context.
- The non-active-Matrix path still relies on stage banner plus mode-specific panels. It can be reshaped without rewriting Matrix/Fee/Project Folder internals.
- A disabled `View activity history` button currently advertises a planned future surface. TASK_341 first slice should remove that disabled future action rather than expose unavailable future scope.
- Existing tests already cover many lifecycle/no-active-Matrix and active-Matrix behaviors. TASK_341 should add focused shell tests instead of broad snapshot tests.

### First Controlled Implementation Slice

TASK_341 implementation should be frontend-only and limited to one Workbench shell slice:

1. Add a pure Workbench shell model selector that maps existing runtime state into TASK_340 shell regions:
   - lifecycle header: lifecycle label, formal identity marker, Matrix authority marker, timestamp/reason line, primary action label
   - lifecycle banner: active/stopped/closed copy from TASK_339A readonly model and TASK_340 shell copy
   - primary workspace kind: `temporary_planning`, `matrix_setup`, `active_matrix`, or `readonly_archive`
   - supporting output rail entries for current features only: Basic Information, Project Folder, Required Forms, Fee Evaluation, LTR/Public Drive when current model fields support them
   - history/evidence summary limited to current data: lifecycle timestamp/reason/close summary warnings and existing Matrix authority/history signals where available
2. Update `ProjectWorkbenchLayout` to render the new shell grammar while preserving existing feature components:
   - header region named `Project State`
   - primary region named `Matrix`
   - output/supporting region named `Outputs`
   - optional current-data-only region named `History`
   - no disabled future history button
3. Preserve the active Matrix workspace as the visual primary work surface when `activeConfirmedMatrixSnapshot` exists.
4. Keep stopped projects readable and readonly, with Resume/Close only if existing lifecycle UI/API surfaces already support those actions. Because current `ProjectWorkbenchLayout` does not yet implement resume/close lifecycle action controls, TASK_341 first slice must not invent them. It should show the business-readable readonly reason and keep current read/preview surfaces visible.
5. Keep closed completed and closed administrative projects readonly archives and do not render Resume, Stop, Close again, Delete, or other lifecycle write actions.
6. Do not alter backend lifecycle API shape, TASK_338 guards, Matrix/Fee/Folder business rules, registry behavior, or future execution/reporting scope.

### Explicit Implementation File List After User Approval

Create:

- `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
  - Pure selector/model for TASK_340 shell regions, labels, current-feature-only output rail entries, lifecycle archive summary, and user-facing copy.
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`
  - Pure tests for active temporary, active registered without Matrix, active registered with Matrix, stopped, closed completed, closed administrative, raw enum hiding, and current-feature-only exclusions.

Modify:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - Consume `deriveProjectWorkbenchShellModel(...)`.
  - Render Project State header fields and lifecycle badge.
  - Render shell region wrappers around existing stage banner, mode surfaces, and active Matrix workspace.
  - Remove the disabled planned `View activity history` button.
  - Keep existing dialog/write handlers unchanged except for shell-level visibility and readonly presentation.
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - Add narrow presentational components if needed for shell header, output rail, or history summary.
  - Preserve `TemporaryPlanningMode`, `RegisteredSetupMode`, `WorkbenchStageBanner`, and lifecycle management behavior.
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - Add or adjust labels/wrappers so active Matrix remains the primary `Matrix` workspace and the existing Folder Action / Basic Information side content reads as supporting output rail.
  - Do not change Matrix projection, token selection, folder task decision logic, or Basic Information summary behavior.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - Only if required to expose stable mode/tone data to the shell model. Do not change lifecycle state semantics beyond the approved tests.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
  - Only if selector output changes are needed for shell model integration.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - Add focused component tests for shell regions, lifecycle header labels, Matrix-primary ordering, closed/stopped readonly behavior, and future-scope exclusions.
- `frontend/src/workbench.css`
  - Add or adjust Workbench shell layout classes for header, region labels, output rail, readonly archive summary, and responsive behavior.
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
  - Record implementation summary, validation, QA prerequisites, risks, and stop point.

Not planned for TASK_341 implementation:

- `frontend/src/api/client.ts`, because the required lifecycle/runtime data already exists.
- `frontend/src/pages/ProjectWorkbenchPage.tsx`, unless implementation reveals a route-level accessibility wrapper is strictly necessary. If touched, Reviewer should treat that as a plan deviation requiring explicit evidence.
- Projects registry files from TASK_339B.
- Backend, tests outside frontend, Office gateways, database/migrations, task board, TASK_342 files.

### Shell State Contract

Active temporary/no-LTR project:

- Header label: `Active`
- Formal identity marker: `Temporary planning`
- Matrix marker: `No Matrix` or `Candidate Matrix`
- Primary workspace: temporary planning / Matrix planning
- Supporting outputs: compact current-feature statuses only; no Project Folder package generation as the primary focus
- Write controls remain governed by existing active-state business rules

Active registered project without active Matrix:

- Header label: `Active`
- Formal identity marker: `Registered project`
- Matrix marker: `Candidate Matrix` or `No Matrix`
- Primary workspace: Matrix authority setup
- Supporting outputs remain secondary and must not visually outrank Matrix

Active registered project with active Matrix:

- Header label: `Active`
- Formal identity marker: `Registered project`
- Matrix marker: `Active Matrix`
- Primary workspace: active Matrix authority workspace
- Supporting outputs: Folder Action, Basic Information, Required Forms/Fee/Public Drive status entries where current data exists
- Matrix must appear before output rail in DOM and visual hierarchy

Stopped project:

- Header label: `Stopped`
- Banner: `Stopped project` and `This project is paused. Resume it before making changes.`
- Primary workspace: readonly version of the same appropriate workspace
- Read/preview surfaces remain visible where existing TASK_339A/TASK_338 behavior permits them
- Do not render Stop/Delete. Do not invent Resume/Close if current UI/API wiring is not already present in this slice.

Closed completed project:

- Header label: `Closed: Completed`
- Banner: `Project closed as completed` or accepted TASK_339A business-readable equivalent
- Primary workspace: readonly archive view using current data
- No Resume, Stop, Close, Delete, Matrix edit, folder generation, Required Forms generation, public-drive upload, or other write action

Closed administrative project:

- Header label: `Closed: Administrative`
- Banner: `Project closed administratively` or accepted TASK_339A business-readable equivalent
- Primary workspace: readonly archive view using current data
- No Resume, Stop, Close, Delete, Matrix edit, folder generation, Required Forms generation, public-drive upload, or other write action

### Testing Plan After User Approval

Pure shell model tests:

```powershell
cd frontend
npm test -- --run src/features/project-workbench/projectWorkbenchShellModel.test.ts
```

Required assertions:

- active temporary/no-LTR project maps to `Temporary planning`, `No Matrix` or `Candidate Matrix`, and primary workspace `temporary_planning`
- active registered without Matrix maps to `Registered project`, `Matrix authority setup`, and primary workspace `matrix_setup`
- active registered with active Matrix maps to `Registered project`, `Active Matrix`, and primary workspace `active_matrix`
- stopped project maps to business-readable `Stopped` copy and readonly reason
- closed completed maps to `Closed: Completed` and no Resume/Stop/Close/Delete action model
- closed administrative maps to `Closed: Administrative` and no Resume/Stop/Close/Delete action model
- output rail includes only current features and excludes Report generation, StepInstance, AI, permissions, LAN/server, and multi-user labels
- model output does not expose raw enum words such as `cancelled`, `closed_completed`, `closed_administrative`, `lifecycle_state`, or `closure_type`

Focused Workbench component tests:

```powershell
cd frontend
npm test -- --run src/features/project-workbench/projectWorkbenchLayout.test.tsx src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts
```

Required assertions:

- Project State header is visible for active temporary, active registered, stopped, closed completed, and closed administrative states
- active registered with active Matrix renders the Matrix workspace before Outputs in document order
- stopped no-active-Matrix shell keeps readonly stage information visible and does not render `Stop project`, `Delete temporary project`, `Edit Matrix`, or `Confirm Matrix authority`
- closed completed and closed administrative shells do not render `Resume`, `Stop project`, `Close project`, `Delete temporary project`, `Edit Matrix`, `Confirm Matrix authority`, `Generate project folder`, `Update project folder`, `Collect request material`, `Upload to public drive`, or `Generate Required forms`
- active Matrix shell retains current `Matrix Editor`, `Fee Evaluation`, and `Basic Information` navigation when active and writable
- disabled future `View activity history` action is absent
- no raw enum copy appears in rendered shell

Build validation:

```powershell
cd frontend
npm run build
```

Whitespace/scope validation:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md
git status --short -- backend tests docs/task_board.md tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md
```

Expected:

- focused frontend tests pass
- frontend build passes
- no backend files changed
- no product tests outside the explicitly listed frontend test files changed
- `docs/task_board.md` unchanged by Developer implementation
- TASK_342 files absent or unchanged

### QA Smoke Checklist For Post-Reviewer Gate

QA is required after Reviewer pass because TASK_341 changes the main Workbench operator flow.

QA should smoke at least:

- active temporary/no-LTR project: Project State header, Temporary planning primary area, no future-scope actions
- active registered without active Matrix: Matrix authority setup is primary
- active registered with active Matrix: Matrix appears as primary workspace before Outputs; output rail is compact
- stopped project: readonly reason visible; read surfaces remain visible; write controls hidden/disabled
- closed completed project: readonly archive, no Resume/Stop/Close/Delete, completed label visible
- closed administrative project: readonly archive, no Resume/Stop/Close/Delete, administrative label visible
- narrow viewport: lifecycle label, readonly reason, primary workspace, and output rail do not overlap
- keyboard order: Back to projects, Project State header/action area, lifecycle banner, Matrix/primary workspace, Outputs, History where present

### Risks And Mitigations

Risk: Workbench shell implementation becomes a rewrite.

Mitigation: create one pure shell model and wrap existing Workbench components. Do not rewrite Matrix, Fee, Basic Information, Project Folder, or runtime model internals.

Risk: Matrix loses priority to output status cards.

Mitigation: active Matrix state must render Matrix workspace before Outputs in both DOM and visual hierarchy, with tests asserting order.

Risk: TASK_341 exposes future History, Report, execution, or AI features.

Mitigation: remove disabled future history button; history/evidence summary uses only current lifecycle/runtime data. Tests assert future-scope labels are absent.

Risk: Closed/stopped readonly behavior regresses.

Mitigation: reuse TASK_339A readonly model, keep current guarded write suppression, and add focused tests for closed/stopped action absence.

Risk: Responsive shell overlaps on small screens.

Mitigation: constrain shell header/rail CSS with wrapping grid tracks and require QA narrow-viewport smoke before merge.

### Developer Planning Gate Decision

Developer planning gate: ready.

Reason: TASK_340 accepted IA is implementable as a frontend-only first slice with existing TASK_339A lifecycle data and existing Workbench components. No backend/API change is needed for the first slice.

Implementation remains blocked until the user explicitly approves this Developer plan.

## 11. Planner Validation Commands

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Test-Path tasks\TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md
Test-Path docs\task_341_unified_project_workbench_shell_implementation_plan.md
Test-Path docs\lane_evidence\TASK_341_unified-workbench-shell-implementation_developer.md
Select-String -Path docs\task_board.md -Pattern 'unified-workbench-shell-implementation' -Encoding UTF8
Select-String -Path docs\task_341_unified_project_workbench_shell_implementation_plan.md -Pattern 'Planner gate: ready' -Encoding UTF8
Select-String -Path docs\task_341_unified_project_workbench_shell_implementation_plan.md -Pattern 'QA is required' -Encoding UTF8
rg -n "[ \t]$" tasks\TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md docs\task_341_unified_project_workbench_shell_implementation_plan.md docs\lane_evidence\TASK_341_unified-workbench-shell-implementation_developer.md docs\task_board.md
git diff --check -- tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md docs/task_341_unified_project_workbench_shell_implementation_plan.md docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md docs/task_board.md
```

## 12. Stop Point

TASK_341 implementation is complete and accepted after Reviewer implementation gate, QA gate, and Integrator packaging/readiness gate.

Stop here. Do not start TASK_342, backend closeout, Report generation, StepInstance, AI, permissions, LAN/server, or multi-user scope until Planner/Integrator creates or activates a separate approved lane.
