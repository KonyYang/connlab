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
    "task_id": "TASK_PROJECT_FOLDER_SCHEDULE_PREFLIGHT",
    "summary": "Validate confirmed Project Schedule before Project Folder generation starts so the workflow never reaches Customer Feedback with a missing date authority.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Project Folder schedule preflight and public API regression coverage.",
    "scope_paths": [
      "backend/api/project_folder_generation_composition.py",
      "tests/integration/test_project_folder_generation_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "76c3326049132ac5c8f4a91291c70f42b40ee595",
    "started_at": "2026-09-09T05:03:10.214492Z",
    "updated_at": "2026-09-09T05:03:10.214492Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_REGISTRY_RECOVERY",
    "tier": "high_risk",
    "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
    "summary": "Simplify project closure and implement recoverable project deletion, conflict-safe restore/history, and exclusion from active registries and work queues.",
    "disposition": "completed",
    "decision_ref": "用户明确要求：关闭",
    "closed_at": "2026-09-09T04:41:20.897076Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
