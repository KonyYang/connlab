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
    "task_id": "TASK_CONTACT_POINT_EXPLICIT_IDENTIFIERS_AND_ORDER",
    "summary": "Preserve explicit contact point identifiers and input order independently from Point category.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Update contact point expression parsing and downstream LLCR/CR projections so explicit numeric, PE/P-prefixed, HP-prefixed, and prefixed ranges retain user-entered identifiers and sequence; keep Point category as separate classification metadata.",
    "scope_paths": [
      "backend/application/contact_point_profile_expression.py",
      "backend/application/contact_point_profile_lifecycle_service.py",
      "backend/application/contact_point_profile_confirmed_consumer_adapter.py",
      "backend/application",
      "frontend/src/features/contact-measurement-setup",
      "tests/unit",
      "tests/integration",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "c6110215c574541cdcb34252f703bcf4c45f9778",
    "started_at": "2026-08-25T23:53:42.199459Z",
    "updated_at": "2026-08-26T00:05:04.733290Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CONTACT_POINT_EXPLICIT_IDENTIFIERS_AND_ORDER",
      "stage": "qa",
      "status": "running",
      "summary": "Red-green implementation and two-axis self-review complete; run final related backend/frontend validation, production build, and browser verification.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_SAMPLE_QUANTITY_FOOTNOTE_NORMALIZATION",
    "tier": "standard",
    "subject": "11326fc4f9b5537cd6f2beab8aa2c19058d91c41",
    "summary": "Recognize footnoted whole-number Matrix sample quantities such as 3(a) throughout import and confirmation.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-25T10:55:56.438901Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
