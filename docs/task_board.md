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
    "task_id": "TASK_PROJECT_FOLDER_OPEN_REFRESH_AFTER_CREATE",
    "summary": "Refresh Folder Actions immediately after successful project-folder creation so Open is available without a page reload.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Project Workbench frontend model create-folder state refresh and focused regression coverage.",
    "scope_paths": [
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "fb9f2c500211672195618c16c76cf6a79115fc81",
    "started_at": "2026-08-26T22:57:41.086200Z",
    "updated_at": "2026-08-26T22:57:41.086200Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_LLCR_SN_TEXT_WARNING_SUPPRESSION",
    "tier": "micro",
    "subject": "7783459c05068f20d063c8a780d979dcf92393c7",
    "summary": "Suppress Excel number-stored-as-text warnings for LLCR/CR workbook S/N identifier ranges while preserving identifier text and gray unused-sample cells.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested close after completed delivery.",
    "closed_at": "2026-08-26T22:39:49.894977Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
