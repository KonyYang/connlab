# Developer Evidence - TASK_339B Projects Registry Lifecycle Views

Status: implementation complete - pending review
Task: TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS
Lane: projects-registry-lifecycle-views
Role: Frontend Developer
Last Updated: 2026-06-27

## Approval

Planner created this formal planned lane after the user requested TASK_339B lane preparation.

Planner activated this lane as approved for Frontend Developer planning first after closing the TASK_340 source mismatch.

## Current Phase

Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## Why This Lane Is Allowed

TASK_339A is complete and accepted.

The user-required TASK_340 background files were missing from the current worktree, but Planner restored them from `stash@{0}^3` on 2026-06-27:

- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`

TASK_340 remains background for later TASK_341 Workbench shell implementation and does not authorize Workbench shell implementation in TASK_339B.

TASK_339B is approved for planning first only. Frontend product code remains blocked until the TASK_339B plan is reviewed and explicitly approved.

Reviewer plan gate passed after the planning-first pass. The user then explicitly requested the TASK_339B Developer implementation pass.

## Goal

After activation, plan and implement Projects registry lifecycle views for active, stopped, closed completed, and closed administrative projects.

## May Touch

Planner/Integrator planning may touch:

- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/task_board.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`

Frontend Developer planning may touch:

- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`

Frontend Developer implementation may touch only files explicitly listed in the user-approved TASK_339B implementation plan.

## Must Not Touch

- frontend product code before lane activation and plan approval
- backend implementation
- TASK_338 backend write guards
- Unified Workbench Shell implementation
- Project Workbench shell layout or navigation IA
- Office gateway internals
- Matrix/Fee business rules
- Project Folder backend behavior
- StepInstance, Report generation, AI, permissions, LAN/server, or multi-user scope
- public-drive authority replacement
- unrelated governance/orchestration residual files

## Locked Paths

- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`
- frontend registry files explicitly listed in the approved TASK_339B implementation plan

## Validation Gate

- Plan approved by user before frontend product code changes.
- Active/stopped/closed completed/closed administrative registry views are covered.
- Registry copy uses business labels and does not expose raw enum names.
- Default registry view remains operational for active work.
- Archived closed projects remain findable without crowding the active work queue.
- Focused frontend tests pass.
- Frontend build passes.

## Merge Gate

Reviewer and Integrator gates are required. QA is required if the approved plan calls for browser/manual smoke or if registry filtering cannot be covered by component tests alone.

Merge remains blocked if backend code is changed, Workbench shell implementation is mixed in, lifecycle write actions are added from the registry without explicit approval, or future scope appears under this task.

## Commands Or Checks Run

Planner Discovery:

- Read `AGENTS.md`.
- Read `docs/task_board.md`.
- Read `.agents/skills/connlab-lane-orchestrator/SKILL.md`.
- Read `.agents/skills/connlab-planner/SKILL.md`.
- Read `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`.
- Read `docs/project_management/PARALLEL_EXECUTION_MODEL.md`.
- Read `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`.
- Read `docs/project_management/ROLE_THREAD_REGISTRY.md`.
- Read `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`.
- Read `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`.
- Read `tasks/TASK_339A_PROJECT_LIFECYCLE_FRONTEND_READONLY_MODEL.md`.
- Read `docs/task_339a_project_lifecycle_frontend_readonly_model_plan.md`.
- Read `docs/lane_evidence/TASK_339A_frontend-readonly-model_developer.md`.
- Loaded `$impeccable` product-register context from `PRODUCT.md` and `DESIGN.md`.
- Attempted to read required TASK_340 task, plan, and evidence files; all three are missing.
- Confirmed latest local commit: `74dd366 feat(frontend): complete TASK_339A readonly model`.
- Confirmed TASK_339B/TASK_341/TASK_342 formal task files did not exist before this Planner turn.
- Inspected existing Projects registry entry point: `frontend/src/pages/ProjectListPage.tsx`.

Planner activation blocker closure:

- Checked current tracked files with `git ls-files`; TASK_340 files were not tracked in current `master`.
- Checked current worktree paths with `rg --files`; TASK_340 files were absent.
- Checked git history for the three expected TASK_340 paths; no tracked history was found.
- Checked `git stash list`; found `stash@{0}: On codex/task-337a-lifecycle-backend-api: wip governance planning residuals before TASK_337 merge`.
- Checked `git stash show --name-status --include-untracked 'stash@{0}'`; the untracked stash parent included all three TASK_340 files.
- Restored only the three TASK_340 files from `stash@{0}^3`.
- Did not apply the full stash and did not restore unrelated governance residuals.
- Updated TASK_339B task/plan/evidence and `docs/task_board.md` from `planned_blocked` to `approved` planning first.

Frontend Developer planning-first pass:

- Read `AGENTS.md`.
- Read latest `docs/task_board.md`.
- Read `.agents/skills/connlab-lane-orchestrator/SKILL.md`.
- Read `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`.
- Read `docs/project_management/ROLE_THREAD_REGISTRY.md`.
- Read `docs/project_management/PARALLEL_EXECUTION_MODEL.md`.
- Read `docs/project_management/TASK_EXECUTION_SKILL.md`.
- Read `docs/02_ARCHITECTURE_RULES.md`.
- Read `docs/frontend_architecture_rules.md`.
- Loaded `$impeccable` product-register context from `PRODUCT.md` and `DESIGN.md`.
- Read `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`.
- Read relevant registry/lifecycle sections of `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`.
- Read `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`.
- Read `docs/task_339b_projects_registry_lifecycle_views_plan.md`.
- Read this evidence file.
- Read restored TASK_340 facts:
  - `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
  - `docs/task_340_unified_project_workbench_shell_plan.md`
  - `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- Inspected current registry/frontend structure without modifying product code:
  - `frontend/src/pages/ProjectListPage.tsx`
  - `frontend/src/api/client.ts`
  - `frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts`
  - `frontend/src/project-dashboard.css`
- Confirmed current `ProjectRegistryRow` does not expose `lifecycle_state` or `closure_type`.
- Confirmed TASK_339A already provides `ProjectLifecycleResponse`, `getProjectLifecycle(projectId)`, and lifecycle readonly display helpers.
- Confirmed current `ProjectListPage.tsx` still uses `status === "cancelled"` as legacy `Stopped` and currently routes cancelled rows into the `completed` view.
- Updated `docs/task_339b_projects_registry_lifecycle_views_plan.md` with the Developer implementation plan:
  - frontend-only data source decision: base registry rows plus existing per-row lifecycle overlay via `getProjectLifecycle(project_id)`
  - `On-going`, `Planning`, `Closed`, and `All` view contract
  - stopped project classification rules
  - closed completed/admin labels and next-step copy
  - explicit no lifecycle write actions from registry
  - concrete post-approval file list
  - focused selector/component test plan
  - implementation validation commands
  - risks and mitigations
- Did not modify `frontend/`, `backend/`, or `tests/` product code.
- Did not update global `docs/task_board.md`.
- Did not modify TASK_340 source files.

Developer planning decision:

- Current frontend/API facts are sufficient for a frontend-only first implementation because `getProjectLifecycle(project_id)` already exists.
- No backend DTO change should be included in TASK_339B.
- If registry volume makes per-row lifecycle fetches too costly, a later backend/API summary enhancement should be proposed as a separate task.

Developer planning validation:

- `Test-Path docs\task_339b_projects_registry_lifecycle_views_plan.md` -> true.
- `Test-Path docs\lane_evidence\TASK_339B_projects-registry-lifecycle-views_developer.md` -> true.
- Keyword checks in the plan cover `ProjectRegistryRow`, `getProjectLifecycle`, `On-going`, `Planning`, `Closed`, `Closed: Completed`, `Closed: Administrative`, `projectRegistryLifecycleViews`, and `ProjectListPage.test.tsx`.
- `rg -n "[ \t]$" docs/task_339b_projects_registry_lifecycle_views_plan.md docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md` -> no matches.
- `git diff --check -- docs/task_339b_projects_registry_lifecycle_views_plan.md docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md` -> passed.
- `git status --short -- frontend backend tests` -> no output.
- `git status --short -- docs/task_board.md tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md docs/task_340_unified_project_workbench_shell_plan.md docs/lane_evidence/TASK_340_unified-shell-plan_planner.md` -> existing Planner/Integrator governance and restored-source dirt remains outside this Developer planning touch set; not modified by this pass.

Frontend Developer implementation pass:

- Read the required governance, task, plan, restored TASK_340 background, and evidence sources again before implementation.
- Loaded `$impeccable` product-register context and frontend architecture rules before editing frontend UI code.
- Used TDD for the TASK_339B lifecycle registry behavior:
  - added helper tests for view classification, business-readable labels, fallback behavior, and raw enum hiding
  - added ProjectListPage tests for default `On-going`, `Closed`, `Planning`, no lifecycle write actions, and lifecycle overlay failure fallback
- Implemented `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts` as a focused frontend selector/helper module.
- Updated `frontend/src/pages/ProjectListPage.tsx` to:
  - keep `listProjectRegistryRows()` as the base registry list
  - fetch accepted TASK_339A lifecycle overlays with `getProjectLifecycle(project_id)` per row
  - expose `On-going`, `Planning`, `Closed`, and `All` views
  - classify closed completed/admin projects into `Closed`
  - keep stopped formal/registered projects in `On-going`
  - keep stopped temporary/no-LTR projects in `Planning`
  - retain rows with compatibility labels when lifecycle overlay loading fails
  - keep registry actions read/navigation-oriented with `Open` only
- Updated `frontend/src/project-dashboard.css` with lifecycle badge and overlay warning styles.
- Did not modify backend code.
- Did not modify TASK_338 write guards.
- Did not implement TASK_340 shell, TASK_341, or TASK_342.
- Did not update global `docs/task_board.md`.
- Did not merge, commit, or push.

Frontend Developer implementation changed files:

- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `frontend/src/project-dashboard.css`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`

Frontend Developer implementation validation:

- Initial focused test run after adding tests was red as expected before implementation.
- `npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx` -> 2 files passed, 10 tests passed.
- `npm run build` from `frontend/` -> passed (`tsc -b && vite build`).
- `git diff --check -- frontend/src/pages/ProjectListPage.tsx frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.test.tsx frontend/src/project-dashboard.css docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md` -> passed; Git reported LF/CRLF working-copy warnings for existing tracked frontend files.
- `rg -n "[ \t]$" frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts frontend/src/pages/ProjectListPage.test.tsx docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md` -> no matches.
- `git status --short -- backend docs/task_board.md tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md docs/task_340_unified_project_workbench_shell_plan.md docs/lane_evidence/TASK_340_unified-shell-plan_planner.md` -> no backend output; existing `docs/task_board.md` modification and TASK_339B/TASK_340 untracked governance/source files remain outside this implementation pass.

Implementation risks / follow-ups:

- TASK_339B intentionally uses per-row lifecycle overlay calls. If registry volume makes this too chatty, propose a separate backend/API summary-overlay task rather than expanding this lane.
- Existing Planner/Integrator governance and restored-source worktree dirt may still need packaging review outside this Developer lane.

## Stop Point

TASK_339B frontend Developer implementation is complete and pending Reviewer review.

Developer stops here and does not route itself into Reviewer, Integrator, TASK_340, TASK_341, or TASK_342.

## Integrator Packaging / Readiness Gate

Date: 2026-06-27

Reviewer latest callback:

- Completion status: `reviewer_pass`
- `Reviewer implementation gate`: pass
- QA not required because approved registry filtering/copy/no-write-action behavior is covered by focused helper/component tests.
- Reviewer rerun: focused tests `2` files / `10` tests passed; frontend build passed.

Package accepted files:

- `docs/task_board.md`
- `tasks/TASK_339B_PROJECTS_REGISTRY_LIFECYCLE_VIEWS.md`
- `docs/task_339b_projects_registry_lifecycle_views_plan.md`
- `docs/lane_evidence/TASK_339B_projects-registry-lifecycle-views_developer.md`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/project-dashboard.css`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts`
- `frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts`
- `frontend/src/pages/ProjectListPage.test.tsx`
- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`

TASK_340 files are included only as restored source-consistency facts because TASK_339B board/task/plan/evidence reference them as required background. They do not authorize or implement Workbench shell runtime behavior.

Explicitly excluded dirty governance/orchestration residuals:

- `AGENTS.md`
- `.agents/skills/connlab-lane-orchestrator/`
- `.agents/skills/connlab-planner/`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`

Integrator validation rerun:

- `npm test -- --run src/features/projects-registry/projectRegistryLifecycleViews.test.ts src/pages/ProjectListPage.test.tsx` -> passed, `2` files and `10` tests.
- `npm run build` -> passed.
- `git diff --check -- <TASK_339B package files>` -> passed.
- `git diff --cached --check` after staging the accepted package -> passed.
- `git diff --cached --name-only -- AGENTS.md .agents docs/project_management backend tests` -> no output.

Integrator decision: `Integrator gate: accepted`.

Stop point: TASK_339B is complete. Do not start TASK_341, TASK_342, Workbench shell implementation, or Projects registry redesign beyond lifecycle views until Planner/Integrator creates or activates a separate approved lane.
