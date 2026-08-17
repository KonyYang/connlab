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
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_CARD_SELECTION",
    "summary": "Replace per-file Select buttons with accessible clickable file cards in the browser Matrix Import source picker.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove the redundant per-row Select button. Make each blue filename card the explicit candidate confirmation target for mouse click and Enter or Space, retain filename-only display, focus visibility, busy disabled semantics, Cancel and Upload other file behavior, and verify the real browser layout. Do not change backend selection authority, desktop native picker, read-only behavior, persistence, or external files.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
      "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
      "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx",
      "frontend/src/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "6b7c79b19355c1bb7442fbf87a2f81d4042dc82d",
    "started_at": "2026-08-17T13:05:03.829103Z",
    "updated_at": "2026-08-17T13:05:03.829103Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST",
    "tier": "standard",
    "subject": "f6bbf843d25aa7d8b288cc467d2ef0219e686604",
    "summary": "Complete the ordinary-browser Matrix Import source picker with direct target-directory Word/PDF candidates and stale-safe opaque selection while preserving desktop and read-only behavior.",
    "disposition": "cancelled",
    "decision_ref": "User: 取消当前交付并继续修改",
    "closed_at": "2026-08-17T13:04:44.755220Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
