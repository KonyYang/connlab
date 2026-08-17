# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/TASK_WORKFLOW.md`.
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
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST",
    "summary": "Complete the ordinary-browser Matrix Import source picker with direct target-directory Word/PDF candidates and stale-safe opaque selection while preserving desktop and read-only behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Implement only missing behavior on current master: resolve Submitted Material before parsed intake attachments; list direct .doc/.docx/.pdf files without paths; preserve picker states, desktop native selection, read-only zero calls, and existing Matrix preview authority; bind opaque IDs to directory, filename, and current file content or instance; add proportional regressions and browser verification; no persistence, recursive scan, external mutation, or legacy workflow restoration.",
    "scope_paths": [],
    "risk_reasons": [],
    "activation_head": "f79a095c5db02ed8143d3cfd41099e54fece801a",
    "started_at": "2026-08-17T12:17:24.839564Z",
    "updated_at": "2026-08-17T12:38:17.317052Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST",
      "stage": "developer_validation",
      "status": "running",
      "summary": "Current master implementation and focused regressions are complete; backend/API tests, frontend focused tests, build, and responsive browser smoke pass before independent review and QA.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": null,
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
