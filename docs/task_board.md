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
    "task_id": "TASK_FEE_ADDITIVE_SAMPLE_QUANTITY_DEFAULTS",
    "summary": "Fee Evaluation automatically sums additive Matrix sample quantity expressions such as 3+3 for Units and keeps Sample preparation fully discounted by default.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fee draft default calculation, safe draft rebase behavior, and focused frontend/API verification for additive sample quantities and Sample preparation discount.",
    "scope_paths": [
      "backend/modules/fee_evaluation",
      "backend/application",
      "tests/unit",
      "tests/integration",
      "frontend/src/features/fee-evaluation"
    ],
    "risk_reasons": [],
    "activation_head": "53d063e35ce570a2735226c708e5496b96372e07",
    "started_at": "2026-09-08T22:43:11.360327Z",
    "updated_at": "2026-09-08T23:18:27.939464Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_ADDITIVE_SAMPLE_QUANTITY_DEFAULTS",
      "stage": "revision",
      "status": "running",
      "summary": "User requested unmatched Fee Evaluation rows default to per sample and use the first sample count term, so 3+3 yields Units 3.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_SCHEDULE_AUTHORITY",
    "tier": "high_risk",
    "subject": "e05cc7594605e6d2a38a50951978cf5d534830bc",
    "summary": "Establish Project Schedule as an independent authority, remove duplicate schedule inputs from Basic Information, and source official document dates from the confirmed schedule.",
    "disposition": "completed",
    "decision_ref": "User: 关闭",
    "closed_at": "2026-09-08T22:17:38.248101Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
