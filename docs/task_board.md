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
    "task_id": "TASK_MATRIX_XLSX_ROUND_TRIP",
    "summary": "Implement two-phase ConnLab Matrix XLSX import: strict visible-format fallback with Day default 0 and non-blocking warning, then hidden metadata with fingerprint-validated lossless round-trip.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Matrix XLSX import/export, preview UI, source pickers, draft propagation, metadata/fingerprint validation, and focused regression coverage.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/routes_matrix_editor_live_xlsx_export.py",
      "backend/api/routes_project_test_plan.py",
      "backend/application/matrix_editor_live_xlsx_export_service.py",
      "backend/application/matrix_editor_live_xlsx_publication_service.py",
      "backend/application/matrix_import_draft_builder.py",
      "backend/application/project_test_plan_matrix_preview_service.py",
      "backend/application/project_test_plan_source_candidate_service.py",
      "backend/desktop/path_picker_api.py",
      "backend/infrastructure/office/connlab_matrix_xlsx_gateway.py",
      "backend/infrastructure/office/matrix_editor_live_xlsx_workbook_gateway.py",
      "backend/modules/test_plan/connlab_matrix_xlsx_format.py",
      "backend/modules/test_plan/product_spec_matrix_parser.py",
      "docs/project_management/SOL_NATIVE_WORKFLOW.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.import.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixImportDialog.test.tsx",
      "frontend/src/features/matrix-editor/MatrixImportDialog.tsx",
      "frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.test.ts",
      "frontend/src/features/matrix-editor/matrixEditorXlsxExportProjection.ts",
      "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
      "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
      "frontend/src/features/matrix-editor/useMatrixImportWorkflow.ts",
      "frontend/src/workbench.css",
      "scripts/connlab_sol_task.py",
      "tests/integration/test_matrix_editor_live_xlsx_export_api.py",
      "tests/integration/test_project_test_plan_preview_api.py",
      "tests/unit/test_connlab_matrix_xlsx_gateway.py",
      "tests/unit/test_connlab_sol_native_workflow.py",
      "tests/unit/test_matrix_editor_live_xlsx_publication_service.py",
      "tests/unit/test_matrix_editor_live_xlsx_workbook_gateway.py",
      "tests/unit/test_matrix_import_commit_service.py",
      "tests/unit/test_matrix_source_candidate_service.py"
    ],
    "risk_reasons": [
      "Imports external Excel files into a draft that can later become authoritative through Confirm Matrix.",
      "Changes the supported Matrix round-trip contract and generated workbook structure.",
      "Requires coordinated backend, frontend, Office-format, and compatibility behavior."
    ],
    "activation_head": "71c519b22eb48baf3685ab70acbfac066d3f3090",
    "started_at": "2026-08-29T04:13:35.511871Z",
    "updated_at": "2026-08-29T05:27:45.533212Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_XLSX_ROUND_TRIP",
      "stage": "scope_manifest_correction",
      "status": "running",
      "summary": "User approved a controlled scope-manifest correction for the current task and authorized using it to complete task closeout.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-001D",
    "tier": "high_risk",
    "subject": "42f3887ca38327f54937dc101631c407e9a5b46d",
    "summary": "Carry confirmed application-form Test Sample Information through structured persistence and Basic Information authority into the E-3707_H SAMPLE DESCRIPTION table.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭.",
    "closed_at": "2026-08-29T04:06:23.444332Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
