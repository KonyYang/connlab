# TASK_329_MATRIX_PROJECTION_TEST_ITEM_WEIGHT_HOTFIX

## Status

Complete.

## Context

In the Project Workbench Matrix projection table, the `Test item` body cells were
rendered in bold. This made descriptive test item names visually heavier than the
table needed and competed with the Matrix token content.

## Scope

- Change Matrix projection body row header cells (`Test item` cells) from bold to
  normal font weight.
- Keep table structure, Matrix tokens, meta rows, and selection behavior unchanged.
- Do not change Matrix data, Project Folder, Fee, StepInstance, report, AI,
  permissions, LAN, or multi-user behavior.

## Validation

- `cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task329"`
- `cd frontend; npm run build`
