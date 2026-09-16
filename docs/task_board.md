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
    "task_id": "TASK_FEE_GROUP_SUMMARY_PLACEMENT",
    "summary": "Move the Preview group and Total Testing Fee card into the totals row and replace the redundant Grand Cost card.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Recompose the Fee Evaluation preview header and totals row so the group selector/selected total occupies the former Grand Cost slot, keep filtering and calculations unchanged, adjust responsive styling, and add focused layout regression tests.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.test.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "c76588889a9a66b3d01ed269ad67ad41dd40e047",
    "started_at": "2026-09-16T16:22:17.929009Z",
    "updated_at": "2026-09-16T16:22:17.929009Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_FORM_IMPORT_AVAILABILITY",
    "tier": "micro",
    "subject": "c7e050cdd95bbc9db29a74933961ea7b48fe9e46",
    "summary": "Keep Import Fee Form available for editable saved drafts without conflating draft freshness with Fee authority.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭 in the current turn.",
    "closed_at": "2026-09-16T16:19:32.546279Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
