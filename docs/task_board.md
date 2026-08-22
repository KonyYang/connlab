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
    "task_id": "TASK_MATRIX_EDITOR_PURE_MODEL_EXTRACTION",
    "summary": "Extract Matrix Editor draft and Step workspace pure models without changing observable behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Preserve the Matrix Editor external interface, DOM, API calls, copy, and behavior while moving pure draft/signature/request and Step validation/preview/notes logic into two deep internal modules.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "frontend/src/features/matrix-editor/matrixStepWorkspaceModel.ts",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.durationAuthority.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "f8b7e637e25d219ce4ed205978d2a06515bf66ee",
    "started_at": "2026-08-22T03:32:06.539977Z",
    "updated_at": "2026-08-22T03:32:06.539977Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_DISCOVERY_AND_PERMISSION_FAST_PATH",
    "tier": "micro",
    "subject": "4cd4f00ceb5e258fd1e6fca4fdf76058dcbeb6cd",
    "summary": "Make repository discovery and known-permission command startup efficient.",
    "disposition": "completed",
    "decision_ref": "User request 2026-08-22: 关闭",
    "closed_at": "2026-08-22T03:16:12.609021Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
