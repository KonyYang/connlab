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
    "task_id": "TASK_LLCR_CR_MATRIX_RECORDS",
    "summary": "Generate separate LLCR and CR test-record workbooks from confirmed Matrix and confirmed Project Point Profile, with a persisted LLCR Delta R option.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Point Profile Delta R authority, Matrix-driven LLCR/CR projections, separate xlsx generation/download, Matrix Editor panel, and proportional regression coverage.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/routes_contact_point_profile.py",
      "backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py",
      "backend/application/contact_point_profile_confirmed_consumer_adapter.py",
      "backend/application/contact_point_profile_fingerprint.py",
      "backend/application/contact_point_profile_lifecycle_service.py",
      "backend/application/contact_point_profile_read_service.py",
      "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
      "backend/application/confirmed_matrix_llcr_cr_record_preview_service.py",
      "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
      "backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py",
      "backend/infrastructure/office/llcr_cr_record_workbook_layout.py",
      "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
      "backend/infrastructure/storage/contact_point_profile_schema_migration.py",
      "backend/infrastructure/storage/models_contact_point_profile.py",
      "frontend/src/api/client.ts",
      "frontend/src/contact-measurement-plan.css",
      "frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx",
      "frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx",
      "frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx",
      "frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx",
      "frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.ts",
      "frontend/src/features/contact-measurement-plan/projectPointProfileSelectors.test.ts",
      "frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts",
      "frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx",
      "frontend/src/features/matrix-editor/LlcrCrRecordWorkbookPanel.tsx",
      "frontend/src/features/matrix-editor/LlcrCrRecordWorkbookPanel.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts",
      "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.test.tsx",
      "tests/integration/test_contact_point_profile_api.py",
      "tests/integration/test_llcr_cr_specialized_record_workbook_api.py",
      "tests/unit/test_contact_point_profile_confirmed_consumer_adapter.py",
      "tests/unit/test_contact_point_profile_fingerprint.py",
      "tests/unit/test_contact_point_profile_lifecycle.py",
      "tests/unit/test_contact_point_profile_schema.py",
      "tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py",
      "tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py",
      "tests/unit/test_llcr_cr_specialized_record_workbook_gateway.py"
    ],
    "risk_reasons": [
      "Additive SQLite schema migration for versioned Delta R authority",
      "Derived workbook behavior changes across backend, Office adapter, and Matrix Editor"
    ],
    "activation_head": "9c4739074d8fa803fdcf5c1169c7be4a1968cbb3",
    "started_at": "2026-08-23T05:51:56.868533Z",
    "updated_at": "2026-08-23T06:34:30.524067Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_LLCR_CR_MATRIX_RECORDS",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_LLCR_CR_MATRIX_RECORDS",
      "subject": "2b1654da61fe603600663878ff13008121e6af42",
      "summary": "Separate Matrix-driven LLCR and CR workbook generation with confirmed Point Profile categories and an LLCR-only Delta R option is complete.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/routes_confirmed_matrix_llcr_cr_record_workbook.py",
        "backend/api/routes_contact_point_profile.py",
        "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
        "backend/application/confirmed_matrix_llcr_cr_record_preview_service.py",
        "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
        "backend/application/contact_point_profile_confirmed_consumer_adapter.py",
        "backend/application/contact_point_profile_fingerprint.py",
        "backend/application/contact_point_profile_lifecycle_service.py",
        "backend/application/contact_point_profile_read_service.py",
        "backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py",
        "backend/infrastructure/office/llcr_cr_record_workbook_layout.py",
        "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
        "backend/infrastructure/storage/contact_point_profile_schema_migration.py",
        "backend/infrastructure/storage/models_contact_point_profile.py",
        "frontend/src/api/client.ts",
        "frontend/src/contact-measurement-plan.css",
        "frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx",
        "frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx",
        "frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.test.tsx",
        "frontend/src/features/contact-measurement-plan/ProjectPointProfileEditor.tsx",
        "frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.test.tsx",
        "frontend/src/features/contact-measurement-plan/useProjectPointProfileModel.ts",
        "frontend/src/features/matrix-editor/LlcrCrRecordWorkbookPanel.test.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordWorkbookPanel.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.test.tsx",
        "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts",
        "tests/integration/test_contact_point_profile_api.py",
        "tests/integration/test_llcr_cr_specialized_record_workbook_api.py",
        "tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py",
        "tests/unit/test_contact_point_profile_lifecycle.py",
        "tests/unit/test_contact_point_profile_schema.py",
        "tests/unit/test_llcr_cr_specialized_record_workbook_gateway.py"
      ],
      "validation": [
        {
          "name": "affected backend pytest",
          "status": "passed",
          "summary": "54 passed"
        },
        {
          "name": "frontend Vitest",
          "status": "passed",
          "summary": "418 passed"
        },
        {
          "name": "frontend production build",
          "status": "passed",
          "summary": "141 modules transformed"
        },
        {
          "name": "in-app browser workflow",
          "status": "passed",
          "summary": "LLCR and CR previewed and generated independently; Delta R setup verified"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "summary": "Confirmed authorities, separate artifact boundaries, migration, and acceptance criteria remained in scope."
        },
        "developer": {
          "status": "passed",
          "summary": "Implemented schema, projection, workbook, API, UI, and regression coverage."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards and specification reviews passed after compatibility and workbook usability fixes."
        },
        "qa": {
          "status": "passed",
          "summary": "Affected backend, complete frontend, build, workbook, and browser validations passed."
        },
        "integrator": {
          "status": "passed",
          "summary": "Exact committed diff, scope allowlist, clean HEAD, and local integration verified."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "verified_local"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_SAMPLE_PREPARATION_MATRIX_QUANTITY",
    "tier": "standard",
    "subject": "ab58a3f695d1c44b40b087bb5165c6f6db30998b",
    "summary": "Use confirmed Matrix Samples Quantity (PCS) as Sample preparation Units instead of stale saved default 1.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-23T05:00:59.191192Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
