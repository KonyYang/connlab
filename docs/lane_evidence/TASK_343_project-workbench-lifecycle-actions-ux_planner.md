# Planner Evidence - TASK_343 Project Workbench Lifecycle Actions UX

Status: accepted
Task: TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX
Lane: project-workbench-lifecycle-actions-ux
Role: Planner/Designer
Updated: 2026-06-27

## Scope Boundary

This Planner pass creates the formal planning-first lane for the remaining Workbench lifecycle action UX loop. It does not modify frontend code, backend code, tests, database schema, API implementation, runtime routing, or product behavior.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- TASK_336 task and plan
- TASK_337A task, plan, and developer evidence
- TASK_337B task, plan, and developer evidence
- TASK_338 task, plan, and developer evidence
- TASK_339A task, plan, and developer evidence
- TASK_339B task, plan, and developer evidence
- TASK_340 task, plan, and planner evidence
- TASK_341 task, plan, developer evidence, and QA evidence
- TASK_342 task, plan, developer evidence, and QA evidence
- `$impeccable` product context for Workbench UX planning

## Confirmed Facts

- `docs/task_board.md` marks TASK_342 complete and accepted.
- TASK_337A provides backend lifecycle endpoints for get lifecycle, stop, resume, close completed, and close administrative.
- TASK_337A evidence records completed close summary signals and output status summary.
- TASK_338 implemented first lifecycle write guards and preserves classified readonly previews.
- TASK_339A implemented frontend readonly behavior and lifecycle error copy.
- TASK_339B implemented registry lifecycle views and deliberately kept registry actions read/navigation oriented.
- TASK_340 defined the accepted Unified Workbench Shell IA and lifecycle action model.
- TASK_341 implemented the first shell slice and explicitly did not invent Resume/Close controls.
- TASK_342 closed the prior series with no product source/test changes and recorded remaining browser narrow-viewport/tab-order risk as non-blocking.
- Manual smoke found the remaining Workbench Stop/Resume/Close action loop, close confirmation flow, Active Matrix lifecycle action area, and Projects list action copy/routing alignment gaps.

## Files Created Or Updated

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- `docs/task_board.md`

## Split Decision

TASK_343 remains the Planner/UX contract lane.

Recommended follow-up implementation lanes:

- `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`, first implementation lane, frontend-only by default.
- `TASK_343B_CLOSE_COMPLETED_ADMIN_CONFIRMATION_FLOW`, close completed/admin confirmation flow lane.
- `TASK_343C_PROJECTS_LIST_ACTION_COPY_ROUTING_ALIGNMENT`, Projects list copy/routing alignment lane.

## First Implementation Lane Gates

Recommended first implementation lane:

- Task: `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX`
- Lane: `workbench-lifecycle-actions-ux`
- Next role after TASK_343 Reviewer plan pass and user approval: Frontend Developer planning-first
- Backend touch: not approved by default
- QA: required after Reviewer pass because the lane alters the main Workbench operator flow

May Touch, Must Not Touch, Locked Paths, Evidence, Validation Gate, Reviewer Gate, QA Gate, and Merge Gate are defined in `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`.

## Unrelated Residuals

`git status --short` shows existing governance/orchestration residuals under:

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/`
- `.agents/skills/connlab-planner/`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

These residuals are explicitly excluded from TASK_343 and from recommended TASK_343A/B/C product packages unless a separate governance lane owns them.

## Validation

Planned validation after file updates:

```powershell
Test-Path tasks\TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md
Test-Path docs\task_343_project_workbench_lifecycle_actions_ux_plan.md
Test-Path docs\lane_evidence\TASK_343_project-workbench-lifecycle-actions-ux_planner.md
Select-String -Path docs\task_board.md -Pattern 'project-workbench-lifecycle-actions-ux' -Encoding UTF8
Select-String -Path docs\task_343_project_workbench_lifecycle_actions_ux_plan.md -Pattern 'Gap Review' -Encoding UTF8
Select-String -Path docs\task_343_project_workbench_lifecycle_actions_ux_plan.md -Pattern 'Planner gate: ready' -Encoding UTF8
git diff --check -- tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md docs/task_343_project_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md docs/task_board.md
```

## Stop Point

Stop after validation and completion callback. Do not start Developer implementation, do not create TASK_343A/B/C formal implementation files without separate user approval, do not modify product code, do not merge, commit, push, or clean unrelated residuals.

## Planner Fix Pass - Reviewer Blocking Finding B1

Reviewer result:

- `Reviewer plan gate: blocked`
- Blocking finding B1: TASK_343A previously allowed a non-functional or placeholder `Close project` affordance while close completed/admin confirmation was assigned to TASK_343B.

Fix applied:

- Updated `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md` so TASK_343A must withhold all Close controls entirely.
- Clarified that Close as completed / Close administratively UI, confirmation dialog, output summary, close note, administrative reason, acknowledgement checkbox, post-close archive transition, and close API calls remain TASK_343B only.
- Stated that TASK_343A may reference Close only as future locked/excluded scope, not as a visible disabled placeholder, routing target, reserved button, menu item, or non-functional affordance.
- Updated TASK_343A May Touch / Must Not Touch / Validation Gate / Reviewer Gate / QA Gate / Merge Gate language to enforce the boundary.
- Updated `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md` to record the same first-lane boundary.

Files updated in fix pass:

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`

No product code, frontend, backend, tests, or unrelated governance residuals were modified.

Fix-pass validation:

- `Select-String` check for removed permissive wording found no TASK_343 occurrences of `Close entry may be visible`, `Close project secondary`, `may reserve or route`, `non-functional until TASK_343B`, or `controlled placeholder`.
- TASK_343 plan/task/board now contain explicit TASK_343A Close-withholding language.
- `git diff --check -- tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md docs/task_343_project_workbench_lifecycle_actions_ux_plan.md docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md docs/task_board.md` passed with only the existing `docs/task_board.md` CRLF working-copy warning.
- `git status --short -- frontend backend tests ...` showed no `frontend/`, `backend/`, or root `tests/` changes. Existing unrelated governance/orchestration residuals remain visible and excluded.

Fix-pass stop point:

Ready for Reviewer plan gate re-review. Do not route to Developer.

## Reviewer Acceptance And Planner Packaging Ownership Checkpoint

Date: 2026-06-27

Reviewer plan gate result after B1 fix: pass, per current board state and delegated Planner cleanup input.

Planner ownership decision:

- The parent `TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX` files are legitimate Planner-owned planning source-of-truth files.
- They are prerequisite/package inputs for child `TASK_343A_WORKBENCH_LIFECYCLE_ACTIONS_UX` because `docs/task_board.md` records TASK_343 as the accepted parent contract and TASK_343A as its first approved implementation lane.
- Excluding these parent source files while packaging `docs/task_board.md` would leave the board pointing at missing source files.
- Including them does not make them TASK_343A product implementation files and does not retroactively expand Developer May Touch.

Integrator packaging allowance:

- `tasks/TASK_343_PROJECT_WORKBENCH_LIFECYCLE_ACTIONS_UX.md`
- `docs/task_343_project_workbench_lifecycle_actions_ux_plan.md`
- `docs/lane_evidence/TASK_343_project-workbench-lifecycle-actions-ux_planner.md`
- `docs/task_board.md`

These files may be included by Integrator as Planner-owned prerequisite/source-consistency inputs for TASK_343A packaging. They must remain separate from the TASK_343A frontend implementation package and must not authorize TASK_343B, TASK_343C, Close UI, backend/API/schema changes, or unrelated governance/orchestration residuals.
