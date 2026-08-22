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
    "task_id": "TASK_MATRIX_EDITOR_DRAFT_PERSISTENCE_EXTRACTION",
    "summary": "Extract Matrix Editor draft autosave and cancel persistence into one deep feature hook without changing observable behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Move autosave scheduling, save identity/token state, authority/source persistence identity, import persistence reset, and Cancel wait/abort/discard orchestration out of MatrixEditorWorkspace; preserve API, UI, confirmation behavior, and business rules; record but do not fix pre-existing business defects.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
      "frontend/src/features/matrix-editor/useMatrixDraftPersistence.ts",
      "frontend/src/features/matrix-editor/useMatrixDraftPersistence.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "4e779572248cdf17361ba1fa0ad8dd8ce4f7e64d",
    "started_at": "2026-08-22T04:34:15.462259Z",
    "updated_at": "2026-08-22T04:34:15.462259Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_EDITOR_IMPORT_WORKFLOW_EXTRACTION",
    "tier": "standard",
    "subject": "1e14d8ab1d7a2e95356749446b2bd03442189673",
    "summary": "Extract the Matrix Editor import orchestration into a deep feature hook without changing observable behavior.",
    "disposition": "completed",
    "decision_ref": "User request 2026-08-22: 关闭",
    "closed_at": "2026-08-22T04:25:42.691712Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
