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
    "task_id": "TASK_FOLDER_WARNING_INITIAL_FLASH",
    "summary": "Avoid flashing historic generation errors while the latest recovery preview is loading.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Show neutral checking state during initial recovery preview, then show current ready or blocked result; preserve recovery journal and all write guards.",
    "scope_paths": [
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "94d73a7934cbc2d14ad6183fa55d1dfbdad5f08a",
    "started_at": "2026-09-10T14:06:05.718092Z",
    "updated_at": "2026-09-10T14:06:05.718092Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_FORM_IMPORT",
    "tier": "standard",
    "subject": "ef88b77fdda44c8e85e9369f94b460c7db381748",
    "summary": "Import Fee Form into editable draft with same-Matrix restoration and cross-project price reuse.",
    "disposition": "completed",
    "decision_ref": "User explicitly closes Fee import and starts warning flash fix.",
    "closed_at": "2026-09-10T14:06:05.718092Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
