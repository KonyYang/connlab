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
    "task_id": "TASK_MATRIX_IMPORT_SETUP_RETURN_DRAFT_RESTORE",
    "summary": "Preserve the newly imported Matrix draft when returning from a feature-card Setup workflow.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fix Matrix Editor navigation-state restoration so Import Matrix results remain active after entering Setup and returning, without changing Matrix authority or unrelated workflows.",
    "scope_paths": [],
    "risk_reasons": [],
    "activation_head": "c9e5343188f04d7b17a9b2927b388d6db7c225ed",
    "started_at": "2026-08-20T22:38:08.460457Z",
    "updated_at": "2026-08-20T22:38:08.460457Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_DOCS_ROOT_INFORMATION_ARCHITECTURE_CLEANUP",
    "tier": "standard",
    "subject": "9cc494a21d7e1061e77e7619377d45007e6bb6c0",
    "summary": "Consolidate historical documentation indexes, relocate and refresh the Intake/Precheck contract, and retire obsolete archive tooling without changing product behavior.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭 on 2026-08-21.",
    "closed_at": "2026-08-20T22:37:07.262264Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
