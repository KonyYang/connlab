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
    "task_id": "TASK_MATRIX_TEST_POINTS_SINGLE_AUTHORITY",
    "summary": "Unify Test points draft/confirmation with Matrix authority and safely publish LLCR/CR forms to project Test results.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Matrix Editor inline Test points with project default and Group/Step exceptions; Confirm Matrix sole authority; legacy data preservation; Fee/LLCR/CR consumers; safe recoverable Create folder output and non-overwriting update; IR/DWV excluded.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/matrix_editor_session_dtos.py",
      "backend/api/matrix_editor_session_response_mappers.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/api/project_folder_preflight.py",
      "backend/api/routes_contact_point_profile.py",
      "backend/api/routes_matrix_editor_llcr_cr_record_generation.py",
      "backend/api/routes_matrix_editor_session.py",
      "backend/application/confirmed_matrix_authority_service.py",
      "backend/application/confirmed_matrix_fee_cr_specified_current.py",
      "backend/application/confirmed_matrix_fee_draft_line_builder.py",
      "backend/application/confirmed_matrix_fee_draft_service.py",
      "backend/application/confirmed_matrix_fee_step_quantities.py",
      "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
      "backend/application/confirmed_matrix_llcr_cr_record_preview_service.py",
      "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
      "backend/application/contact_point_profile_confirmed_consumer_adapter.py",
      "backend/application/matrix_editor_confirmed_snapshot_builder.py",
      "backend/application/matrix_editor_llcr_cr_record_generation_service.py",
      "backend/application/matrix_editor_llcr_cr_record_projection.py",
      "backend/application/matrix_editor_session_contracts.py",
      "backend/application/matrix_editor_session_draft_state.py",
      "backend/application/matrix_editor_session_projection.py",
      "backend/application/matrix_editor_session_service.py",
      "backend/application/matrix_editor_session_signature.py",
      "backend/application/matrix_test_points_authority.py",
      "backend/application/project_folder_generation_service.py",
      "backend/application/project_matrix_draft_persistence_service.py",
      "backend/domain/confirmed_matrix_authority_models.py",
      "backend/domain/enums.py",
      "backend/domain/matrix_contact_measurement_models.py",
      "backend/domain/project_matrix_draft_models.py",
      "backend/infrastructure/files/project_folder_required_forms_gateway.py",
      "backend/infrastructure/office/llcr_cr_record_workbook_layout.py",
      "backend/infrastructure/storage/matrix_contact_measurement_schema_migration.py",
      "backend/infrastructure/storage/models_confirmed_matrix_authority.py",
      "backend/infrastructure/storage/models_project_matrix_draft.py",
      "backend/infrastructure/storage/repositories/confirmed_matrix_authority.py",
      "backend/infrastructure/storage/repositories/project_matrix_draft.py",
      "docs/PROJECT_CONTEXT.md",
      "frontend/src/App.tsx",
      "frontend/src/api/client.ts",
      "frontend/src/contact-measurement-plan.css",
      "frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx",
      "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.test.tsx",
      "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.test.tsx",
      "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts",
      "frontend/src/features/matrix-editor/useMatrixDraftPersistence.ts",
      "tests/integration/test_contact_point_profile_api.py",
      "tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/unit/test_confirmed_matrix_authority_repository.py",
      "tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py",
      "tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py",
      "tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py",
      "tests/unit/test_matrix_contact_measurement_schema_migration.py",
      "tests/unit/test_matrix_editor_session_service.py",
      "tests/unit/test_project_folder_generation_service.py",
      "tests/unit/test_project_matrix_draft_repository.py"
    ],
    "risk_reasons": [
      "SQLite authority migration and legacy project data compatibility",
      "Authoritative LLCR/CR and fee consumer cutover",
      "Project Test results filesystem writes and recovery"
    ],
    "activation_head": "03b4b015b8842c86cc7299c8e9c330a0270c7678",
    "started_at": "2026-09-27T02:48:00.644593Z",
    "updated_at": "2026-09-27T11:29:19.668622Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_TEST_POINTS_SINGLE_AUTHORITY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "version": 1,
      "scope_ok": true,
      "task_id": "TASK_MATRIX_TEST_POINTS_SINGLE_AUTHORITY",
      "roles": {
        "developer": {
          "evidence": "TDD backend and frontend implementation; targeted and final checks passed.",
          "status": "passed"
        },
        "planner": {
          "evidence": "Independent file-flow and risk-boundary plan completed.",
          "status": "passed"
        },
        "integrator": {
          "evidence": "Independent exact scope and approval audit passed; 66 committed task/board paths.",
          "status": "passed"
        },
        "qa": {
          "evidence": "Independent final full gate exit 0 on final source bytes.",
          "status": "passed"
        },
        "reviewer": {
          "evidence": "Independent review findings P1 CR naming and P2 draft preview addressed and re-reviewed.",
          "status": "passed"
        }
      },
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/matrix_editor_session_dtos.py",
        "backend/api/matrix_editor_session_response_mappers.py",
        "backend/api/project_folder_generation_composition.py",
        "backend/api/project_folder_preflight.py",
        "backend/api/routes_contact_point_profile.py",
        "backend/api/routes_matrix_editor_llcr_cr_record_generation.py",
        "backend/api/routes_matrix_editor_session.py",
        "backend/application/confirmed_matrix_authority_service.py",
        "backend/application/confirmed_matrix_fee_cr_specified_current.py",
        "backend/application/confirmed_matrix_fee_draft_line_builder.py",
        "backend/application/confirmed_matrix_fee_draft_service.py",
        "backend/application/confirmed_matrix_fee_step_quantities.py",
        "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
        "backend/application/confirmed_matrix_llcr_cr_record_preview_service.py",
        "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
        "backend/application/contact_point_profile_confirmed_consumer_adapter.py",
        "backend/application/matrix_editor_confirmed_snapshot_builder.py",
        "backend/application/matrix_editor_llcr_cr_record_generation_service.py",
        "backend/application/matrix_editor_llcr_cr_record_projection.py",
        "backend/application/matrix_editor_session_contracts.py",
        "backend/application/matrix_editor_session_draft_state.py",
        "backend/application/matrix_editor_session_projection.py",
        "backend/application/matrix_editor_session_service.py",
        "backend/application/matrix_editor_session_signature.py",
        "backend/application/matrix_test_points_authority.py",
        "backend/application/project_folder_generation_service.py",
        "backend/application/project_matrix_draft_persistence_service.py",
        "backend/domain/confirmed_matrix_authority_models.py",
        "backend/domain/enums.py",
        "backend/domain/matrix_contact_measurement_models.py",
        "backend/domain/project_matrix_draft_models.py",
        "backend/infrastructure/files/project_folder_required_forms_gateway.py",
        "backend/infrastructure/office/llcr_cr_record_workbook_layout.py",
        "backend/infrastructure/storage/matrix_contact_measurement_schema_migration.py",
        "backend/infrastructure/storage/models_confirmed_matrix_authority.py",
        "backend/infrastructure/storage/models_project_matrix_draft.py",
        "backend/infrastructure/storage/repositories/confirmed_matrix_authority.py",
        "backend/infrastructure/storage/repositories/project_matrix_draft.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/App.tsx",
        "frontend/src/api/client.ts",
        "frontend/src/contact-measurement-plan.css",
        "frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.test.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.test.tsx",
        "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts",
        "frontend/src/features/matrix-editor/useMatrixDraftPersistence.ts",
        "tests/integration/test_contact_point_profile_api.py",
        "tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py",
        "tests/integration/test_project_folder_generation_complete_chain.py",
        "tests/integration/test_project_folder_generation_recovery.py",
        "tests/unit/test_confirmed_matrix_authority_repository.py",
        "tests/unit/test_confirmed_matrix_fee_draft_profile_consumer.py",
        "tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py",
        "tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py",
        "tests/unit/test_matrix_contact_measurement_schema_migration.py",
        "tests/unit/test_matrix_editor_session_service.py",
        "tests/unit/test_project_folder_generation_service.py",
        "tests/unit/test_project_matrix_draft_repository.py"
      ],
      "schema": "connlab.sol-task-report",
      "summary": "Matrix Editor Test points now share Confirm Matrix authority; LLCR/CR draft previews and protected official forms, Create-folder generation, legacy preservation, and CR fee manual review are implemented.",
      "subject": "effed0fca1458f17563c573c2c56c3260370e8fe",
      "integration": {
        "evidence": "Clean master, exact 65 non-board product paths, approved 9 scope additions, no external project data changed or publication.",
        "status": "passed"
      },
      "validation": [
        {
          "result": "Python 3105 passed, 8 skipped, 19 Office deselected; Vitest 696 passed, 1 skipped; tsc and Vite build passed.",
          "command": "run_tests.ps1 -Suite All",
          "status": "passed"
        },
        {
          "result": "Task commit whitespace check passed.",
          "command": "git diff --cached --check",
          "status": "passed"
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_SECTION_COLUMN_WIDTH",
    "tier": "micro",
    "subject": "e95575dc90a23c557500ad6810a5a2cacd8e1981",
    "summary": "Widen the Matrix Editor Section column so its header stays on one line.",
    "disposition": "completed",
    "decision_ref": "User final response: 关闭 (2026-09-27)",
    "closed_at": "2026-09-27T02:23:55.680167Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_361A_FEE_SUMMARY_ACCEPTANCE_CONTRACT",
      "tier": "standard",
      "closed_at": "2026-09-18T03:01:50.000000Z"
    },
    {
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS_COMPLETE",
      "tier": "high_risk",
      "closed_at": "2026-09-17T11:59:24.022479Z"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.

## Pending engineering-debt tasks ( backlog / not active )

These items are not in-flight; they are recorded here for prioritization. They do not
change the `active` field above.

### TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT

**Tier:** micro
**Revised from:** the stale broad test-environment proposal discovered during TASK_361A
**Goal:** Keep the supported test entry point on the same Python runtime as ConnLab development.

The original diagnosis was rechecked before implementation:

- `C:/PythonEnvs/connlab/.venv` is Python 3.11.9 and imports Tkinter 8.6 successfully; no
  dependency installation is needed.
- Office-dependent integration tests already use the `office_integration` marker. The normal gate
  excludes them and `-Suite Office` remains the explicit installed-Office check.
- WorkBuddy or Codex temporary-directory and safe-delete restrictions are host permissions, not
  ConnLab product behavior. They must be handled by the runner environment or an explicitly
  permitted pytest temp location, not by weakening repository cleanup or test semantics.

The remaining defect was limited to `scripts/run_tests.ps1`: it invoked the ambient `py` launcher,
which selected Python 3.13.3 instead of the Python 3.11.9 environment used by ConnLab. The revised
runner defaults to `C:/PythonEnvs/connlab/.venv/Scripts/python.exe`, supports an explicit
`-PythonExe` override, fails clearly when that interpreter is missing, and preserves the existing
normal/Office split.

**Validation:** the focused runner contract passes, and the complete non-Office Python gate passes
with 2954 tests, 7 skips, and 19 Office tests deselected on Python 3.11.9. No product code,
dependencies, Office implementation, or host safety policy changed.
