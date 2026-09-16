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
    "task_id": "TASK_FEE_FORM_IMPORT_AVAILABILITY",
    "summary": "Keep Import Fee Form available for editable saved drafts without conflating draft freshness with Fee authority.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove stale pricing-draft status as an Import Fee Form disable condition while retaining lifecycle read-only, loading, error, rebase-required, Confirm, and Cancel protections; add focused regression coverage for the post-autosave state.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "24d08449eac4084e27976c34d8b705179587de3e",
    "started_at": "2026-09-16T16:10:19.301501Z",
    "updated_at": "2026-09-16T16:10:19.301501Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_FORM_ACTION_LABELS",
    "tier": "micro",
    "subject": "93721fc79867142773c69359003002eee7794a16",
    "summary": "Replace the Fee Form status explanation with authority-aware English action labels.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭任务 before starting the Import Fee Form optimization.",
    "closed_at": "2026-09-16T16:08:21.989250Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
