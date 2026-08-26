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
    "task_id": "TASK_SELECTED_APPLICATION_FORM_PROJECT_FOLDER_BINDING",
    "summary": "Bind project-folder application-form generation to the application form selected from a multi-form imported email.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Fix selected application-form identity propagation from intake review through project creation and folder generation; add regression coverage for selecting the second of two forms. No schema or API contract expansion.",
    "scope_paths": [
      "backend/application",
      "backend/api",
      "backend/modules/folder",
      "frontend/src",
      "tests/unit",
      "tests/integration",
      "docs/task_board.md"
    ],
    "risk_reasons": [
      "The corrected identity controls which existing application-form file is used by project-folder generation; regression coverage will use isolated fixtures and temporary directories."
    ],
    "activation_head": "87849d729bdaa98c689434068a1dfcb269878f51",
    "started_at": "2026-08-26T05:03:44.752650Z",
    "updated_at": "2026-08-26T05:03:44.752650Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_CONTACT_POINT_EXPLICIT_IDENTIFIERS_AND_ORDER",
    "tier": "standard",
    "subject": "db7f82da52190b6f8141c303cc2326b99717a609",
    "summary": "Preserve explicit contact point identifiers and input order independently from Point category.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-26T05:01:07.239546Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
