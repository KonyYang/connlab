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
    "task_id": "TASK_PROJECT_FOLDER_SINGLE_ENTRY",
    "summary": "Unify project folder update and recovery entry; retain explicit advanced rebuild confirmation.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Single UI entry and read-only recovery guidance using existing generation safety guards; no engine rewrite or real output operations.",
    "scope_paths": [
      "frontend/src/features/project-workbench",
      "frontend/src/api/client.ts",
      "backend/api/project_folder_generation_composition.py",
      "tests",
      "docs/project_management"
    ],
    "risk_reasons": [],
    "activation_head": "b70a1dea611d83e8f2e9ed8b8e063e5240f63446",
    "started_at": "2026-09-12T01:36:01.264661Z",
    "updated_at": "2026-09-12T01:36:01.264661Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_RELEASE_PUBLICATION_DIAGNOSTICS",
    "tier": "standard",
    "subject": "4c2fc3a9056c65b524f71606542555a7abc0d74f",
    "summary": "Add correlated, privacy-bounded diagnostics for Fee Form publication and project folder generation, including Office child failures and a verified browser release.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭.",
    "closed_at": "2026-09-12T00:45:34.911362Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
