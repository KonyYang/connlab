# TASK_343B Close Completed/Admin Confirmation Flow

Status: complete/accepted by Integrator
Lane: workbench-close-completed-admin-ux
Owner Role: Planner/Designer
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Create the formal planning-first lane for Project Workbench close UX after `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` was accepted.

TASK_343B covers functional Workbench close controls and confirmation flows only:

- Close as completed.
- Close administratively.
- Completed close output status summary review.
- Required completed close note.
- Required administrative close reason.
- Post-close refresh into readonly archive state.

This lane completed the approved planning, Workbench frontend implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness flow.

## 2. Allowed Reason

- `TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX` is complete/accepted and split the remaining work into TASK_343A, TASK_343B, and TASK_343C.
- `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` is complete/accepted by Integrator in local commit `27de54907f9f46f8c15669822328b49f07059969`.
- TASK_343A intentionally withheld all Close controls.
- The user explicitly requested formal planning-first lane creation/activation for TASK_343B.
- `docs/task_board.md` currently shows no active implementation lane and recommends Planner Discovery Gate for TASK_343B.

## 3. Required Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `PRODUCT.md` / `DESIGN.md` via `$impeccable`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`
- `docs/task_338_project_lifecycle_write_guard_integration_plan.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`
- `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`
- `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`
- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `tasks/TASK_341_UNIFIED_PROJECT_WORKBENCH_SHELL_IMPLEMENTATION.md`
- `docs/task_341_unified_project_workbench_shell_implementation_plan.md`
- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- TASK_343A task, plan, developer evidence, and QA evidence

## 4. Scope

TASK_343B may plan:

- Workbench functional Close project affordance for allowed active/stopped states.
- Close as completed confirmation flow for formal/registered projects.
- Close administratively confirmation flow for active or stopped projects.
- Current output status summary display using existing lifecycle response data where available.
- Manual completion acknowledgement copy that does not imply StepInstance-backed verification.
- Required `close_note` for completed close.
- Required `reason` for administrative close.
- Use of existing frontend API helpers:
  - `closeProjectCompletedLifecycle(...)`
  - `closeProjectAdministrativeLifecycle(...)`
- Workbench state refresh after successful close.
- Closed completed/admin archive banner and no Resume/Stop/Close-again controls.
- Focused frontend tests, build, no-future-scope source scans, and QA smoke expectations.

## 5. Hard Boundaries

TASK_343B must not:

- modify backend/API/schema/write guards by default.
- change `frontend/src/api/client.ts` unless Reviewer accepts a plan blocker proving the existing client contract is insufficient.
- rework TASK_343A Stop/Resume behavior except for necessary integration with Close placement in the same Workbench lifecycle action area.
- implement TASK_343C Projects list copy/routing alignment.
- implement StepInstance, execution persistence, Report generation, AI, permissions, LAN/server, multi-user scope, or future feature controls.
- change Matrix, Fee, Folder, Basic Information, LTR, Required Forms, Public Drive, Office, or output authority behavior.
- claim automatic testing completion.
- allow completed close for temporary/no-LTR planning projects unless a separate approved exception lane exists.
- expose Close controls in closed completed/admin archive states.
- package unrelated governance/orchestration residuals.

## 6. May Touch

Planner activation may touch:

- `tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md`
- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_planner.md`
- `docs/task_board.md`

Reviewer plan gate may touch only its review evidence/checkpoint if the role creates one, or may report findings in thread if no reviewer evidence file is yet created.

Future Developer planning-first may touch only after Reviewer plan gate pass and routing:

- `docs/task_343b_close_completed_admin_confirmation_flow_plan.md`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md`

Future implementation may touch only after explicit approval of the Developer planning pass. Likely candidates are limited to Workbench lifecycle/action files and focused frontend tests under:

- `frontend/src/features/project-workbench/`
- `frontend/src/features/project-lifecycle/` only if shared lifecycle display/readonly helpers need a frontend-only close model
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_343B_workbench-close-completed-admin-ux_developer.md`

## 7. Must Not Touch

- `backend/`
- root `tests/`
- `frontend/src/api/client.ts` by default
- `frontend/src/features/projects-registry/`
- `frontend/src/pages/ProjectListPage.tsx`
- TASK_343A implementation files except read-only reference and any future approved minimal integration point
- TASK_343C task/plan/evidence files
- TASK_336 through TASK_342 files except read-only reference
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- unrelated governance/orchestration residuals

## 8. Locked Paths

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

## 9. Validation Gate

TASK_343B planning validation is satisfied when:

- task, plan, Planner evidence, and board row exist.
- Discovery Gate separates user facts, repository evidence, Planner assumptions, and open questions.
- plan confirms existing close backend endpoints and frontend client helpers.
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, Reviewer Gate, QA Gate, and Merge Gate are explicit.
- plan states completed close is formal/registered by default.
- plan states temporary/no-LTR projects default to administrative close.
- plan states completed close uses manual confirmation plus output status summary because StepInstance does not exist.
- plan states administrative close requires a reason.
- plan states closed projects are readonly archives and cannot Resume.
- no product code is changed.

## 10. Reviewer / QA / Merge Gates

Reviewer plan gate is required before Developer planning-first or implementation routing.

Future implementation must require:

- Developer evidence.
- Reviewer implementation gate.
- QA gate because close actions are lifecycle-changing, destructive in the sense of archiving, and affect main Workbench operator flow.
- Integrator packaging/readiness gate.

Merge remains blocked until:

- Reviewer plan gate passes.
- user/orchestrator explicitly routes the next role.
- Developer evidence records exact implemented file list and validation.
- Reviewer has no blocking findings.
- QA passes or records an accepted non-blocking residual.
- package contains only approved TASK_343B files plus board/evidence updates.
- backend/API/schema/frontend API client changes are absent unless a separate approved scope change exists.
- TASK_343C, Report, StepInstance, AI, permissions, LAN/server, multi-user, and unrelated governance residuals are not mixed in.

## 11. Stop Point

Stop after Integrator packaging/readiness acceptance and completion callback.

Do not start TASK_343C, backend changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, push, reset, delete, or unrelated cleanup from this lane.
