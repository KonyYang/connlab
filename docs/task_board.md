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
    "task_id": "TASK_MATRIX_SCHEDULE_CONFIRM_INDEPENDENCE",
    "summary": "Fix Matrix confirmation and deleted-row restoration; confirm Project Schedule independently and keep outputs usable.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Repair imported Matrix save/confirm/reopen and independent schedule authority with backward-compatible migration; validate output consumers and release behavior without altering operator data or bypassing Fee confirmation.",
    "scope_paths": [
      "backend/api/routes_project_schedule.py",
      "backend/application/confirmed_matrix_authority_service.py",
      "backend/application/matrix_editor_session_signature.py",
      "backend/application/matrix_revision_flow_service.py",
      "backend/application/project_schedule_output.py",
      "backend/application/project_schedule_service.py",
      "backend/domain/project_schedule_models.py",
      "backend/infrastructure/storage/models_project_schedule.py",
      "backend/infrastructure/storage/project_schedule_schema_migration.py",
      "backend/infrastructure/storage/repositories/project_schedule.py",
      "docs/PROJECT_CONTEXT.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.test.ts",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "frontend/src/features/matrix-editor/matrixSchedulePlanning.test.ts",
      "frontend/src/features/matrix-editor/matrixSchedulePlanning.ts",
      "tests/integration/test_confirmed_matrix_authority_api.py",
      "tests/integration/test_matrix_editor_session_api.py",
      "tests/integration/test_project_schedule_api.py",
      "tests/unit/test_confirmed_matrix_authority_service.py",
      "tests/unit/test_matrix_editor_session_service.py",
      "tests/unit/test_matrix_revision_flow_service.py",
      "tests/unit/test_project_schedule_repository.py",
      "tests/unit/test_project_schedule_schema_migration.py",
      "tests/unit/test_project_schedule_service.py"
    ],
    "risk_reasons": [
      "Backward-compatible nullable schedule lineage schema migration and authority boundary changes"
    ],
    "activation_head": "f3e5ddc81e8ecf7947bae58d152b595f1d277fd1",
    "started_at": "2026-09-09T15:39:07.292887Z",
    "updated_at": "2026-09-09T23:19:02.600121Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_SCHEDULE_CONFIRM_INDEPENDENCE",
      "stage": "excel_short_path_fix",
      "status": "running",
      "summary": "User approved expanding current task to Fee Excel short local staging, close-before-publish, regression protection and rebuilt release smoke. Original operator data remains untouched.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_BLOCKER_VISIBILITY",
    "tier": "standard",
    "subject": "0a5b7355291310c390fa022f523c6809cc583164",
    "summary": "Keep Project Folder generation blockers visible until the user corrects the input or explicitly starts a new recovery action.",
    "disposition": "completed",
    "decision_ref": "user-explicit-close-2026-09-09",
    "closed_at": "2026-09-09T15:17:18.761335Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
