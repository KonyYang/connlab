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
    "task_id": "TASK_FEE_VISUAL_INSPECTION_DEFAULT_TIME",
    "summary": "Set Visual Inspection default spend time to 0.5 without overwriting deliberate fee edits",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Trace and correct the fee-draft default/rebase path so Visual Inspection starts at 0.5 hours while preserving explicitly edited current fee rows.",
    "scope_paths": [
      "backend/application/confirmed_matrix_fee_draft_service.py",
      "backend/application/fee_evaluation_pricing_draft_v2_rebase.py",
      "backend/modules/fee_evaluation/fee_default_fill.py",
      "tests/unit/test_confirmed_matrix_fee_draft_service.py",
      "tests/unit/test_fee_evaluation_pricing_draft_v2_rebase.py"
    ],
    "risk_reasons": [],
    "activation_head": "e4f66b9a1f44c69d974874b6a5a4d9b25d94a589",
    "started_at": "2026-09-16T22:52:34.891033Z",
    "updated_at": "2026-09-16T22:52:34.891033Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_CONFIRMED_DRAFT_HYDRATION",
    "tier": "standard",
    "subject": "0869c0bcb9b3d8cf5de0955d887dba8aabb6a96d",
    "summary": "Restore confirmed Fee Form authority after reopening Fee Evaluation instead of incorrectly reverting to Draft.",
    "disposition": "completed",
    "decision_ref": "User requested task closure after Fee authority, sample quantity, and LLCR/CR point linkage verification.",
    "closed_at": "2026-09-16T22:43:39.772723Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
