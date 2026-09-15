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
    "task_id": "TASK_MATRIX_GROUP_IDENTITY_B",
    "summary": "Audit Matrix draft and confirmed-authority identity integrity against the real local database, then define a previewable and reversible repair workflow plus a simpler retention and UI policy for draft and authority history.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Read-only database and code audit, evidence-backed repair and retention design, and any narrowly required read-only audit tooling or tests. Do not mutate operator data, delete history, or change authority records in this phase.",
    "scope_paths": [
      "backend",
      "scripts",
      "tests",
      "docs"
    ],
    "risk_reasons": [],
    "activation_head": "2d133f93b2289d0cbb1a94a96a5743dc9339fe6e",
    "started_at": "2026-09-15T22:46:59.607261Z",
    "updated_at": "2026-09-15T22:46:59.607261Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_GROUP_IDENTITY_A",
    "tier": "standard",
    "subject": "6826d851a399ebbbf201bfe9084345c5c81aad83",
    "summary": "Prevent duplicate Matrix group identities across add, insert, duplicate, save, confirm, reload, and export while preserving existing group data for explicit diagnosis.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭 in the current turn.",
    "closed_at": "2026-09-15T22:37:03.852203Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
