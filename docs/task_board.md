# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/TASK_WORKFLOW.md`.
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
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_FOOTER_BUTTON_STYLE",
    "summary": "Match the Matrix Import source picker footer buttons to the Matrix Editor button style with white default surfaces, rounded borders, bold text, and blue hover/focus feedback.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Style the existing Cancel and Upload other file controls only; preserve their behavior and picker state handling.",
    "scope_paths": [
      "frontend/src/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "86063b97254e204eb3ded4ff72c56085139acdec",
    "started_at": "2026-08-17T13:23:14.326507Z",
    "updated_at": "2026-08-17T13:23:14.326507Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_CARD_SELECTION",
    "tier": "micro",
    "subject": "c2ac7409efa763587d7dfb596e59f98fb27dc0e3",
    "summary": "Replace per-file Select buttons with accessible clickable file cards in the browser Matrix Import source picker.",
    "disposition": "cancelled",
    "decision_ref": "User: 取消当前交付并继续修改",
    "closed_at": "2026-08-17T13:20:50.365406Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
