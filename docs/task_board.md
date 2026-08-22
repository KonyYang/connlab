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
    "task_id": "TASK_REMOVE_LEGACY_MATRIX_STEP_QUANTITY_API",
    "summary": "Remove the unused legacy Matrix Step quantity HTTP and frontend API while preserving stored authority compatibility.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Remove the uncalled frontend client contract, backend route registration, route-only service and dead direct replacement seam; retain domain models, persisted snapshot compatibility, Fee Evaluation and Test Record consumers.",
    "scope_paths": [
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
      "backend/api/main.py",
      "backend/api/routes_matrix_step_quantities.py",
      "backend/application/matrix_step_quantity_service.py",
      "backend/infrastructure/storage/repositories/project_matrix_draft.py",
      "tests/integration/test_matrix_step_quantity_api.py",
      "tests/unit/test_matrix_step_quantity_service.py",
      "tests/unit/test_project_matrix_draft_repository.py"
    ],
    "risk_reasons": [],
    "activation_head": "682f63335d59945e33320ae6ee5cf25ad9a0ca5c",
    "started_at": "2026-08-22T02:41:20.149325Z",
    "updated_at": "2026-08-22T02:41:20.149325Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_REMOVE_MATRIX_STEP_QUANTITY_SETUP_UI",
    "tier": "standard",
    "subject": "6ee5d5dd96fc9694b46ef10eb647d921bd8d159b",
    "summary": "Remove the redundant Matrix Step quantity setup UI while preserving downstream and historical compatibility.",
    "disposition": "completed",
    "decision_ref": "User request 2026-08-22: close current task and execute legacy Step quantity API cleanup",
    "closed_at": "2026-08-22T02:40:45.165696Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
