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
    "task_id": "TASK_REMOVE_MATRIX_STEP_QUANTITY_SETUP_UI",
    "summary": "Remove the redundant Matrix Step quantity setup UI while preserving downstream and historical compatibility.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Remove the Matrix Editor Step quantity setup card and its page load/edit/save orchestration; keep Test Record unchanged, keep backend/API/storage compatibility, retain Point Profile and group sample authorities, and add regression coverage that the page no longer calls Step quantity APIs.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
      "frontend/src/features/matrix-editor/MatrixStepQuantityPanel.tsx",
      "frontend/src/features/matrix-editor/matrixStepQuantitySelectors.ts",
      "frontend/src/styles/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "136bddef309a690753ab24364dbc397e78e63373",
    "started_at": "2026-08-22T02:23:57.572083Z",
    "updated_at": "2026-08-22T02:23:57.572083Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FRONTEND_WARNING_MAINTENANCE",
    "tier": "standard",
    "subject": "d990f95b70df37d355c6fba3f54f7079c9d00f05",
    "summary": "Remove existing React act warnings and make evidence-based frontend bundle improvements without changing product behavior.",
    "disposition": "completed",
    "decision_ref": "User: 关闭 TASK_FRONTEND_WARNING_MAINTENANCE，并继续实施当前任务",
    "closed_at": "2026-08-22T02:23:36.831025Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
