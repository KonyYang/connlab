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
    "task_id": "TASK_FEE_MANUAL_SAMPLE_QTY_HYDRATION",
    "summary": "Restore saved manual sample quantities when the current Matrix requires quantity confirmation, so Update Fee is not blocked after a valid reload.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Fix Fee Evaluation saved-draft hydration for manual sample quantities such as 5+5(d), with a focused regression test.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts",
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.test.ts"
    ],
    "risk_reasons": [],
    "activation_head": "ce7539c69dfbaa4be7f7c9b7a54bfcef38ffc393",
    "started_at": "2026-08-24T11:21:45.816433Z",
    "updated_at": "2026-08-24T11:21:45.816433Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_PACKAGE_DRAFT_PREVIEW",
    "tier": "standard",
    "subject": "7a7a2f6654e782747dd5c5438c4bcd100d34eff1",
    "summary": "Allow Project Package preview to remain usable from a Matrix draft; only formal actions require confirmed Matrix authority.",
    "disposition": "completed",
    "decision_ref": "user-message-2026-08-24-close",
    "closed_at": "2026-08-24T05:01:02.837518Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
