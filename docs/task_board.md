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
    "task_id": "TASK_MATRIX_RELEASE_SMOKE_20260905",
    "summary": "Build the Matrix reliability browser release and validate its isolated local operator flow; deliver a second-computer smoke checklist.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Package existing verified code in a new directory; isolate all runtime data, preserve current installation and real data; no unrelated UI changes or deployment to other computers.",
    "scope_paths": [
      "docs/project_management/MATRIX_RELEASE_SMOKE_20260905.md"
    ],
    "risk_reasons": [],
    "activation_head": "ef44aca3986716a4681372a96ed28a3b5e7c8785",
    "started_at": "2026-09-05T02:08:04.985893Z",
    "updated_at": "2026-09-05T03:04:31.774038Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_RELEASE_SMOKE_20260905",
      "stage": "revision",
      "status": "running",
      "summary": "user: default Workbench step numbers to initial black state; remove simulated status colors",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_EXPERIENCE_RELIABILITY_BATCH1",
    "tier": "standard",
    "subject": "7ddd40a14fa8ce82423c07ffa53d25dfa1a1cb57",
    "summary": "Improve Matrix loading, registry status consistency, and edit-save-reopen-confirm-export reliability.",
    "disposition": "completed",
    "decision_ref": "user:关闭 Matrix 优化任务",
    "closed_at": "2026-09-05T01:53:25.379609Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
