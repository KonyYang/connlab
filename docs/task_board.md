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
    "task_id": "TASK_MATRIX_EDITOR_CANCEL_DISCARD_IMPORTED_DRAFT",
    "summary": "Ensure Matrix Editor Cancel discards the exact current imported draft before returning to Workbench.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Matrix Editor session draft discard service, API/frontend behavior, and focused regression tests.",
    "scope_paths": [],
    "risk_reasons": [],
    "activation_head": "8640390fb7704ce9e1f1569652a60eeb2436a04d",
    "started_at": "2026-08-20T23:24:40.249562Z",
    "updated_at": "2026-08-20T23:24:40.249562Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_SETUP_RETURN_DRAFT_RESTORE",
    "tier": "standard",
    "subject": "15353785d68099f81e662291859ecd18892a48f5",
    "summary": "Preserve the newly imported Matrix draft when returning from a feature-card Setup workflow.",
    "disposition": "cancelled",
    "decision_ref": "User browser acceptance feedback on 2026-08-21: Matrix Editor Cancel exits but the discarded draft reappears on re-entry; retain prior restore implementation and continue with a follow-up fix.",
    "closed_at": "2026-08-20T23:24:01.317717Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
