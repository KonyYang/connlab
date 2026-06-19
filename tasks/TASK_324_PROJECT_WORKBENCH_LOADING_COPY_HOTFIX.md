# TASK_324 Project Workbench Loading Copy Hotfix

> Status: Approved and implemented after user request.
> Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation

## Goal

Avoid showing transient `Loading project workbench...` copy when entering Project Workbench quickly.

## Approved Scope

- Hide short-lived Workbench loading copy.
- Keep failure/error rendering unchanged.
- Do not change backend loading, API calls, Project Workbench data model, or business workflow.

## Validation

- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task324"`
- `cd frontend; npm test -- --run ProjectWorkbenchLayout --watch=false`
- `cd frontend; npm run build`
