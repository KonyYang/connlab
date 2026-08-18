# TASK_345D Workbench Lifecycle Primary Action UI

Status: complete (archived 2026-08-18; implementation evidence in docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md)
Lane: workbench-lifecycle-primary-action-ui
Owner Roles: Frontend Developer / Reviewer / QA / Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-29

## 1. Purpose

Create the formal planning-first lane for the frontend Workbench lifecycle primary action model after `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`, `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`, and `TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES` were accepted.

TASK_345D plans the Workbench UI/API-client-facing migration from the earlier TASK_343 Stop/Resume and completed/admin split close model to the accepted business model:

- The Workbench lifecycle area should expose one primary lifecycle action.
- Active formal/registered projects show `Close project`.
- Stopped projects and closed projects, including Completed-closed projects, show `Activate project` when backend lifecycle data allows activation.
- Close uses one unified business close form with business reasons: `Completed`, `Failed`, `Cancelled`, `Cannot test`, `Duplicate`, and `Other`.
- User-facing UI must not expose `administrative`.
- Frontend behavior relies on TASK_345B/TASK_345C backend/API/write-guard semantics.

This task has completed planning-first preparation. Per Planner reconciliation on 2026-06-29, implementation is authorized after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and updated only TASK_345D plan/evidence.
- Reviewer implementation-readiness content review passed.
- User explicitly approved the Developer implementation pass.

Developer implementation must stay inside the Workbench lifecycle UI/API-client-facing scope and the May Touch list below.

## 2. Inputs

- `TASK_345A_PROJECT_LIFECYCLE_BUSINESS_MODEL_CONTRACT`
- `TASK_345B_PROJECT_LIFECYCLE_ACTIVATION_MODEL_API`
- `TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES`
- TASK_343A/B/C Workbench and Projects list lifecycle UX evidence
- `TASK_344C_NO_MATRIX_WORKBENCH_EMPTY_STATE_ALIGNMENT`
- `$impeccable` product/UI guidance
- `docs/frontend_architecture_rules.md`
- `docs/02_ARCHITECTURE_RULES.md`

## 3. Scope

TASK_345D owns Workbench lifecycle primary action UI planning only.

Future implementation may include:

- Updating the Workbench lifecycle action selector/model so the primary lifecycle action is `Close project` for active formal/registered projects and `Activate project` for stopped/closed activatable projects.
- Replacing the older Close completed/admin split UI with one unified close form and business reason taxonomy.
- Updating Workbench state refresh and lifecycle error/recovery copy after close or activate.
- Updating frontend API client types/helpers only if existing client helpers are insufficient for the accepted TASK_345B API.
- Updating focused Workbench tests, API-client type coverage, static frontend guards, and browser smoke evidence.

## 4. Out Of Scope

TASK_345D must not implement:

- Backend model, API, schema, migration, or write-guard changes.
- Projects registry copy/routing changes. Those should be a later TASK_345E-style lane if needed.
- Temporary Apply/Register LTR workflow entrypoint beyond locked/downstream dependency notes.
- Public-drive LTR workbook authority writes or Office workbook mutation.
- StepInstance, Report generation, AI review, permissions, LAN/server, or multi-user scope.
- Matrix Editor business rules, execution persistence, fee/folder/package workflows, or unrelated governance cleanup.

## 5. May Touch

Planner/reconciliation may touch only:

- `tasks/TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI.md`
- `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_planner.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_reconciliation_planner.md`
- `docs/task_board.md`

Developer implementation may touch only:

- `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_developer.md`
- `frontend/src/api/client.ts` for activate/unified-close helpers and lifecycle response/error typing if the accepted backend API requires it.
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx` or a clearly named replacement component
- `frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` only if primary action placement requires it
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` only for static frontend guard coverage if needed
- TASK_345D Developer/QA evidence files under `docs/lane_evidence/`

## 6. Must Not Touch

- `backend/`
- Backend tests except no TASK_345D implementation should need them.
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- Public-drive LTR workbook authority paths and Office gateway write paths.
- TASK_345E or later task files unless a separate Planner lane is created.
- StepInstance, Report, AI, permissions, LAN/server, multi-user, and unrelated governance/orchestration files.

## 7. Locked Paths

- `backend/`
- `backend/api/`
- `backend/application/`
- `backend/domain/`
- `backend/infrastructure/`
- `backend/modules/`
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- Public-drive / Office workbook authority write paths
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`

## 8. Validation Gate

Reviewer plan gate must confirm:

- TASK_345D is frontend/UI/API-client-facing only.
- `frontend/src/api/client.ts` is May Touch only for typed client helpers/DTOs required by TASK_345B.
- No backend/API/write-guard work is hidden in this lane.
- User-facing copy uses `Close project`, `Activate project`, and business close reasons; it does not expose `administrative`.
- Active, stopped, closed Completed, closed non-Completed, registered no-Matrix, temporary/no-LTR, and write-guard conflict cases have test and smoke expectations.
- Existing TASK_343A/B tests are preserved or intentionally migrated to the TASK_345A business model rather than silently deleted.

Future implementation validation should include:

- Focused Vitest coverage for lifecycle selectors/model and Workbench UI.
- Frontend build.
- Static source scans for raw `administrative` user-facing copy, old split close labels, forbidden future scope, and Projects registry mutation controls.
- Browser/manual smoke for active Matrix Workbench, registered no-Matrix Workbench, stopped Workbench, closed Completed Workbench, and closed non-Completed Workbench.

## 9. Merge Gate

Merge remains blocked until:

- Developer planning-first and implementation evidence are complete.
- Reviewer implementation gate passes.
- QA/browser smoke gate passes or records an accepted residual.
- Integrator packaging/readiness confirms package scope, validation, and forbidden-path checks.

Current stop point: implementation authorized, pending Developer implementation. Do not mark complete until Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness all pass.
