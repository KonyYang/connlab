# Task Plan Index

Last Updated: 2026-05-16
Status: Slice C decision record

## Decision

`TASK_203 Slice C` decision:

- Keep `docs/task_XXX_*_plan.md` files in place.
- Do not move them into `docs/archive/task_plans/` in this slice.

Reason:

- `docs/task_board.md` contains extensive historical references to existing plan paths.
- Path stability is more important than directory compactness at this stage.
- Current runtime direction emphasizes execution velocity and low-risk changes.

## How To Use Task Plan Files

- Treat each `docs/task_XXX_*_plan.md` as planning/review history for that task.
- Use `docs/task_board.md` as the authoritative status source.
- Use the corresponding `tasks/TASK_XXX_*.md` for execution scope.
- Do not treat older plan files as current product truth unless referenced by the active task.

## Current Plan File Pattern

Pattern:

```text
docs/task_XXX_*_plan.md
```

Examples:

- `docs/task_194_matrix_execution_phase_product_realignment_plan.md`
- `docs/task_195_project_workbench_runtime_console_information_architecture_plan.md`
- `docs/task_200_first_runtime_implementation_slice_planning_plan.md`
- `docs/task_201_projection_dto_and_token_reference_builder_minimal_slice_plan.md`
- `docs/task_202_runtime_projection_composition_helper_minimal_slice_plan.md`
- `docs/task_203_documentation_information_architecture_cleanup_plan.md`

## Future Revisit Trigger

Revisit bulk migration of task plan files only when both conditions are true:

1. `docs/task_board.md` reference format is intentionally refactored.
2. A dedicated path-rewrite validation task is approved.

