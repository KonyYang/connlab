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
    "task_id": "TASK_FEE_FORM_ACTION_LABELS",
    "summary": "Replace the Fee Form status explanation with authority-aware English action labels.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Update the existing Fee Form button label to Download Draft Fee Form or Generate Official Fee Form based on current confirmed authority, preserve blocker/error/success notices, and add focused frontend regression tests.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "00831553214ec56912db7b3f27eeb786a50c8020",
    "started_at": "2026-09-16T15:51:59.823678Z",
    "updated_at": "2026-09-16T15:51:59.823678Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_CONFIRMED_STATUS_SIGNATURE_CANONICALIZATION",
    "tier": "micro",
    "subject": "71e61dd0055f6b75e5e4d9de4ec71a0b2cdbabe6",
    "summary": "Normalize optional Fee manual-row identity fields so a confirmed Fee remains visibly confirmed after re-entry.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭任务 in the current turn.",
    "closed_at": "2026-09-16T15:47:18.494991Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
