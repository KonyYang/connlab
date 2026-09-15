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
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_MATRIX_GROUP_IDENTITY_A",
    "summary": "Prevent duplicate Matrix group identities across add, insert, duplicate, save, confirm, reload, and export while preserving existing group data for explicit diagnosis.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Introduce one stable manual-group identity allocator, preserve duplicate legacy groups during hydration, reject duplicate group keys at frontend export and backend draft/confirmation seams, and add focused regression coverage. No external files, database migration, or historical authority rewrite.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.test.ts",
      "frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.ts",
      "frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.test.ts",
      "backend/application/project_matrix_duration_authority_payload.py",
      "backend/application/confirmed_matrix_authority_service.py",
      "backend/application/matrix_revision_flow_service.py",
      "tests/unit/test_project_matrix_draft_persistence_service.py",
      "tests/unit/test_confirmed_matrix_authority_service.py",
      "tests/unit/test_matrix_revision_flow_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "b7fc6c117028dff08986eec737ffbc3fd36650b0",
    "started_at": "2026-09-15T16:10:10.681108Z",
    "updated_at": "2026-09-15T16:48:12.858678Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_GROUP_IDENTITY_A",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_GROUP_IDENTITY_A",
      "subject": "6826d851a399ebbbf201bfe9084345c5c81aad83",
      "summary": "Matrix manual add, insert, and duplicate actions now allocate stable unique identities; legacy duplicate-key drafts retain every group for diagnosis and are blocked from autosave, confirmation, and export at frontend and backend boundaries.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/confirmed_matrix_authority_service.py",
        "backend/application/matrix_editor_session_service.py",
        "backend/application/matrix_group_identity.py",
        "backend/application/matrix_revision_flow_service.py",
        "backend/application/project_matrix_duration_authority_payload.py",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.test.ts",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.test.ts",
        "frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.ts",
        "frontend/src/features/matrix-editor/matrixGroupIdentity.test.ts",
        "frontend/src/features/matrix-editor/matrixGroupIdentity.ts",
        "frontend/src/features/matrix-editor/useMatrixDraftPersistence.ts",
        "tests/unit/test_confirmed_matrix_authority_service.py",
        "tests/unit/test_matrix_editor_session_service.py",
        "tests/unit/test_matrix_revision_flow_service.py",
        "tests/unit/test_project_matrix_draft_persistence_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "affected-backend",
          "summary": "64 affected Python unit tests passed."
        },
        {
          "status": "passed",
          "name": "affected-frontend",
          "summary": "48 affected Matrix Editor frontend tests passed."
        },
        {
          "status": "passed",
          "name": "frontend-complete",
          "summary": "582 frontend tests passed, one was skipped, and the production Vite build passed."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented the invariant and regression coverage with recorded red-green slices."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards and specification review found no remaining in-scope defect."
        },
        "qa": {
          "status": "passed",
          "summary": "Affected suites and complete frontend QA passed; complete non-Office Python QA had 2885 passes and one unrelated pre-existing packaging-notes expectation failure."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Reviewed task diff is committed on the primary branch with a clean worktree."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_PREFLIGHT_PRIMARY_BLOCKER",
    "tier": "standard",
    "subject": "f76df48b41af224a97eb774e6237060c175db2e2",
    "summary": "Show the real Project Folder configuration blocker instead of cascading required-form identity errors.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭 in the current turn.",
    "closed_at": "2026-09-15T15:30:58.288866Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
