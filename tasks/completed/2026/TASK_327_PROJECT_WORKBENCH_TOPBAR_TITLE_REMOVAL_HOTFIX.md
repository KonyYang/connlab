# TASK_327_PROJECT_WORKBENCH_TOPBAR_TITLE_REMOVAL_HOTFIX

## Status

Complete.

## Context

The active Project Workbench page already shows the project identity as the main
header. The visible `Project Workbench` app-title text beside the back icon was
redundant in the current Workbench layout.

## Scope

- Remove the visible topbar `Project Workbench` title text.
- Keep the back-to-projects icon button and its accessible label.
- Keep the project identity heading and Workbench action buttons unchanged.
- Do not change Project Folder, Matrix, Fee, StepInstance, report, AI,
  permissions, LAN, or multi-user behavior.

## Validation

- `cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task327"`
- `cd frontend; npm run build`
