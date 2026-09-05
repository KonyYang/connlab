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
    "task_id": "TASK_MATRIX_EXPERIENCE_RELIABILITY_BATCH1",
    "summary": "Improve Matrix loading, registry status consistency, and edit-save-reopen-confirm-export reliability.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "First Matrix optimization batch only; preserve business semantics and real data, validate using isolated fixtures.",
    "scope_paths": [
      "frontend/src/features/matrix-editor",
      "frontend/src/features/project-workbench",
      "frontend/src/features/projects-registry",
      "frontend/src/pages/ProjectListPage.tsx",
      "frontend/src/api",
      "backend/application",
      "backend/api",
      "tests"
    ],
    "risk_reasons": [],
    "activation_head": "d407f3ffbe8d7fdb4b5a3772b2c4ef19ce68c04c",
    "started_at": "2026-09-05T00:23:15.197219Z",
    "updated_at": "2026-09-05T01:51:27.088002Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_EXPERIENCE_RELIABILITY_BATCH1",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_EXPERIENCE_RELIABILITY_BATCH1",
      "subject": "7ddd40a14fa8ce82423c07ffa53d25dfa1a1cb57",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/matrix_editor_session_dtos.py",
        "backend/api/matrix_step_text_output_dtos.py",
        "backend/api/project_matrix_draft_dtos.py",
        "backend/api/project_matrix_draft_response_mappers.py",
        "backend/api/routes_confirmed_matrix_test_record_preview.py",
        "backend/api/routes_matrix_editor_llcr_cr_record_generation.py",
        "backend/api/routes_matrix_editor_session.py",
        "backend/api/routes_matrix_editor_test_record_generation.py",
        "backend/api/routes_project.py",
        "backend/api/routes_project_matrix_drafts.py",
        "backend/application/confirmed_matrix_authority_service.py",
        "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
        "backend/application/confirmed_matrix_runtime_projection_service.py",
        "backend/application/confirmed_matrix_test_record_preview_service.py",
        "backend/application/matrix_editor_confirmed_snapshot_builder.py",
        "backend/application/matrix_editor_llcr_cr_record_generation_service.py",
        "backend/application/matrix_editor_llcr_cr_record_projection.py",
        "backend/application/matrix_editor_session_contracts.py",
        "backend/application/matrix_editor_session_draft_state.py",
        "backend/application/matrix_editor_session_projection.py",
        "backend/application/matrix_editor_session_publication.py",
        "backend/application/matrix_editor_session_service.py",
        "backend/application/matrix_editor_session_signature.py",
        "backend/application/matrix_editor_test_record_authority.py",
        "backend/application/matrix_editor_test_record_document_generation_service.py",
        "backend/application/matrix_editor_test_record_publication_service.py",
        "backend/application/matrix_revision_snapshot_builder.py",
        "backend/application/matrix_step_text_output.py",
        "backend/application/matrix_step_text_overrides.py",
        "backend/application/project_matrix_draft_persistence_service.py",
        "backend/application/project_matrix_duration_authority_payload.py",
        "backend/application/project_registry_summary_service.py",
        "backend/domain/__init__.py",
        "backend/domain/confirmed_matrix_authority_models.py",
        "backend/domain/project_matrix_draft_models.py",
        "backend/infrastructure/office/llcr_cr_record_workbook_layout.py",
        "backend/infrastructure/office/test_record_document_gateway.py",
        "backend/infrastructure/office/test_report_document_gateway.py",
        "backend/infrastructure/storage/matrix_draft_lifecycle_migration.py",
        "backend/infrastructure/storage/models_confirmed_matrix_authority.py",
        "backend/infrastructure/storage/models_project_matrix_draft.py",
        "backend/infrastructure/storage/repositories/confirmed_matrix_authority.py",
        "backend/infrastructure/storage/repositories/project_matrix_draft.py",
        "backend/modules/runtime_projection/snapshot_adapter.py",
        "backend/modules/runtime_projection/token_projection_builder.py",
        "docs/PROJECT_CONTEXT.md",
        "docs/project_management/MATRIX_RELIABILITY_BATCH1.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixImportOptionalStandardFallback.test.tsx",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "frontend/src/features/matrix-editor/matrixStepWorkspaceModel.ts",
        "frontend/src/features/matrix-editor/useMatrixDraftPersistence.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixDraftPersistence.ts",
        "frontend/src/features/matrix-editor/useMatrixEditorContext.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixEditorContext.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchMatrixProjectionPanel.test.tsx",
        "frontend/src/features/project-workbench/RecordStepWorkspacePanel.test.tsx",
        "frontend/src/features/project-workbench/RecordStepWorkspacePanel.tsx",
        "frontend/src/features/project-workbench/projectWorkbenchMatrixProjectionSelectors.ts",
        "frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts",
        "frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts",
        "tests/integration/test_matrix_editor_session_api.py",
        "tests/integration/test_matrix_editor_test_record_generation_api.py",
        "tests/integration/test_project_registry_summary_api.py",
        "tests/unit/test_matrix_editor_llcr_cr_record_projection.py",
        "tests/unit/test_matrix_step_text_outputs.py",
        "tests/unit/test_test_record_document_gateway.py",
        "tests/unit/test_test_report_document_gateway.py"
      ],
      "summary": "Matrix loading, registry status and durable group/step-local draft text are implemented; only successful Confirm publishes formal text. Independent review, full non-Office QA and isolated browser verification passed. No real-data migration, release deployment or push.",
      "validation": [
        {
          "status": "passed",
          "suite": "Python non-Office full gate",
          "subject": "707e89712e2d9ea801be258bab4a54b4a61024ce",
          "passed": 2565,
          "skipped": 4,
          "deselected": 19,
          "seconds": 210.83
        },
        {
          "status": "passed",
          "suite": "Frontend full gate",
          "subject": "707e89712e2d9ea801be258bab4a54b4a61024ce",
          "files": 75,
          "tests": 482,
          "test_seconds": 14.75,
          "typecheck": "passed",
          "build": "passed",
          "command_seconds": 21.43
        },
        {
          "status": "passed",
          "suite": "Isolated browser",
          "subject": "707e89712e2d9ea801be258bab4a54b4a61024ce",
          "checks": "save/reload/Confirm/reopen, group and Test Item isolation, saved draft separate from active authority; owned resources stopped"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "context": "/root/step_persistence_plan",
          "note": "Independent persistence planning; this context later contributed bounded output implementation."
        },
        "developer": {
          "status": "passed",
          "contexts": [
            "/root",
            "/root/step_backend_developer",
            "/root/step_persistence_plan"
          ],
          "note": "Coherent RED/GREEN public-behavior regressions and affected checks; final correction covered by three API tests."
        },
        "reviewer": {
          "status": "passed",
          "context": "/root/matrix_reviewer",
          "subject": "707e89712e2d9ea801be258bab4a54b4a61024ce",
          "remaining_blocking_findings": 0
        },
        "qa": {
          "status": "passed",
          "context": "/root/matrix_qa",
          "subject": "707e89712e2d9ea801be258bab4a54b4a61024ce",
          "note": "Initial collection-only missing declared msoffcrypto dependency repaired in existing venv; full gate then passed without test edits. Office COM excluded."
        },
        "integrator": {
          "status": "passed",
          "context": "/root/matrix_integrator_final",
          "subject": "7ddd40a14fa8ce82423c07ffa53d25dfa1a1cb57"
        }
      },
      "integration": {
        "status": "passed",
        "subject": "7ddd40a14fa8ce82423c07ffa53d25dfa1a1cb57",
        "branch": "master",
        "tree": "6ac8edc4e02c46caff9551f9ee5eee4084a6472c",
        "parents": [
          "707e89712e2d9ea801be258bab4a54b4a61024ce"
        ],
        "clean": true,
        "fact": "Changes committed on local master; only final report differs from reviewed/QA subject. No merge, push or deployment required.",
        "evidence_path": "docs/project_management/MATRIX_RELIABILITY_BATCH1.md",
        "evidence_commit": "7ddd40a14fa8ce82423c07ffa53d25dfa1a1cb57",
        "evidence_raw_sha256": "789dac5d3c01f85eb8dd99dbf78317d12161b68c7d57397a43dc166b897832da"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_ASTRA_USAGE_GUIDE",
    "tier": "micro",
    "subject": "e92488c77c40bbb546dde3eaa3882ad514965b96",
    "summary": "Create a Chinese GPT-6 Astra usage guide and align active documentation.",
    "disposition": "completed",
    "decision_ref": "user:关闭使用指南任务，恢复目标并继续 Matrix 优化",
    "closed_at": "2026-09-05T00:23:15.197219Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
