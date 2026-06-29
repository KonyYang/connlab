# TASK_345D Workbench Lifecycle Primary Action UI - Planner Evidence

Task ID: TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI
Lane: workbench-lifecycle-primary-action-ui
Role: Planner
Status: superseded for implementation authorization by reconciliation checkpoint; original Planner lane creation was planned - ready for Reviewer plan gate
Created: 2026-06-29

Implementation authorization source-of-truth after later Reviewer readiness and user approval:

- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_reconciliation_planner.md`

## Planner Checkpoint - 2026-06-29

### Current Phase / Task / Lane

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current task: `TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI`.
- Current lane: `workbench-lifecycle-primary-action-ui`.
- Why allowed now: `TASK_345C_PROJECT_LIFECYCLE_WRITE_GUARD_RULES` is complete/accepted by Integrator after backend write-guard implementation. The board states downstream frontend/UI/API-client-facing work must use its own formal lane, Reviewer/user gates, and scoped validation.

### Required Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `.agents/skills/impeccable/reference/product.md`
- `docs/frontend_architecture_rules.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- TASK_345A/B/C task, plan, and evidence context from board and lane files
- TASK_343A/B/C task, plan, developer evidence, and QA evidence excerpts
- TASK_344C task, plan, developer evidence, and QA evidence excerpts
- Current frontend API client snippets from `frontend/src/api/client.ts`
- Current Workbench lifecycle selectors/model snippets from `frontend/src/features/project-workbench/`

### Discovery Gate Result

Discovery Gate passed for creating a formal planning-first lane.

User-confirmed facts:

- Workbench lifecycle action should be one primary button.
- Active projects show `Close project`.
- Stopped and closed projects, including Completed-closed projects, support `Activate project`.
- Completed is one close reason, not a special close path.
- Close uses one unified close form with business close reason taxonomy.
- UI must not expose `administrative`.
- Temporary Apply/Register LTR is only a workflow entrypoint for the current batch; public-drive LTR workbook authority writing is downstream and locked.

Repository-proven facts:

- TASK_345A is accepted as the business lifecycle contract.
- TASK_345B is accepted as backend/API/audit activation model implementation.
- TASK_345C is accepted as backend lifecycle write-guard/read-only rule implementation.
- Current frontend API client still exposes old Stop/Resume and completed/admin split close helpers, with no confirmed activate helper or unified close helper.
- Current Workbench selectors still model primary lifecycle action as `stop`, `resume`, or `none`.
- Current Workbench close confirmation code still exposes old completed/admin split close language.
- TASK_344C preserved existing TASK_343A/B lifecycle behavior while aligning no-Matrix Workbench shell layout.

Planner inference:

- TASK_345D should be a frontend/UI/API-client-facing lane.
- `frontend/src/api/client.ts` should be May Touch for the future implementation because the accepted backend API now has activate/unified close semantics that the current frontend client does not fully expose.
- Backend/API/write-guard changes remain locked. If Developer discovers an API mismatch, the lane should stop and request a separate backend/API lane.

### Definition Of Ready

Satisfied for planning-first lane creation and Reviewer plan gate.

Not satisfied for Developer implementation. Developer implementation requires Reviewer plan gate pass and explicit user implementation approval.

## Files Created / Updated

- Created `tasks/TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI.md`.
- Created `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`.
- Created `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_planner.md`.
- Updated `docs/task_board.md`.

## May Touch

Planner activation may touch:

- `tasks/TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI.md`
- `docs/task_345d_workbench_lifecycle_primary_action_ui_plan.md`
- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_planner.md`
- `docs/task_board.md`

Future implementation may touch only after Reviewer plan gate and explicit user approval:

- `frontend/src/api/client.ts` for lifecycle client helper/type updates required by TASK_345B.
- Workbench lifecycle selector/model/component/test files listed in the task and plan.
- `frontend/src/workbench.css` only for Workbench lifecycle action/form layout.
- `tests/unit/test_frontend_shell_files.py` only for static frontend guard coverage if needed.
- TASK_345D Developer/QA evidence files.

## Must Not Touch

- Backend product code, backend API, schema, migrations, write guards, backend tests.
- Projects registry implementation or `ProjectListPage`.
- Public-drive LTR workbook authority writes or Office workbook mutation.
- Temporary Apply/Register LTR implementation.
- TASK_345E+ future lanes.
- StepInstance, Report, AI, permissions, LAN/server, multi-user.
- `AGENTS.md`, `.agents/`, `docs/project_management/`, or unrelated governance/orchestration residuals.

## Locked Paths

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

## Evidence / Validation / Merge Gates

Evidence file:

- `docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_planner.md`

Validation Gate:

- Reviewer plan gate next.
- Future implementation must run focused Workbench/frontend tests, frontend build, static no-`administrative` user-facing copy scans, no backend/Projects registry mutation checks, and browser/manual smoke.

Merge Gate:

- Blocked until Reviewer plan gate, explicit user implementation approval, Developer evidence, Reviewer implementation gate, QA gate, and Integrator packaging/readiness gate all pass.

## Next Role Recommendation

Recommended next role: Reviewer plan gate.

Do not route Developer implementation yet.

## Completion Callback Text

Source role: ConnLab Planner
Completion status: ready_for_review
TASK_ID: TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI
Lane: workbench-lifecycle-primary-action-ui
Evidence path: docs/lane_evidence/TASK_345D_workbench-lifecycle-primary-action-ui_planner.md
Recommended next role: Reviewer plan gate
Blocker summary: none for plan review. Developer implementation remains blocked until Reviewer plan gate passes and user explicitly approves implementation.
Request: Please immediately run one full auto-orchestration scan and execute only one legal routing action.
