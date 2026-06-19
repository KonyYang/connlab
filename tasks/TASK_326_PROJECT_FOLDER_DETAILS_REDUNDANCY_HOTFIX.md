# TASK_326_PROJECT_FOLDER_DETAILS_REDUNDANCY_HOTFIX

## Status

Complete.

## Context

In the active Project Workbench Matrix workspace, the bottom `Project folder details`
disclosure repeated Project Folder workflow information that was already represented
by the right-side `Folder Action` card. The duplicated details increased vertical
noise below the Matrix workspace and made the operator-facing path feel less direct.

## Scope

- Remove the bottom `Project folder details` disclosure from the active Matrix
  workspace only.
- Keep the `Folder Action` card as the single visible Project Folder action entry
  in the active Matrix workspace.
- Keep `ProjectFolderTaskList` available for lifecycle/setup contexts that still
  need the full checklist.
- Do not change Project Folder backend behavior, conflict handling, task selection
  rules, folder generation, Matrix authority, Fee authority, StepInstance, report,
  AI, permissions, LAN, or multi-user scope.

## Validation

- `cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task326"`
- `cd frontend; npm run build`
