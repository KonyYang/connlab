# TASK_328_PROJECT_WORKBENCH_TOPBAR_ICON_GAP_HOTFIX

## Status

Complete.

## Context

After removing the visible `Project Workbench` topbar title, the left icon column
still reserved the old fixed title width. This left a large empty gap between the
back-to-projects icon button and the project identity heading.

## Scope

- Make the Workbench topbar left icon column content-sized instead of fixed-width.
- Remove the unused divider/padding from the icon-only app-title container.
- Keep the back-to-projects button, project identity heading, and action buttons
  unchanged.
- Do not change Project Folder, Matrix, Fee, StepInstance, report, AI,
  permissions, LAN, or multi-user behavior.

## Validation

- `cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task328"`
- `cd frontend; npm run build`
