# TASK_343 Project Workbench Lifecycle Actions UX

Status: complete/accepted
Lane: project-workbench-lifecycle-actions-ux
Owner Role: Planner/Designer
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Create the planning-first UX contract for the remaining Project Workbench lifecycle action loop after TASK_342 closeout.

TASK_337A through TASK_342 established backend lifecycle/API shape, first write guards, frontend readonly behavior, registry lifecycle views, the Unified Project Workbench Shell, and final closeout validation. Manual smoke after closeout found that the Workbench still needs a controlled follow-up for Stop, Resume, Close action UX, close confirmation flows, Active Matrix lifecycle action placement, and Projects registry action copy/routing alignment.

This task is planning and lane definition only. It does not implement frontend or backend runtime behavior.

## 2. Required Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `tasks/TASK_337A_PROJECT_LIFECYCLE_BACKEND_API_SHAPE.md`
- `docs/task_337a_project_lifecycle_backend_api_shape_plan.md`
- `docs/lane_evidence/TASK_337A_lifecycle-backend-api_developer.md`
- `tasks/TASK_337B_PROJECT_LIFECYCLE_GUARD_INVENTORY_AND_TEST_MATRIX.md`
- `docs/task_337b_project_lifecycle_guard_inventory_and_test_matrix.md`
- `docs/lane_evidence/TASK_337B_guard-inventory_developer.md`
- `tasks/TASK_338_PROJECT_LIFECYCLE_WRITE_GUARD_INTEGRATION.md`
- `docs/task_338_project_lifecycle_write_guard_integration_plan.md`
- `docs/lane_evidence/TASK_338_write-guard-integration_developer.md`
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
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_developer.md`
- `docs/lane_evidence/TASK_341_unified-workbench-shell-implementation_qa.md`
- `tasks/TASK_342_LIFECYCLE_INTEGRATION_QA_AND_BOARD_CLOSEOUT.md`
- `docs/task_342_lifecycle_integration_qa_and_board_closeout_plan.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_developer.md`
- `docs/lane_evidence/TASK_342_lifecycle-integration-qa-and-board-closeout_qa.md`

## 3. Scope

TASK_343 must produce:

- a gap review comparing the original lifecycle product rules with delivered TASK_337A through TASK_342 capability
- a split decision for TASK_343A, TASK_343B, and TASK_343C
- state-specific Workbench lifecycle action UX rules
- close completed and close administrative confirmation flow contracts
- Projects registry copy/routing alignment rules
- May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, Merge Gate, Reviewer/QA/Integrator gates for the first implementation lane

## 4. Split Decision

TASK_343 should remain the Planner/UX contract lane.

Recommended implementation lanes:

1. `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`
   - first implementation lane
   - frontend-only by default
   - adds Workbench lifecycle action placement and Stop/Resume action UX using existing TASK_337A/TASK_339A data and APIs
   - withholds all Close controls until a separate approved functional close lane exists
2. `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW`
   - second implementation lane
   - implements completed close and administrative close confirmation dialogs and refresh behavior
   - backend remains out of scope unless Developer planning proves existing close summary data is insufficient
3. `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`
   - third implementation lane
   - aligns Projects list status copy, Next Step copy, and Open routing language with the accepted Workbench states

Do not implement all three as one broad lane.

## 5. First Implementation Lane Recommendation

First lane: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`.

Reason: Workbench is the state authority surface for lifecycle actions. It should expose a consistent action area before close-specific dialog details and registry copy refinements are implemented.

Boundary: TASK_343A must not expose Close as completed or Close administratively as a visible button, disabled placeholder, menu item, routing target, reserved control, or non-functional affordance. Close UI, confirmation dialogs, output summary acknowledgement, close note/reason fields, and close API calls remain TASK_343B only.

## 6. May Touch For TASK_343 Planner Lane

Planner may touch only:

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- `docs/task_board.md`

## 7. Must Not Touch For TASK_343 Planner Lane

Planner must not touch:

- `frontend/`
- `backend/`
- root `tests/`
- `tasks/TASK_343A_*`, `tasks/TASK_343B_*`, or `tasks/TASK_343C_*` unless the user separately approves formal lane creation
- product runtime behavior
- database schema
- API implementations
- public-drive, Office, Matrix, Fee, LTR, folder, Basic Information, Required Forms, or output generation behavior
- unrelated governance/orchestration residuals under `AGENTS.md`, `.agents/skills/*`, or `docs/project_management/*`

## 8. Locked Paths

- `frontend/`
- `backend/`
- `tests/`
- `AGENTS.md`
- `.agents/skills/`
- `docs/project_management/`
- all TASK_337A through TASK_342 source/evidence files, except read-only reference

## 9. Validation Gate

TASK_343 Planner validation is satisfied when:

- task, plan, evidence, and board row exist
- plan includes gap review table
- plan includes split decision and recommended first implementation lane
- plan defines state behavior for Active Matrix workspace, Registered setup, Temporary planning, Stopped, Closed completed, and Closed administrative
- plan defines completed close and administrative close flows
- plan states that TASK_343A withholds all Close controls until TASK_343B or another approved functional close lane exists
- plan defines Projects list copy/routing alignment
- first implementation lane gates are explicit
- no product code is changed

## 10. Merge Gate

TASK_343 has no product merge gate. It may proceed only through Reviewer plan gate.

Future TASK_343A, TASK_343B, and TASK_343C implementation lanes must each require Developer, Reviewer, QA where workflow behavior or browser/manual smoke is needed, and Integrator packaging/readiness gates before acceptance.

## 11. Stop Point

Stop after Planner evidence is updated and the Orchestrator callback is sent or printed.

Do not start Developer implementation, TASK_343A, TASK_343B, TASK_343C, backend guard changes, Report generation, StepInstance, execution persistence, AI, permissions, LAN/server, multi-user scope, or unrelated governance cleanup from this task.
