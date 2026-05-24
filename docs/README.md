# ConnLab Documentation Map

Last Updated: 2026-05-24

This directory contains current product/architecture documentation, task plans, validation notes, and historical records. Not every document is current source of truth.

## Read Order

For any new task, use this order:

1. `../AGENTS.md`
2. `task_board.md`
3. current `tasks/TASK_XXX_*.md`
4. task-specific plan or architecture docs referenced by the task
5. this documentation map

## Current Source Documents

- `docs/task_board.md` - current task board and execution source of truth
- `docs/markdown_management_rules.md` - Markdown source-of-truth and archive rules
- `docs/task_archive_index.md` - completed task file archive index
- `docs/plan_archive_index.md` - completed task plan archive index
- `docs/runtime_governance_freeze_rule.md` - post-TASK_202 runtime governance rule
- `PRODUCT.md` - product purpose and design principles
- `README.md` - setup and entry point
- `docs/02_ARCHITECTURE_RULES.md` - architecture constraints
- `docs/frontend_architecture_rules.md` - frontend architecture constraints

## Current Phase And Runtime Direction

- `docs/stage_freeze_2026-05-15_project_workbench_matrix_approval_package.md`
- `docs/matrix_execution_phase_principles.md`
- `docs/project_workbench_runtime_console_information_architecture.md`
- `docs/step_centric_domain_foundation.md`
- `docs/interactive_step_token_read_model_projection_foundation.md`
- `docs/runtime_projection_service_and_read_model_boundary.md`
- `docs/first_runtime_implementation_slice_planning.md`

## Current Snapshots

- `docs/03_DOMAIN_MODEL.md` - domain model snapshot
- `docs/04_API_CONTRACTS.md` - API surface snapshot
- `docs/07_FUTURE_EXTENSION_MAP.md` - controlled future work map
- `docs/architecture_inventory_2026-05-15.md` - architecture inventory

## Task History

- `tasks/` contains active, planned, recently completed, and not-yet-archived task execution files.
- `tasks/completed/YYYY/` is the future archive location for completed task files after final board alignment.
- `docs/task_XXX_*_plan.md` files are review/history records for task planning. They are not automatically current product truth.
- `docs/completed_plans/YYYY/` is the future archive location for completed task plan files after final board alignment.
- `docs/task_board.md` remains authoritative for task status.
- `docs/task_plan_index.md` records the earlier Slice C decision and the DOCS_001 update that introduces controlled dry-run-first archiving.
- `docs/markdown_management_rules.md` defines archive eligibility and protected files.

## Historical And Archive Material

Historical phase plans, external AI modification logs, session notes, and old blueprints may contain obsolete wording. Treat them as context only unless confirmed by `../AGENTS.md`, `task_board.md`, or the current task.

Archive semantics are defined in `docs/archive/README.md`.

Common archive locations:

- `docs/archive/historical_plans/` - old phase-wide implementation plans
- `docs/archive/external_ai/` - external AI or manual modification records
- `docs/archive/legacy_blueprints/` - packed historical blueprints
- `docs/archive/validation_summaries/` - historical phase validation and smoke records
- `docs/archive/task_artifacts/` - historical task-related docs outside normal task/plan naming
