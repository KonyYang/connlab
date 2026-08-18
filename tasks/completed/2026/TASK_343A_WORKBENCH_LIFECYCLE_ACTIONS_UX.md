# TASK_343A Workbench Lifecycle Actions UX

Status: complete/accepted by Integrator
Lane: workbench-lifecycle-actions-ux
Owner Role: Frontend Developer
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Plan first, then after separate user approval implement the first Workbench lifecycle action UX slice for Stop and Resume only.

TASK_343A must use the accepted lifecycle contract from TASK_336, backend lifecycle API shape from TASK_337A, readonly/write-guard behavior from TASK_338 and TASK_339A, and the first Unified Workbench Shell from TASK_341.

This lane completed the approved Frontend Developer planning-first, implementation, Reviewer re-gate, QA gate, and Integrator packaging/readiness flow.

## 2. Allowed Reason

- Parent `TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX` passed Reviewer plan gate.
- Reviewer accepted the B1 fix: TASK_343A withholds all Close controls.
- Current board has no active implementation lane.
- The user explicitly asked Planner to create/activate `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`.

## 3. Scope

TASK_343A may plan:

- Workbench lifecycle action area for Stop and Resume only.
- Active project Stop action where TASK_337A lifecycle state and allowed actions permit it.
- Stopped project Resume action where TASK_337A lifecycle state and allowed actions permit it.
- Optional reason input for Stop and Resume, matching TASK_337A request DTOs.
- Guarded confirmation pattern for Stop and Resume because they are lifecycle-changing actions.
- Local Workbench lifecycle refresh after Stop/Resume success.
- Business-readable loading, success, and error states.
- Focused component/model tests and QA smoke expectations.

## 4. Hard Boundary

TASK_343A must not implement or expose Close controls in any form.

Forbidden in TASK_343A:

- visible `Close project` buttons
- disabled Close placeholders
- reserved Close controls
- Close menu items
- Close route targets
- non-functional Close affordances
- Close as completed UI
- Close administratively UI
- close confirmation dialogs
- output summary acknowledgement
- close note or administrative reason fields
- post-close archive transition behavior
- close API calls

Those remain TASK_343B only unless a separate approved functional close lane exists before implementation.

## 5. May Touch

Planner activation may touch:

- `tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`
- `docs/task_board.md`

Frontend Developer planning-first may touch:

- `docs/task_343a_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343A_workbench-lifecycle-actions-ux_developer.md`

Frontend implementation may touch only after explicit user approval of the Developer planning pass, and only files confirmed in that approved plan. Likely candidates:

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

## 6. Must Not Touch

- `backend/`
- backend API contract, database schema, migrations, or write guards
- `frontend/src/api/client.ts` unless a separate Planner-approved scope change is created; existing `stopProjectLifecycle` and `resumeProjectLifecycle` functions already exist
- Projects registry implementation beyond read-only reference
- TASK_343B/TASK_343C files unless separately approved
- Close controls or close flows listed in section 4
- Matrix, Fee, Folder, Basic Information, LTR, Required Forms, Public Drive business rules
- Report generation
- StepInstance or execution persistence
- AI, permissions, LAN/server, or multi-user scope
- unrelated governance/orchestration residuals

## 7. Locked Paths

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts`
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- parent `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- parent `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- parent `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- TASK_336 through TASK_342 task/plan/evidence files, except read-only reference

Packaging note: parent TASK_343 files remain locked for Developer/QA/product implementation changes. A Planner cleanup decision on 2026-06-27 permits Integrator to include the parent TASK_343 task, plan, evidence, and `docs/task_board.md` as Planner-owned prerequisite/source-consistency inputs when packaging TASK_343A. This does not authorize product code changes, Close controls, TASK_343B/TASK_343C, backend/API/schema changes, or unrelated governance/orchestration residuals.

## 8. Validation Gate

Developer planning-first must define exact validation before implementation. Minimum implementation validation must include:

- Active project shows Stop action where allowed.
- Stop action uses a guarded confirmation with optional reason.
- Stopped project shows readonly reason and Resume action where allowed.
- Resume action uses a guarded confirmation or explicit intentional action pattern with optional reason, refreshes Workbench lifecycle state, and restores active progression.
- Active Matrix workspace keeps Matrix primary while lifecycle actions remain reachable.
- Registered setup state exposes Stop and no Close controls.
- Temporary planning state exposes Stop and no Close controls.
- Closed completed/admin states do not show Resume and do not show any TASK_343A Close controls.
- Stopped readonly write controls remain blocked through existing TASK_339A/TASK_338 behavior.
- No `Close project`, close placeholders, close routes, close dialogs, close note/reason fields, output summary acknowledgement, or close API calls are added.
- Focused component/model tests pass.
- Frontend build passes or any unrelated build blocker is recorded with evidence.
- Browser/manual smoke covers at least Active Matrix workspace and registered setup lifecycle action placement. If browser tooling is unavailable, QA must record a residual-risk disposition.

## 9. Reviewer / QA / Merge Gates

Reviewer gate is required after Developer implementation.

QA gate is required because this lane changes the main Workbench operator flow and lifecycle actions.

Integrator may accept only after:

- Developer evidence records completed implementation and validation.
- Reviewer has no blocking findings.
- QA passes or records an accepted non-blocking residual.
- product implementation package contains only approved TASK_343A files.
- parent TASK_343 source files are included only as Planner-owned prerequisite/source-consistency inputs, or a separate Planner waiver explicitly excludes them without leaving board references unresolved.
- no Close controls or TASK_343B close flow are mixed into the package.
- no backend/API/schema, future-scope, or unrelated governance residuals are included.

## 10. Stop Point

Current stop point: complete/accepted by Integrator.

Do not start TASK_343B, TASK_343C, backend changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, push, or unrelated cleanup from this lane.
