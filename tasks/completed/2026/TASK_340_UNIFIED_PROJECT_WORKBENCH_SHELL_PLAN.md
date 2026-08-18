# TASK_340 Unified Project Workbench Shell Plan

Status: complete
Lane: unified-shell-plan
Owner Role: Planner/Designer
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## 1. Purpose

Plan the Unified Project Workbench Shell information architecture and UX direction for the Project Lifecycle + Unified Workbench series.

This task turns the accepted TASK_336 lifecycle contract into a reviewable shell plan. It must help future implementation lanes reduce the current 5+2 style mental model into one lifecycle-aware Project Workbench surface.

## 2. Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/TASK_EXECUTION_SKILL.md`
- `tasks/TASK_336_PROJECT_LIFECYCLE_AND_UNIFIED_WORKBENCH_CONTRACT.md`
- `docs/task_336_project_lifecycle_and_unified_workbench_contract_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- `$impeccable` ConnLab product and design guidance
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- Existing Project Workbench IA/reference docs and current Workbench frontend files, read-only

## 3. Outputs

- `docs/task_340_unified_project_workbench_shell_plan.md`
- updated `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- optional TASK_340 lane status note in `docs/task_board.md`

## 4. Scope

The plan must cover:

- unified Workbench shell regions
- active, stopped, closed completed, and closed administrative shell states
- readonly banners and action rules
- current-feature-only navigation
- how the shell reduces the current 5+2 mental model
- future implementation smoke checklist
- risks, serial dependencies, and acceptance criteria

## 5. Non-Goals

This task must not:

- implement frontend UI
- change frontend runtime behavior
- change backend runtime behavior
- change API contracts
- change database schema
- change lifecycle status implementation
- change Matrix, Fee, Project Folder, Basic Information, LTR, public-drive, Office, or output behavior
- implement TASK_337B, TASK_337A, TASK_338, TASK_339A, TASK_339B, TASK_341, or any product implementation lane
- expose StepInstance, Report generation, AI review, permissions, LAN/server, or multi-user scope as current UI features

## 6. Allowed Files

May touch:

- `tasks/TASK_340_UNIFIED_PROJECT_WORKBENCH_SHELL_PLAN.md`
- `docs/task_340_unified_project_workbench_shell_plan.md`
- `docs/lane_evidence/TASK_340_unified-shell-plan_planner.md`
- `docs/task_board.md` only for Planner lane status/evidence note updates

Must not touch:

- `frontend/`
- `backend/`
- tests
- runtime configuration
- Office gateway files
- database migrations or schema files
- unrelated task/evidence files

## 7. Validation

Documentation-only validation:

- task file exists
- shell plan exists
- plan includes active, stopped, closed completed, and closed administrative states
- plan includes readonly banners/action rules
- plan includes current-feature-only navigation and future-scope exclusions
- plan includes smoke checklist for future implementation lane
- evidence file records changed files, checks, and stop point

## 8. Stop Point

Stop after the plan and evidence are ready for user review. Do not implement product code. Do not execute TASK_337B or any implementation lane.
