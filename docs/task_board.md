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
    "task_id": "TASK_PROJECT_SCHEDULE_AUTHORITY",
    "summary": "Establish Project Schedule as an independent authority, remove duplicate schedule inputs from Basic Information, and source official document dates from the confirmed schedule.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Create a project-level confirmed Schedule lifecycle derived from confirmed Basic Information and Matrix duration authority; remove editable Sample received from the schedule card and duplicate Estimated Completion, Start Test Date, Finish Test Date, and Report Date inputs from Basic Information; keep Requested Completion in Basic Information; ensure schedule-only edits do not activate Confirm Matrix; update Application Form, Customer Feedback, and Test Report outputs to compose their dates from the correct confirmed authorities; preserve legacy projects through deterministic fallback/bootstrap behavior.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/dependencies_matrix_editor_live_xlsx_export.py",
      "backend/api/main.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/api/routes_project_schedule.py",
      "backend/api/routes_project_section2_sync.py",
      "backend/application/customer_feedback_form_generation_service.py",
      "backend/application/matrix_editor_live_xlsx_publication_service.py",
      "backend/application/project_application_form_write_back_service.py",
      "backend/application/project_schedule_output.py",
      "backend/application/project_schedule_service.py",
      "backend/application/project_section2_sync_service.py",
      "backend/application/test_report_draft_service.py",
      "backend/domain/project_schedule_models.py",
      "backend/infrastructure/storage/database.py",
      "backend/infrastructure/storage/models_project_schedule.py",
      "backend/infrastructure/storage/project_schedule_schema_migration.py",
      "backend/infrastructure/storage/repositories/project_schedule.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
      "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx",
      "frontend/src/features/project-basic-information/basicInformationFieldConfig.ts",
      "frontend/src/features/project-workbench/ProjectSection2SyncPanel.test.tsx",
      "frontend/src/features/project-workbench/ProjectSection2SyncPanel.tsx",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
      "tests/integration/test_customer_feedback_form_generation_api.py",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_project_schedule_api.py",
      "tests/integration/test_project_section2_sync_api.py",
      "tests/unit/test_customer_feedback_form_generation_service.py",
      "tests/unit/test_database.py",
      "tests/unit/test_matrix_editor_live_xlsx_publication_service.py",
      "tests/unit/test_project_application_form_write_back_service.py",
      "tests/unit/test_project_schedule_repository.py",
      "tests/unit/test_project_schedule_schema_migration.py",
      "tests/unit/test_project_schedule_service.py",
      "tests/unit/test_project_section2_sync_service.py",
      "tests/unit/test_test_report_draft_service.py"
    ],
    "risk_reasons": [
      "Adds a new SQLite authority schema and migrates date ownership between confirmed business authorities.",
      "Changes authoritative date inputs used by official Word and Excel outputs."
    ],
    "activation_head": "fd01d8af9fc6b5c963f144f021f74a517fbf7827",
    "started_at": "2026-09-08T15:09:32.891637Z",
    "updated_at": "2026-09-08T18:23:00.632709Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_SCHEDULE_AUTHORITY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_PROJECT_SCHEDULE_AUTHORITY",
      "subject": "e05cc7594605e6d2a38a50951978cf5d534830bc",
      "summary": "Project Schedule authority implementation is complete.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/dependencies_matrix_editor_live_xlsx_export.py",
        "backend/api/main.py",
        "backend/api/project_folder_generation_composition.py",
        "backend/api/routes_project_schedule.py",
        "backend/api/routes_project_section2_sync.py",
        "backend/application/customer_feedback_form_generation_service.py",
        "backend/application/matrix_editor_live_xlsx_publication_service.py",
        "backend/application/project_application_form_write_back_service.py",
        "backend/application/project_schedule_output.py",
        "backend/application/project_schedule_service.py",
        "backend/application/project_section2_sync_service.py",
        "backend/application/test_report_draft_service.py",
        "backend/domain/project_schedule_models.py",
        "backend/infrastructure/storage/database.py",
        "backend/infrastructure/storage/models_project_schedule.py",
        "backend/infrastructure/storage/project_schedule_schema_migration.py",
        "backend/infrastructure/storage/repositories/project_schedule.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx",
        "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.test.tsx",
        "frontend/src/features/project-basic-information/ProjectBasicInformationWorkspace.tsx",
        "frontend/src/features/project-basic-information/basicInformationFieldConfig.ts",
        "frontend/src/features/project-workbench/ProjectSection2SyncPanel.test.tsx",
        "frontend/src/features/project-workbench/ProjectSection2SyncPanel.tsx",
        "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
        "tests/integration/test_customer_feedback_form_generation_api.py",
        "tests/integration/test_project_folder_generation_complete_chain.py",
        "tests/integration/test_project_schedule_api.py",
        "tests/integration/test_project_section2_sync_api.py",
        "tests/unit/test_customer_feedback_form_generation_service.py",
        "tests/unit/test_database.py",
        "tests/unit/test_matrix_editor_live_xlsx_publication_service.py",
        "tests/unit/test_project_application_form_write_back_service.py",
        "tests/unit/test_project_schedule_repository.py",
        "tests/unit/test_project_schedule_schema_migration.py",
        "tests/unit/test_project_schedule_service.py",
        "tests/unit/test_project_section2_sync_service.py",
        "tests/unit/test_test_report_draft_service.py"
      ],
      "validation": [
        {
          "name": "backend",
          "status": "passed"
        },
        {
          "name": "frontend",
          "status": "passed"
        },
        {
          "name": "build",
          "status": "passed"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed"
        },
        "developer": {
          "status": "passed"
        },
        "reviewer": {
          "status": "passed"
        },
        "qa": {
          "status": "passed"
        },
        "integrator": {
          "status": "passed"
        }
      },
      "integration": {
        "status": "passed",
        "mode": "verified_local"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_BASIC_INFORMATION_PREFLIGHT",
    "tier": "standard",
    "subject": "dc5ab9c861640f6d363b91b179af7ea6869527e0",
    "summary": "Prevent Project Folder generation from starting before Basic Information is confirmed and provide precise actionable guidance for incomplete versus unconfirmed information.",
    "disposition": "completed",
    "decision_ref": "User: 关闭任务",
    "closed_at": "2026-09-08T14:04:11.537222Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
