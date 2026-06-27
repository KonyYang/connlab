# TASK_343C Planner Evidence

Status: ready_for_review
Task: TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT
Lane: projects-list-action-copy-routing-alignment
Role: Planner/Designer
Date: 2026-06-27

## Summary

This Planner pass creates and activates the formal planning-first lane for Projects list action copy/routing alignment. It does not modify frontend product code, backend code, tests, database schema, API client code, Workbench behavior, TASK_343A/TASK_343B implementation, runtime routing, or lifecycle writes.

Planner gate: ready.

Recommended next role: Reviewer plan gate.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context from `PRODUCT.md` and `DESIGN.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- parent TASK_343 task, plan, and Planner evidence
- TASK_343A task, plan, Developer evidence, and QA evidence
- TASK_343B task, plan, Planner evidence, Developer evidence, and QA evidence
- TASK_339B task, plan, and Developer evidence
- read-only source inspection of current Projects registry helper, `ProjectListPage`, and API client lifecycle helper names

## Discovery Gate Result

Confirmed by user:

- TASK_343B is complete/accepted by Integrator.
- TASK_343C should align Projects list action copy/routing with completed Workbench lifecycle actions.
- Projects list should route to the right Workbench context instead of exposing duplicate mutation flows.
- Existing TASK_339B filtering/categories must be preserved.
- Planner must not modify product code, TASK_343A/TASK_343B implementation, commit, push, reset, delete, or clean unrelated residuals.

Confirmed by repository evidence:

- `docs/task_board.md` shows no active implementation lane and names TASK_343C as next formal lane candidate.
- Parent TASK_343 names TASK_343C as the third child implementation lane.
- TASK_339B implemented lifecycle registry views and kept row actions read/navigation-oriented with `Open` only.
- TASK_343A and TASK_343B accepted packages did not modify Projects registry or `ProjectListPage`.
- Current Projects registry helper already centralizes status/next-step labels.
- Current `ProjectListPage` row action routes through `onOpenProject(projectId)`.

Inferred by Planner:

- TASK_343C can remain frontend-only because the needed registry and lifecycle overlay data already exist.
- The likely future implementation files are the Projects registry helper, ProjectListPage, their tests, and possibly small registry CSS.
- API client and Workbench lifecycle implementation files should stay locked.

Not yet confirmed:

- Exact final row action wording should be checked by Reviewer and Developer planning.
- Browser control availability for future QA is unknown.

Decision: Definition of Ready is satisfied. Unconfirmed wording/browser details do not change file ownership, API ownership, or serial ordering.

## Files Created Or Updated

- `tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md`
- `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`
- `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- `docs/task_board.md`

## Lane Boundaries

May Touch:

- Planner activation docs and board row.
- Future Developer planning evidence after Reviewer plan gate.
- Future implementation, only after explicit approval, limited to Projects registry helper, ProjectListPage, focused tests, and small registry CSS if needed.

Must Not Touch:

- backend, root tests, frontend API client, Workbench lifecycle implementation, TASK_343A/TASK_343B implementation, TASK_336 through TASK_342 source files except read-only reference, governance/orchestration residuals, database/API/write guards, Office/public-drive workflows, future scope.

Locked Paths:

- TASK_343C task/plan/evidence files.
- Future Projects registry implementation/test paths declared in the task and plan.

Evidence:

- Planner evidence: `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md`
- Future Developer evidence: `docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_developer.md`

Validation Gate:

- plan and board row exist.
- no product code changed.
- registry remains routing-only.
- future implementation must prove no lifecycle mutation helper calls from Projects registry code.

Merge Gate:

- Reviewer implementation gate pass.
- QA pass or accepted residual if required.
- Integrator accepts only approved TASK_343C package files.
- no backend/API/schema/frontend API client, Workbench lifecycle behavior, TASK_343A/TASK_343B implementation, future scope, or unrelated governance residuals included.

## Validation

Commands run from `D:\PythonProject\connlab` after Planner edits:

```powershell
Test-Path tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md
Test-Path docs/task_343c_projects_list_action_copy_routing_alignment_plan.md
Test-Path docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md
Select-String -Path docs/task_board.md,tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md,docs/task_343c_projects_list_action_copy_routing_alignment_plan.md,docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md -Pattern 'TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT|projects-list-action-copy-routing-alignment|Planner gate: ready|Reviewer plan gate|Must Not Touch|Merge Gate' -Encoding UTF8
git diff --check -- tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md docs/task_343c_projects_list_action_copy_routing_alignment_plan.md docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md docs/task_board.md
git status --short -- backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/project-dashboard.css tasks/TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX.md tasks/TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW.md docs/task_board.md tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md docs/task_343c_projects_list_action_copy_routing_alignment_plan.md docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md AGENTS.md .agents docs/project_management
rg -n "stopProjectLifecycle|resumeProjectLifecycle|closeProjectCompletedLifecycle|closeProjectAdministrativeLifecycle" tasks/TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT.md docs/task_343c_projects_list_action_copy_routing_alignment_plan.md docs/lane_evidence/TASK_343C_projects-list-action-copy-routing-alignment_planner.md
```

Observed results:

- TASK_343C task, plan, and Planner evidence files exist.
- Keyword checks found the new task ID, lane ID, Planner gate readiness, Reviewer plan gate, Must Not Touch, and Merge Gate coverage across board/task/plan/evidence.
- `git diff --check` passed for TASK_343C planning files and board, with only the existing `docs/task_board.md` LF/CRLF working-copy warning.
- Product-code scope status showed no modified `frontend/`, `backend/`, or root `tests/` paths. The only relevant changes are `docs/task_board.md` plus the three new TASK_343C planning/evidence files. Existing unrelated governance/orchestration residuals remain visible under `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*` and are excluded from TASK_343C.
- Lifecycle mutation helper names appear only inside the future validation command in `docs/task_343c_projects_list_action_copy_routing_alignment_plan.md`; no product code was edited or scanned as changed in this Planner pass.

## Stop Point

Stop after validation and completion callback.

Do not start Developer implementation. Do not modify product code. Do not start TASK_344 or later tasks. Do not commit, push, reset, delete, or clean unrelated residuals.
