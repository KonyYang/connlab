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
  "state": "ready_for_close",
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
    "updated_at": "2026-08-17T13:17:02.683144Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_CARD_SELECTION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_CARD_SELECTION",
      "subject": "c2ac7409efa763587d7dfb596e59f98fb27dc0e3",
      "summary": "The browser Matrix Import source picker now uses each filename card as the accessible selection control, with no nested Select button.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx",
        "frontend/src/workbench.css"
      ],
      "validation": [
        {
          "name": "focused frontend tests",
          "status": "passed",
          "result": "54 passed"
        },
        {
          "name": "frontend production build",
          "status": "passed",
          "result": "134 modules built"
        },
        {
          "name": "browser verification",
          "status": "passed",
          "result": "603x831 card click, fit, preview transition, cancel, and console checks"
        },
        {
          "name": "git diff check",
          "status": "passed",
          "result": "clean"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented, self-reviewed, and validated the scoped micro change."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Committed cleanly on current master at the reported subject."
      }
    }
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
