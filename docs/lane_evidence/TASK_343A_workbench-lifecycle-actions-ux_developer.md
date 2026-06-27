# Developer Evidence - TASK_343A Workbench Lifecycle Actions UX

Status: integrator accepted
Task: TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX
Lane: workbench-lifecycle-actions-ux
Role: Frontend Developer
Updated: 2026-06-27

## Planner Activation Summary

Planner created this evidence file as the lane evidence anchor, following the local convention for implementation lanes. Developer owns future updates.

This lane is approved for Developer planning-first only. Developer must update `docs/task_343a_workbench_lifecycle_actions_ux_plan.md` and this evidence file, then stop for user approval before product code changes.

## Source Facts

- Parent `TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX` passed Reviewer plan gate.
- Reviewer accepted B1 fix: TASK_343A must withhold all Close controls.
- Existing frontend client functions are present:
  - `stopProjectLifecycle(...)`
  - `resumeProjectLifecycle(...)`
- Existing close client functions are present but locked for this lane:
  - `closeProjectCompletedLifecycle(...)`
  - `closeProjectAdministrativeLifecycle(...)`
- TASK_337A backend lifecycle/API shape is complete.
- TASK_338 write guards are complete.
- TASK_339A frontend readonly model is complete.
- TASK_340 shell plan is accepted.
- TASK_341 shell implementation is complete.

## Lane Goal

Plan, then after separate user approval implement frontend Workbench Stop/Resume lifecycle action UX only.

## May Touch

Planner activation may touch:

- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- `docs/task_board.md`

Developer planning-first may touch:

- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`

Implementation may touch only after explicit user approval of the Developer planning pass and only files listed in the approved plan.

## Must Not Touch

- `backend/`
- backend API/schema/write guards
- `frontend/src/api/client.ts`
- root `tests/`
- Projects registry implementation
- any Close controls, Close placeholders, Close routing targets, Close dialogs, output summary acknowledgement, close note/reason fields, post-close archive transition, or close API calls
- TASK_343B/TASK_343C files
- Matrix/Fee/Folder/Basic Information/LTR/Required Forms/Public Drive business rules
- Report generation
- StepInstance/execution persistence
- AI, permissions, LAN/server, multi-user scope
- unrelated governance/orchestration residuals

## Locked Paths

- `backend/`
- `tests/`
- `frontend/src/api/client.ts`
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- parent TASK_343 task/plan/evidence files
- TASK_336 through TASK_342 task/plan/evidence files, except read-only reference

## Validation Gate

Developer planning-first must define exact validation before implementation. Minimum expected validation:

- focused Workbench/project-lifecycle component/model tests
- frontend build
- assertions that active and stopped states expose Stop/Resume correctly
- assertions that closed states expose neither Stop nor Resume
- assertions that no Close controls or close API calls are introduced
- QA smoke plan for Active Matrix workspace, registered setup, stopped, and closed states

## Merge Gate

Merge remains blocked until:

- Developer planning-first is approved by user before code
- implementation evidence is ready
- Reviewer has no blocking findings
- QA passes or records accepted non-blocking residuals
- Integrator confirms clean package scope

## Planner Activation Validation

Checks run by Planner:

```powershell
Test-Path tasks\TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md
Test-Path docs\task_343a_workbench_lifecycle_actions_ux_plan.md
Test-Path docs\lane_evidence\TASK_343A_workbench-lifecycle-actions-ux_developer.md
Select-String -Path docs\task_board.md -Pattern 'TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX' -Encoding UTF8
Select-String -Path docs\task_343a_workbench_lifecycle_actions_ux_plan.md -Pattern 'Planner gate: ready' -Encoding UTF8
git diff --check -- tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md docs/task_board.md
```

Results:

- TASK_343A task, plan, and evidence files exist.
- `docs/task_board.md` contains the `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` / `workbench-lifecycle-actions-ux` approved lane row.
- TASK_343A plan contains `Planner gate: ready`.
- TASK_343A task/plan/evidence contain the required no-Close boundary.
- `git diff --check -- ...` passed with only the existing `docs/task_board.md` CRLF working-copy warning.
- No frontend/backend/product code validation was run because Planner activation did not modify product code.

## Developer Planning-First Pass

Date: 2026-06-27

### Anti-Skip Confirmation

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task/lane: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` / `workbench-lifecycle-actions-ux`.
- Current role: Frontend Developer planning-first.
- Allowed reason: `docs/task_board.md` marks TASK_343A as approved for Developer planning-first only, and the user explicitly requested this pass.
- Stop point: update TASK_343A plan/evidence only, then stop for Reviewer plan gate / user approval before product code.

### Required Inputs Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `$impeccable` `PRODUCT.md`, `DESIGN.md`, and product-register guidance
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- Relevant TASK_337A, TASK_338, TASK_339A, TASK_340, and TASK_341 task/plan/evidence inputs
- Read-only frontend source inspection under `frontend/src/api/client.ts`, `frontend/src/features/project-lifecycle/`, and `frontend/src/features/project-workbench/`

### Planning Findings

- Existing lifecycle client support is sufficient. `frontend/src/api/client.ts` exports `stopProjectLifecycle(...)`, `resumeProjectLifecycle(...)`, and lifecycle DTOs. No API-client change is needed.
- Close lifecycle helpers also exist in the client, but TASK_343A must not import or call them.
- Current Workbench Stop path still uses legacy `stopProject(...)`, browser `prompt`/`confirm`, and `onBack()` after success. The implementation plan now requires replacing this with lifecycle API actions and in-place Workbench refresh.
- Current Workbench has no Resume UI. The plan now defines a stopped readonly Resume action using the same compact inline confirmation pattern.
- `useProjectWorkbenchModel.onRefreshLifecycle()` refreshes lifecycle only. The plan now requires Stop/Resume success to refresh both lifecycle and `Project.status`/identity so legacy `cancelled` compatibility does not leave Resume in a stale stopped branch.
- Active Matrix workspace currently keeps Matrix primary but lacks a lifecycle Stop action area. The plan now requires a compact lifecycle action area that remains subordinate to Project State and does not displace Matrix.
- Existing TASK_339A/TASK_341 readonly behavior suppresses stopped/closed write surfaces; TASK_343A should preserve that behavior and add only the allowed Resume path for stopped projects.

### Plan Updates Made

Updated `docs/task_343a_workbench_lifecycle_actions_ux_plan.md` with:

- Developer planning-first anti-skip confirmation.
- Current code inspection summary.
- Exact implementation file list.
- Explicit API/DTO usage and API-client lock.
- Display-only lifecycle action model rules.
- Inline Stop confirmation UX pattern.
- Inline Resume confirmation UX pattern.
- Refresh path requiring lifecycle and project status refresh.
- No-Close enforcement strategy.
- Focused implementation test list.
- Validation commands and static no-Close review.
- Browser/manual QA smoke expectations.
- Planning-pass validation and stop point.

### Approved Implementation File List For Later User Approval

After explicit user approval, implementation may touch only:

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

Locked for TASK_343A implementation:

- `frontend/src/api/client.ts`
- `backend/`
- root `tests/`
- Projects registry files
- TASK_343B/TASK_343C files
- parent TASK_343 files
- TASK_336 through TASK_342 files except read-only reference

### Scope Held

This Developer planning-first pass changed only:

- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`

No frontend product code, backend code, root tests, frontend test source, API client, board closeout, merge, commit, or push was performed.

### Validation Results

Planning validation to run after this evidence update:

```powershell
Test-Path docs\task_343a_workbench_lifecycle_actions_ux_plan.md
Test-Path docs\lane_evidence\TASK_343A_workbench-lifecycle-actions-ux_developer.md
git diff --check -- docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
rg -n "[ \t]$" docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
git status --short -- frontend backend tests docs/task_board.md docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md
```

Results:

- `Test-Path docs\task_343a_workbench_lifecycle_actions_ux_plan.md` -> `True`.
- `Test-Path docs\lane_evidence\TASK_343A_workbench-lifecycle-actions-ux_developer.md` -> `True`.
- `git diff --check -- docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md` -> passed with no output.
- `rg -n "[ \t]$" docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md` -> no matches. Exit code `1` means no trailing whitespace matches.
- `git status --short -- frontend backend tests docs/task_board.md docs/task_343a_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md` ->

```text
 M docs/task_board.md
?? docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
?? docs/task_343a_workbench_lifecycle_actions_ux_plan.md
?? tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md
```

No `frontend/`, `backend/`, or root `tests/` output appeared. `docs/task_board.md` and the TASK_343A task file state are Planner/activation packaging residuals; this Developer planning-first pass edited only the two allowed TASK_343A docs.

### Risks / Follow-Ups

- Browser tooling availability remains a QA-time risk. If unavailable, QA must document residual risk and rely on focused component/static/CSS evidence only if tests and build pass.
- TASK_343A deliberately ignores `allowed_actions` value `close`; close UX remains TASK_343B only.
- Current worktree already has Planner activation residuals (`docs/task_board.md`, TASK_343A task/plan/evidence state). Developer must not package board/task-file changes as implementation work.

### Stop Point

Status: developer planning-first complete - pending user approval.

Next recommended role: Reviewer plan gate.

Do not implement frontend product code, do not update `docs/task_board.md`, do not start TASK_343B/TASK_343C, do not merge, commit, or push.

## Developer Implementation Pass

Date: 2026-06-27

### Anti-Skip Confirmation

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task/lane: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` / `workbench-lifecycle-actions-ux`.
- Current role: Frontend Developer implementation.
- Allowed reason: Reviewer plan gate passed and the user's latest routing instruction explicitly allowed TASK_343A implementation under the approved Workbench Stop/Resume scope.
- Stop point: implementation, evidence, and validation only; stop for Reviewer implementation gate.

### Implementation Summary

- Added a Workbench lifecycle action selector that derives display-only Stop/Resume availability from existing lifecycle DTO `allowed_actions`.
- Replaced the legacy Workbench Stop path that used `stopProject(...)`, `window.prompt`, `window.confirm`, and `onBack()` with an inline Stop confirmation that calls existing `stopProjectLifecycle(...)`.
- Added stopped-project Resume UX with inline confirmation that calls existing `resumeProjectLifecycle(...)`.
- Updated the Workbench model to refresh both lifecycle and `Project.status` after Stop/Resume so legacy `cancelled` compatibility does not leave stale display state after Resume.
- Added compact lifecycle action panel behavior for active Matrix workspace, registered setup, temporary planning, and stopped readonly states.
- Preserved closed completed/admin states as readonly archives with no Stop, Resume, Close, Delete, or placeholder lifecycle write controls.
- Left `frontend/src/api/client.ts` unchanged and used only existing lifecycle client functions.

### Changed Files

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

### TDD Red Result

Initial focused frontend tests failed before implementation, as expected:

- `deriveProjectWorkbenchLifecycleActions is not a function`
- `result.current.onStopLifecycle is not a function`
- `result.current.onResumeLifecycle is not a function`
- Layout still exposed old Stop behavior without inline confirmation / allowed-action gating

### Validation Results

Focused frontend tests:

```powershell
npm test -- --run src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/useProjectWorkbenchModel.test.tsx src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
```

Result:

```text
Test Files 3 passed
Tests 60 passed
```

Frontend build:

```powershell
npm run build
```

Result:

```text
tsc -b && vite build -> passed
```

Build note:

- Vite emitted the existing chunk-size warning for a post-minification JS chunk over 500 kB. This is not introduced by TASK_343A behavior and does not block this lane.

Static checks:

```powershell
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
rg -n "[ \t]$" frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|Close project|Close as completed|Close administratively|output_summary_acknowledged|close_note" frontend/src/features/project-workbench frontend/src/workbench.css
git status --short -- backend tests frontend/src/api/client.ts docs/task_board.md tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md
```

Results:

- `git diff --check -- ...` passed; Git reported only LF/CRLF working-copy warnings for the touched frontend/doc files.
- trailing whitespace scan returned no matches. Exit code `1` means no `rg` matches.
- production no-Close scan returned no matches. Exit code `1` means no `rg` matches.
- forbidden-scope status showed only `M docs/task_board.md`. That file is a pre-existing Planner/activation residual outside this Developer implementation pass and was not modified here.

### No-Close Proof

- TASK_343A implementation does not import or call `closeProjectCompletedLifecycle(...)` or `closeProjectAdministrativeLifecycle(...)`.
- `deriveProjectWorkbenchLifecycleActions(...)` always returns `canClose: false`.
- Workbench Layout tests assert no visible `Close project` button in Stop, Resume, stopped, and closed states.
- Closed completed/admin tests assert no Stop/Resume/Delete lifecycle write affordances.
- `frontend/src/api/client.ts` was not modified.

### Scope Held

- No backend files changed.
- No root `tests/` files changed.
- No Projects registry files changed.
- No TASK_343B/TASK_343C files changed.
- No Close controls, placeholders, route targets, dialogs, output-summary acknowledgement, close note/reason fields, post-close transition, or close API calls were implemented.
- `docs/task_board.md` was not updated by this Developer implementation pass.
- No merge, commit, or push was performed.

### Risks / Follow-Ups

- Browser/manual smoke remains for QA/Reviewer follow-up if required by the lane, especially keyboard order and narrow viewport confirmation panel behavior.
- TASK_343A intentionally ignores backend `allowed_actions` value `close`; TASK_343B owns all Close UX and output-summary/note confirmation work.

### Stop Point

Status: implementation complete - pending review.

Next recommended role: Reviewer implementation gate.

Do not start TASK_343B/TASK_343C, do not update `docs/task_board.md`, do not merge, commit, or push.

## Developer Fix Pass - Reviewer Blocking Finding

Date: 2026-06-27

### Reviewer Blocking Finding

Reviewer implementation gate found one blocking UI issue:

- `.runtime-console-readonly-note` used `border-left: 3px solid var(--color-border-strong)`, which violates the `$impeccable` / frontend architecture ban on thick side-stripe borders.

Reviewer confirmed all functional and scope checks otherwise passed.

### Fix Summary

- Changed `.runtime-console-readonly-note` from a side-stripe expression to a full `1px` border with muted surface background and stable padding.
- Did not change Stop/Resume behavior, copy, API calls, selectors, tests, backend, Projects registry, TASK_343B/TASK_343C, or Close scope.
- Did not add any new `border-left` or `border-right` side stripe greater than `1px`.

### Fix Validation

Validation to run after this evidence update:

```powershell
npm test -- --run src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts src/features/project-workbench/useProjectWorkbenchModel.test.tsx src/features/project-workbench/ProjectWorkbenchLayout.test.tsx
npm run build
git diff --check -- frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
rg -n "[ \t]$" frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.ts frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx frontend/src/workbench.css docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md
rg -n --glob '!*.test.ts' --glob '!*.test.tsx' "closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle|Close project|Close as completed|Close administratively|output_summary_acknowledged|close_note" frontend/src/features/project-workbench frontend/src/workbench.css
git diff -U0 -- frontend/src/workbench.css | rg "^\+.*border-(left|right): [2-9]"
git status --short -- backend tests frontend/src/api/client.ts docs/task_board.md tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md
```

Results:

- Focused frontend tests passed: `3` test files, `60` tests.
- `npm run build` passed; Vite emitted the existing chunk-size warning only.
- `git diff --check -- ...` passed; Git reported only LF/CRLF working-copy warnings for touched frontend/doc files.
- trailing whitespace scan returned no matches. Exit code `1` means no `rg` matches.
- production no-Close scan returned no matches. Exit code `1` means no `rg` matches.
- diff-only thick side-stripe scan returned no matches. Exit code `1` means no added `border-left` / `border-right` greater than `1px` in `frontend/src/workbench.css`.
- forbidden-scope status showed only `M docs/task_board.md`. That file is a pre-existing Planner/activation residual outside this Developer fix pass and was not modified here.

### Fix Stop Point

Status: fix pass complete - pending review.

Next recommended role: Reviewer implementation re-gate.

Stop here. Do not start TASK_343B/TASK_343C, do not update `docs/task_board.md`, do not merge, commit, or push.

## Integrator Packaging Checkpoint

Date: 2026-06-27

### Integrator Gate Result

Integrator gate: blocked.

### Gate Status

- Reviewer implementation re-gate: pass, per delegated QA source fact.
- QA gate: pass, recorded in `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_qa.md`.
- Focused TASK_343A frontend tests rerun by Integrator: passed, `3` files / `60` tests.
- Frontend build rerun by Integrator: passed, with existing non-blocking Vite chunk-size warning only.
- `git diff --check` for TASK_343A package candidates: passed with LF/CRLF working-copy warnings only.
- Trailing whitespace scan: no matches.
- Production no-Close scan: no matches.
- Changed-CSS thick side-stripe scan: no matches.
- Forbidden product scope status: no backend/API/schema/frontend API client/Projects registry/TASK_343B/TASK_343C changes.

### Blocker

Controlled packaging is blocked by board/source consistency risk.

Current `docs/task_board.md` diff from `HEAD` is not a TASK_343A-only closeout. It also introduces the parent `TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX` planning lane as complete/accepted and references these parent lane files:

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`

Those parent files are currently untracked and are locked/excluded from the TASK_343A package boundary. Packaging `docs/task_board.md` as-is would mix parent TASK_343 planning residuals into the TASK_343A commit, while excluding the parent source files would leave the committed board pointing at files not included in the package.

### Clean TASK_343A Package Candidates Verified

- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_qa.md`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`

### Excluded Dirty Paths

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/`
- `.agents/skills/connlab-planner/`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`

### Stop Point

No TASK_343A packaging commit was created.

Recommended next role: Planner/Integrator cleanup decision for the parent TASK_343 planning residual and `docs/task_board.md` source consistency. After parent TASK_343 files and board ownership are cleanly resolved, rerun TASK_343A Integrator packaging/readiness.

## Planner Cleanup Decision - Packaging Source Consistency

Date: 2026-06-27

### Cleanup Result

Planner gate: ready_for_integrator.

The parent TASK_343 planning files are legitimate Planner-owned prerequisite/source-of-truth files for TASK_343A. `docs/task_board.md` records parent TASK_343 as complete/accepted and records TASK_343A as the first child implementation lane. Therefore, TASK_343A packaging may include the parent planning files as source-consistency inputs so the committed board does not point at missing task/plan/evidence sources.

### Integrator May Include

Parent Planner prerequisite/source-consistency inputs:

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- `docs/task_board.md`

TASK_343A package inputs:

- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_qa.md`
- the TASK_343A frontend Workbench files verified by Developer, Reviewer, QA, and Integrator.

### Scope Boundary

Including parent TASK_343 files is a Planner/source-consistency packaging allowance only. It does not make parent TASK_343 files part of TASK_343A product implementation scope, does not expand Developer May Touch, and does not authorize TASK_343B, TASK_343C, Close controls, backend/API/schema changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, or unrelated governance/orchestration residuals.

Integrator should continue excluding unrelated governance/orchestration residuals, including `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*`, unless a separate governance lane owns them.

### Next Role

Recommended next role: Integrator packaging/readiness.

## Integrator Packaging Readiness - Accepted

Date: 2026-06-27

### Integrator Gate Result

Integrator gate: accepted.

### Package Boundary

Parent Planner source-consistency inputs included:

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- `docs/task_board.md`

TASK_343A package files included:

- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_qa.md`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`

Excluded unrelated dirty paths:

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/`
- `.agents/skills/connlab-planner/`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

### Validation Summary

- Reviewer implementation re-gate: pass.
- QA gate: pass.
- Focused TASK_343A frontend tests: passed, `3` files / `60` tests.
- Frontend build: passed, with existing non-blocking Vite chunk-size warning only.
- Package `git diff --check`: passed with LF/CRLF working-copy warnings only.
- Production no-Close scan: no matches.
- Changed-CSS thick side-stripe scan: no matches.
- Forbidden scope status: no backend/API/schema/frontend API client/Projects registry/TASK_343B/TASK_343C changes.

### Stop Point

TASK_343A is locally accepted by Integrator. Remote push was intentionally not performed.

Recommended next role: Planner for TASK_343B creation/activation, or User if the series should pause.
