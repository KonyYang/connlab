# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> WIP=1. GPT-5.6 Sol routes work as micro, standard, or high risk and runs routine stages
> automatically until the User's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_WORKBENCH_DETAILS_TOGGLE_STYLE",
    "summary": "Move the workbench-details toggle to the left and match the Test Report button style.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Adjust only the Project Workbench details-toggle placement and visual treatment, with focused UI regression coverage.",
    "scope_paths": [
      "frontend/src/features/project-workbench/ProjectWorkbenchExecutionConsole.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "f377e9900659cb500ab88cd366c85a8c2ade67fb",
    "started_at": "2026-09-13T02:40:30.446522Z",
    "updated_at": "2026-09-13T02:40:30.446522Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FOLDER_GENERATION_EFFICIENCY",
    "tier": "standard",
    "subject": "0270448009eabe5bf7ab69e6b70e59563b59cb7a",
    "summary": "Reduce idle generation polling and measure repeated form preflight",
    "disposition": "completed",
    "decision_ref": "User requested closure in this conversation.",
    "closed_at": "2026-09-13T02:29:18.510336Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
