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
    "task_id": "TASK_FEE_CONFIRM_SPEND_TIME_ROUNDTRIP",
    "summary": "Fix Fee confirmation after editing Visual Inspection man-hours",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Reproduce and correct automatic spend-time mapping and confirmation roundtrip without losing manual edits",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts",
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "b7154f4ca5f2c1d00df1b7a244dd94d0aaab1c29",
    "started_at": "2026-09-16T23:14:33.687894Z",
    "updated_at": "2026-09-16T23:43:17.627413Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_CONFIRM_SPEND_TIME_ROUNDTRIP",
      "stage": "revision",
      "status": "running",
      "summary": "User approved audited Fee roundtrip calculation confirmation cancel and retry fixes",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_VISUAL_INSPECTION_DEFAULT_TIME",
    "tier": "standard",
    "subject": "98da3fb24ac424fb77a5349bd81c320cdbf8a21f",
    "summary": "Set Visual Inspection default spend time to 0.5 without overwriting deliberate fee edits",
    "disposition": "completed",
    "decision_ref": "User requested closure",
    "closed_at": "2026-09-16T23:09:25.184863Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
