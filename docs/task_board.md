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
    "task_id": "TASK_MATRIX_TEST_POINTS_FEE_EVALUATION_SYNC",
    "summary": "Ensure Matrix test-point setup is consistently propagated into Fee Evaluation derived pricing data.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Trace and fix the existing Matrix contact-measurement test-point authority through confirmation, fee draft rebase, and Fee Evaluation reads; add regression coverage without changing unrelated pricing authority.",
    "scope_paths": [
      "backend/application",
      "backend/modules/fee_evaluation",
      "backend/api",
      "tests/unit",
      "tests/integration",
      "frontend/src"
    ],
    "risk_reasons": [],
    "activation_head": "1297fa6f2672e0e6ffa0c75a6a71b25ed16ca5aa",
    "started_at": "2026-08-21T04:41:41.725323Z",
    "updated_at": "2026-08-21T04:41:41.725323Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PDF_MATRIX_GROUP_PREFIX_FOOTNOTE_NORMALIZATION",
    "tier": "standard",
    "subject": "a370ad8de4f5973e4612de956688f590405baa2b",
    "summary": "Include prefixed letter Matrix groups such as Group P(b) when parsing PDF qualification tables.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭 on 2026-08-21 after delivery.",
    "closed_at": "2026-08-21T04:37:54.202883Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
