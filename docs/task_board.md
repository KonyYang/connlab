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
    "task_id": "TASK_MATRIX_EDITOR_IMPORT_WORKFLOW_EXTRACTION",
    "summary": "Extract the Matrix Editor import orchestration into a deep feature hook without changing observable behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Move source selection, preview, locator validation, stale-preview refresh, and replace commit orchestration out of MatrixEditorWorkspace; reorganize affected tests by the public behavior seam; preserve API, UI, and business behavior; record but do not fix pre-existing business defects.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
      "frontend/src/features/matrix-editor/useMatrixImportWorkflow.ts",
      "frontend/src/features/matrix-editor/useMatrixImportWorkflow.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "c09508de1ff62a4f3f004223c8ef6d7b0f1801c5",
    "started_at": "2026-08-22T04:00:23.987819Z",
    "updated_at": "2026-08-22T04:00:23.987819Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_EDITOR_PURE_MODEL_EXTRACTION",
    "tier": "standard",
    "subject": "01b4f548e42b8150cf32a4a619ca32ca0ff0b23a",
    "summary": "Extract Matrix Editor draft and Step workspace pure models without changing observable behavior.",
    "disposition": "completed",
    "decision_ref": "User request 2026-08-22: 关闭",
    "closed_at": "2026-08-22T03:46:43.088734Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
