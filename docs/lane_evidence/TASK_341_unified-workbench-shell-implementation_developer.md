# Developer Evidence - TASK_341 Unified Project Workbench Shell Implementation

Status: implementation complete - pending review
Task: TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION
Lane: unified-workbench-shell-implementation
Role: Frontend Developer
Last Updated: 2026-06-27

## Approval

Planner created and activated this formal planning-first lane after the user explicitly requested `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION`.

This evidence file is initialized by Planner as the lane evidence anchor. Frontend Developer must update it during the planning-first pass and stop for user approval before product code changes.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## Why This Lane Is Allowed

- `TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT` is complete and accepted.
- `TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE` is complete and accepted.
- `TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION` is complete and accepted.
- `TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL` is complete and accepted.
- `TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS` is complete and accepted.
- `TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN` is complete and accepted as planning output only.
- `docs/task_board.md` reports no active implementation lane and calls for Planner creation or activation of the next formal planning-first lane.

## Goal

Plan first, then implement the first controlled frontend slice of the Unified Project Workbench Shell. Preserve existing feature components where practical, keep Matrix as the primary authority workspace, and make active/stopped/closed lifecycle state visible in the shell.

## May Touch

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
- this evidence file

## Must Not Touch

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

## Locked Paths

- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
- frontend Workbench files explicitly listed in the approved TASK_341 plan

## Validation Gate

- Developer plan approved by user before frontend product code changes.
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

## Merge Gate

Reviewer, QA, and Integrator gates are required.

QA is required because this lane changes the main Workbench shell operator flow. QA must include reproducible smoke coverage for active, stopped, closed completed, and closed administrative shell states.

Merge remains blocked if backend code is changed, TASK_342 closeout is mixed in, Projects registry redesign beyond TASK_339B appears, future scope appears, Matrix loses primary priority, or unrelated governance/orchestration residuals are packaged as TASK_341 product work.

## Commands Or Checks Run

Planner activation:

- Read `AGENTS.md`.
- Read `docs/task_board.md`.
- Read `.agents/skills/connlab-lane-orchestrator/SKILL.md`.
- Read `.agents/skills/connlab-planner/SKILL.md`.
- Read `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`.
- Read `docs/project_management/PARALLEL_EXECUTION_MODEL.md`.
- Read `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`.
- Read `docs/project_management/ROLE_THREAD_REGISTRY.md`.
- Loaded `$impeccable` product-register context from `PRODUCT.md` and `DESIGN.md`.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.
- Read TASK_336 task and contract plan.
- Read TASK_339A task, plan, and evidence.
- Read TASK_339B task and evidence.
- Read TASK_340 task, plan, and evidence.
- Checked expected TASK_341/TASK_342 formal files before creation.
- Inspected current Workbench frontend entry points read-only:
  - `frontend/src/pages/ProjectWorkbenchPage.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
  - `frontend/src/workbench.css`
- Created TASK_341 task, plan, and evidence files.
- Updated `docs/task_board.md` to mark TASK_341 as the approved planning-first lane.
- Did not modify `frontend/`, `backend/`, `tests/`, TASK_342 files, or unrelated governance/orchestration residual files.

Planner validation:

- `Test-Path tasks\TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md` -> true.
- `Test-Path docs\task_341_unified_project_workbench_shell_implementation_plan.md` -> true.
- `Test-Path docs\lane_evidence\TASK_341_unified-workbench-shell-implementation_developer.md` -> true.
- `Select-String -Path docs\task_board.md -Pattern 'unified-workbench-shell-implementation' -Encoding UTF8` -> matches found.
- `Select-String -Path docs\task_341_unified_project_workbench_shell_implementation_plan.md -Pattern 'Planner gate: ready' -Encoding UTF8` -> matches found.
- `Select-String -Path docs\task_341_unified_project_workbench_shell_implementation_plan.md -Pattern 'QA is required' -Encoding UTF8` -> matches found.
- `rg -n "[ \t]$" tasks\TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md docs\task_341_unified_project_workbench_shell_implementation_plan.md docs\lane_evidence\TASK_341_unified-workbench-shell-implementation_developer.md docs\task_board.md` -> no matches.
- `git diff --check -- tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md docs/task_341_unified_project_workbench_shell_implementation_plan.md docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md docs/task_board.md` -> passed; Git reported only a CRLF working-copy warning for `docs/task_board.md`.
- `git status --short -- frontend backend tests tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md docs/task_341_unified_project_workbench_shell_implementation_plan.md docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md docs/task_board.md` -> only TASK_341 planning/evidence files and `docs/task_board.md` changed; no `frontend/`, `backend/`, or `tests/` output.

## Stop Point

Planner gate is ready.

Next role: Frontend Developer planning-first pass.

Developer must update `docs/task_341_unified_project_workbench_shell_implementation_plan.md` and this evidence file, then stop for user approval before frontend product code changes. Do not route directly to implementation, Reviewer, QA, Integrator, or TASK_342 before that planning gate is complete.

## Frontend Developer Planning-First Pass

Date: 2026-06-27

### Anti-Skip Confirmation

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION`.
- Current lane: `unified-workbench-shell-implementation`.
- Current role: Frontend Developer planning first.
- Allowed reason: `docs/task_board.md` marks TASK_341 as approved for Developer planning first, and the user explicitly requested this planning-first pass.

### Inputs Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` product-register context from `PRODUCT.md` and `DESIGN.md`
- `$impeccable` product reference guidance
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`
- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- this evidence file

### Read-Only Frontend Reconnaissance

Inspected without modifying product code:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/workbench.css`

Findings:

- Existing route page is already thin; no route-page change is planned for the first slice.
- Existing Workbench layout owns shell composition and is the right integration point.
- TASK_339A readonly model and lifecycle API data are already available through `runtimeModel.lifecycle`.
- TASK_339B registry helpers are registry-only background and should not be imported into the Workbench shell.
- Active Matrix workspace already keeps Matrix visually primary, with Folder Action and Basic Information summary as supporting side content.
- Current non-active-Matrix path can be reshaped by wrapping existing stage/mode components rather than rewriting them.
- The disabled `View activity history` future action should be removed from the TASK_341 implementation slice because current-feature-only UI must not advertise unavailable future surfaces.

### Plan Updates Made

Updated `docs/task_341_unified_project_workbench_shell_implementation_plan.md` to define:

- anti-skip and planning gate status
- read-only reconnaissance findings
- first controlled implementation slice
- exact frontend file list after user approval
- shell state contract for active temporary, active registered without Matrix, active registered with Matrix, stopped, closed completed, and closed administrative states
- pure shell model test plan
- focused Workbench component test plan
- build, diff, and scope validation commands
- QA smoke checklist for the required QA gate
- risks and mitigations
- Developer planning gate decision: ready

### Developer Planning Decision

Developer planning gate: ready.

The TASK_341 first slice is implementable as frontend-only shell composition using existing lifecycle/runtime data and existing Workbench components. No backend/API change is needed.

Product code remains blocked until the user explicitly approves this Developer plan.

### Scope Held

- Did not modify `frontend/`.
- Did not modify `backend/`.
- Did not modify `tests/`.
- Did not update global `docs/task_board.md`.
- Did not modify TASK_342 files.
- Did not merge, commit, or push.

### Validation

- Required file existence check for AGENTS, board, orchestration protocol, role registry, TASK_336/TASK_339A/TASK_339B/TASK_340/TASK_341 task/plan/evidence inputs -> all returned `True`.
- `rg -n "[ \t]$" docs\task_341_unified_project_workbench_shell_implementation_plan.md docs\lane_evidence\TASK_341_unified-workbench-shell-implementation_developer.md` -> no matches.
- `git diff --check -- docs/task_341_unified_project_workbench_shell_implementation_plan.md docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md` -> passed.
- `git status --short -- frontend backend tests` -> no output.
- `git status --short -- docs/task_board.md tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md docs/task_341_unified_project_workbench_shell_implementation_plan.md docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md` -> `docs/task_board.md` is modified and TASK_341 task/plan/evidence are untracked in the current packaging state. The Developer planning-first pass only edited the two allowed TASK_341 docs; `docs/task_board.md` and the TASK_341 task file remain Planner/Integrator packaging scope.

### Stop Point

Stop after documentation validation and completion callback.

Do not implement frontend code, route to Reviewer/QA/Integrator, update `docs/task_board.md`, start TASK_342, merge, commit, or push.

## Frontend Developer Implementation Pass

Date: 2026-06-27

### Approval And Anti-Skip Confirmation

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION`.
- Current lane: `unified-workbench-shell-implementation`.
- Current role: Frontend Developer implementation pass.
- Allowed reason: Developer planning-first completed, and the user explicitly approved the TASK_341 implementation pass while preserving Reviewer, QA, and Integrator gates.

### Implementation Summary

Implemented the approved first controlled frontend slice of the Unified Project Workbench Shell:

- Added a pure `projectWorkbenchShellModel` selector for lifecycle label, formal identity marker, Matrix authority marker, primary workspace, current-feature-only output entries, and current lifecycle evidence.
- Updated `ProjectWorkbenchLayout` to render named shell regions: `Project State`, `Lifecycle state`, `Matrix`, `Outputs`, and current-data-only `History` when evidence exists.
- Removed the disabled planned `View activity history` action from the Workbench shell.
- Kept active Matrix as the primary workspace and rendered `Outputs` after `Matrix` in DOM order.
- Preserved existing feature components and behavior for Matrix, Folder Action, Basic Information, Fee Evaluation, lifecycle readonly suppression, dialogs, and package/folder actions.
- Hid the active Matrix `Matrix Editor` write entry while lifecycle readonly is active, while retaining read/navigation-oriented surfaces already present in this slice.
- Added focused tests for active temporary, active registered without Matrix, active registered with Matrix, stopped, closed completed, closed administrative, raw enum hiding, current-feature-only output labels, Matrix-before-Outputs order, and closed/stopped write-action absence.

### Changed Files

- Created `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`.
- Created `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`.
- Modified `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`.
- Modified `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`.
- Modified `frontend/src/workbench.css`.
- Updated this evidence file.

Files explicitly avoided:

- Did not touch `frontend/src/pages/ProjectWorkbenchPage.tsx`; no route-level wrapper was necessary.
- Did not touch `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`; the existing active Matrix workspace remained compatible.
- Did not touch `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`; existing stage/mode components were preserved.
- Did not touch `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts` or its test; shell integration did not require selector semantics changes.
- Did not touch backend, product tests outside the approved frontend test files, TASK_342 files, or `docs/task_board.md`.

### Validation Run

TDD/red check:

- `npm test -- --run src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` initially failed as expected before implementation because the shell model/regions were not yet present and the disabled future activity action still existed.

Focused frontend tests:

- `npm test -- --run src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx` -> `2 passed`, `40 passed`.
- `npm test -- --run src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts` -> `3 passed`, `57 passed`.

Build:

- `npm run build` -> passed. Vite reported the existing chunk-size warning for a minified JS chunk over 500 kB; no build error.

Diff and scope validation:

- `git diff --check -- frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md` -> passed; Git reported CRLF working-copy warnings only.
- `rg -n "[ \t]$" frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md` -> no matches.
- `git status --short -- backend tests docs/task_board.md tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md docs/lane_evidence/TASK_342_lifecycle-integration-qa-closeout_planner.md` -> only `M docs/task_board.md`, which was a pre-existing governance/packaging residual before this implementation pass; no backend, `tests/`, or TASK_342 files were changed by this pass.
- `git status --short -- frontend/src/features/project-workbench/projectWorkbenchShellModel.ts frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/workbench.css docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md frontend/src/pages/ProjectWorkbenchPage.tsx` -> changed files are limited to `ProjectWorkbenchLayout.tsx`, `ProjectWorkbenchLayout.test.tsx`, `workbench.css`, new shell model/test files, and this evidence file. `ProjectWorkbenchPage.tsx`, `ProjectWorkbenchActiveMatrixWorkspace.tsx`, `ProjectWorkbenchLifecycleSections.tsx`, and lifecycle selector files were not changed.

### Responsive And Keyboard Smoke Evidence

Automated component coverage verifies logical DOM order: `Project State` header is present, `Matrix` appears before `Outputs`, and closed/stopped readonly states keep readable regions while removing lifecycle write entries.

CSS changes add wrapping Project State badges, constrained shell region grids, responsive one-column shell banner layout, and a two-column output rail at narrow widths. Browser/manual narrow viewport smoke still belongs to the required QA gate after Reviewer pass.

### Risks And Follow-Ups

- QA remains required after Reviewer pass because this changes the main Workbench shell operator flow.
- Browser/manual QA should verify narrow viewport overlap and keyboard order in a real browser because JSDOM component tests do not measure visual overlap.
- The Vite chunk-size warning remains a general frontend packaging follow-up and is not introduced by this lane.
- `docs/task_board.md` was already modified before this implementation pass; Developer did not edit it.

### Stop Point

Status: implementation complete - pending review.

Stop after implementation, evidence update, validation, and callback. Do not route directly to QA/Integrator, update `docs/task_board.md`, start TASK_342, merge, commit, or push.

## Integrator Packaging / Readiness Gate

Date: 2026-06-27

Reviewer latest conclusion:

- Completion status: `reviewer_pass`
- `Reviewer implementation gate: pass`
- QA required.
- Reviewer rerun: focused frontend tests `3` files / `57` tests passed; frontend build passed with existing Vite chunk-size warning only.
- No blocking findings.

QA latest conclusion:

- Completion status: `qa_pass`
- `QA gate: pass`
- Evidence: `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_qa.md`
- Focused Workbench shell tests passed: `3` files / `57` tests.
- Frontend build passed with existing Vite chunk-size warning only.
- Source/static checks found no runtime future-scope controls or raw closed enum shell copy.
- Residual non-blocking risk: no browser screenshot/tab-order tool was available to QA, so narrow viewport overlap and real tab order were covered by static/component checks only.

Package accepted files:

- `docs/task_board.md`
- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_qa.md`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.ts`
- `frontend/src/features/project-workbench/projectWorkbenchShellModel.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`

Explicitly excluded dirty governance/orchestration residuals:

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/`
- `.agents/skills/connlab-planner/`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

Integrator validation rerun:

- `npm test -- --run src/features/project-workbench/projectWorkbenchShellModel.test.ts src/features/project-workbench/ProjectWorkbenchLayout.test.tsx src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts` -> passed, `3` files and `57` tests.
- `npm run build` -> passed with existing Vite chunk-size warning only.
- `git diff --check -- <TASK_341 package files>` -> passed; CRLF normalization warnings only.
- `git diff --cached --check` after staging the accepted package -> passed.
- `git diff --cached --name-only -- AGENTS.md .agents docs/project_management backend tests tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md docs/lane_evidence/TASK_342_lifecycle-integration-qa-closeout_planner.md` -> no output.

Integrator decision: `Integrator gate: accepted`.

Stop point: TASK_341 is complete. Do not start TASK_342, backend closeout, Report generation, StepInstance, AI, permissions, LAN/server, or multi-user scope until Planner/Integrator creates or activates a separate approved lane.
