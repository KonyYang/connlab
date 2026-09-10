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
    "task_id": "TASK_PROJECT_REGISTRY_ACTION_ICON_BUTTONS",
    "summary": "Project registry actions are compact icon buttons placed directly beside Open Workbench.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Replace the project registry text action controls with compact accessible icon buttons placed side by side, preserving lifecycle conditions, tooltips, confirmation dialogs, and handlers.",
    "scope_paths": [
      "frontend/src/pages/ProjectListPage.tsx",
      "frontend/src/pages/ProjectListPage.test.tsx",
      "frontend/src/project-dashboard.css"
    ],
    "risk_reasons": [],
    "activation_head": "a86deccd2da4142f95498384ae354b30e5bb10e5",
    "started_at": "2026-09-10T23:23:23.949643Z",
    "updated_at": "2026-09-10T23:48:52.235759Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_REGISTRY_ACTION_ICON_BUTTONS",
      "stage": "revision",
      "status": "running",
      "summary": "User requests more semantic icons for Open Workbench and Close project.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_CONFIRM_RETURN",
    "tier": "micro",
    "subject": "68311a4c8340a387e728f9eb6198d1e3c9bb8d6d",
    "summary": "Rename Update Fee to Confirm and return to Project Workbench after successful Fee authority confirmation.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested: 关闭",
    "closed_at": "2026-09-10T23:15:31.779670Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
