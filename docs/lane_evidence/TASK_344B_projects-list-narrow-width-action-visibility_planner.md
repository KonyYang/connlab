# TASK_344B Planner Evidence

Status: ready_for_review
Task: TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY
Lane: projects-list-narrow-width-action-visibility
Role: Planner/Designer
Date: 2026-06-28

## Summary

Planner created a formal planning-first frontend UX fix lane for the post-acceptance smoke finding that `/projects` hides Status, Next Step, and Action behind horizontal overflow around 514px browser width.

Planner decision: split this frontend UX fix from the closed smoke-data fixture lane. TASK_344B may later touch only narrow `/projects` registry UI files after Reviewer plan gate and Developer planning approval.

Planner gate: ready.

Recommended next role: Reviewer plan gate.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` product context
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- parent TASK_343 task/plan/evidence
- TASK_343A/B/C task/plan/evidence/QA evidence
- current read-only source inspection of `ProjectListPage`, Projects registry helper, and `project-dashboard.css`
- Developer triage callback supplied by user

## Discovery Result

Confirmed:

- TASK_343C is complete/accepted and should not be reopened directly.
- Browser smoke around 514px shows `/projects` table overflow hides Status, Next Step, and Action.
- The core `Open Workbench` / `Open archive` copy is not discoverable without horizontal scrolling.
- This Planner pass must not modify product code.

Repository evidence:

- `.project-table` currently has `min-width: 1060px`.
- `.project-table-wrap` uses horizontal overflow.
- Status, Next Step, and Action are right-side columns.
- TASK_343C QA accepted browser `/projects` smoke as a residual before this real smoke finding existed.

Planner inference:

- The fix should be frontend-only and limited to `/projects` responsive layout/action visibility.
- QA/browser smoke should be required after implementation.

Not yet confirmed:

- Exact responsive pattern.
- Browser tooling availability for future QA.

## Files Created Or Updated

- `tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md`
- `docs/task_344b_projects_list_narrow_width_action_visibility_plan.md`
- `docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md`
- `docs/task_board.md`

## Scope Boundary

May Touch:

- Planner docs and board row.
- Future Developer planning evidence.
- Future implementation, after approval, limited to `ProjectListPage`, Projects registry helper/tests if needed, and `project-dashboard.css`.

Must Not Touch:

- backend, root tests, frontend API client, Workbench lifecycle implementation, TASK_343A/B/C accepted implementation outside approved read-only reference, TASK_344A smoke-data files except read-only reference, future scope, governance residuals.

Validation Gate:

- Reviewer plan gate before Developer planning.
- Future implementation tests, build, mutation-helper scans, forbidden-scope checks, and 514px browser/manual smoke.

Merge Gate:

- Reviewer pass, QA pass, and Integrator packaging/readiness. No backend/API/client/Workbench/future-scope/unrelated residuals.

## Validation

Commands run from `D:\PythonProject\connlab` after Planner edits:

```powershell
Test-Path tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md
Test-Path docs/task_344b_projects_list_narrow_width_action_visibility_plan.md
Test-Path docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md
Select-String -Path docs/task_board.md,tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md,docs/task_344b_projects_list_narrow_width_action_visibility_plan.md,docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md -Pattern 'TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY|projects-list-narrow-width-action-visibility|Planner gate: ready|Reviewer plan gate|Must Not Touch|Merge Gate' -Encoding UTF8
git diff --check -- tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md docs/task_344b_projects_list_narrow_width_action_visibility_plan.md docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md docs/task_board.md
git status --short -- docs/task_board.md tasks/TASK_344B_PROJECTS_LIST_NARROW_WIDTH_ACTION_VISIBILITY.md docs/task_344b_projects_list_narrow_width_action_visibility_plan.md docs/lane_evidence/TASK_344B_projects-list-narrow-width-action-visibility_planner.md backend tests frontend/src/api/client.ts frontend/src/features/project-workbench frontend/src/features/project-lifecycle frontend/src/workbench.css frontend/src/features/projects-registry frontend/src/pages/ProjectListPage.tsx frontend/src/project-dashboard.css AGENTS.md .agents docs/project_management
```

Observed results:

- TASK_344B task, plan, and Planner evidence files exist.
- Keyword checks found the task ID, lane ID, Planner gate readiness, Reviewer plan gate, Must Not Touch, and Merge Gate coverage.
- `git diff --check` passed for TASK_344B planning files and board, with only the existing `docs/task_board.md` LF/CRLF working-copy warning.
- Product-code scope status showed no modified `frontend/`, `backend/`, root `tests/`, API client, Workbench, project-lifecycle, or registry product paths from this Planner pass.
- Existing unrelated governance/orchestration residuals remain visible under `AGENTS.md`, `.agents/skills/*`, and `docs/project_management/*`; they are excluded from TASK_344B.

## Stop Point

Stop after validation and callback. Do not start Developer implementation from this Planner pass.
