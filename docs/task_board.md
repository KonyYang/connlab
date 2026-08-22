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
    "task_id": "TASK_MATRIX_EDITOR_RENDER_AND_TEST_ORGANIZATION",
    "summary": "Organize Matrix Editor rendering and split public UI tests into at most three behavioral groups without changing observable behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Extract only render modules with small cohesive interfaces: Import modal and Matrix Step Workspace; keep the high-prop Grid and shallow Completion dock in MatrixEditorWorkspace; split Workspace public-UI tests into import, editing, and save/cancel/confirm lifecycle groups with shared fixtures; do not add private-function or source-text tests.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/useMatrixImportWorkflow.ts",
      "frontend/src/features/matrix-editor/MatrixImportDialog.tsx",
      "frontend/src/features/matrix-editor/MatrixStepWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.import.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "6ff54f9e0e7ff06e7f23c53b6caccf0f98ce0c4e",
    "started_at": "2026-08-22T04:52:39.260402Z",
    "updated_at": "2026-08-22T04:52:39.260402Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_EDITOR_DRAFT_PERSISTENCE_EXTRACTION",
    "tier": "standard",
    "subject": "632a5b57f8087185ea7db033657234aa34403113",
    "summary": "Extract Matrix Editor draft autosave and cancel persistence into one deep feature hook without changing observable behavior.",
    "disposition": "completed",
    "decision_ref": "User request 2026-08-22: 关闭",
    "closed_at": "2026-08-22T04:49:39.287022Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
