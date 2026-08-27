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
    "task_id": "TASK_TEST_STATUS_WORKBOOK",
    "summary": "Add Matrix Editor Test Status draft download and authoritative Submitted Material workbook generation using shared VBA-compatible projection logic.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Implement the User-requested Test Status workbook draft and authoritative project-folder output without changing Matrix authority semantics.",
    "scope_paths": [
      "backend/application",
      "backend/api",
      "backend/infrastructure/office",
      "backend/domain/enums.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor",
      "tests/unit",
      "tests/integration",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "161d4a027affff0d0c91d6d81ea1260d581c2df0",
    "started_at": "2026-08-26T23:29:40.759240Z",
    "updated_at": "2026-08-26T23:29:40.759240Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_OPEN_REFRESH_AFTER_CREATE",
    "tier": "micro",
    "subject": "db40fdb6e3e5d7bce14ae4ce172ebcb35c6f986a",
    "summary": "Refresh Folder Actions immediately after successful project-folder creation so Open is available without a page reload.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested close after completed delivery.",
    "closed_at": "2026-08-26T23:03:46.456853Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
