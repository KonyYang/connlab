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
    "task_id": "TASK_AUTHORITY_AWARE_MATRIX_XLSX_OUTPUT",
    "summary": "Route Export Matrix to the existing draft download until the current page matches confirmed Matrix authority, then safely publish the formal workbook into Source Book.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Matrix Editor XLSX draft/formal output only, including confirmed-authority matching, Source Book publication, same-name conflict handling, lifecycle protection, and focused UI/API tests.",
    "scope_paths": [
      "backend/application/matrix_editor_live_xlsx_export_service.py",
      "backend/application/matrix_editor_live_xlsx_publication_service.py",
      "backend/application/project_lifecycle_write_guard.py",
      "backend/api/routes_matrix_editor_live_xlsx_export.py",
      "backend/api/dependencies_matrix_editor_live_xlsx_export.py",
      "backend/infrastructure/files/test_record_publication_gateway.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.ts",
      "frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/workbench.css",
      "tests/unit/test_matrix_editor_live_xlsx_export_service.py",
      "tests/unit/test_matrix_editor_live_xlsx_publication_service.py",
      "tests/integration/test_matrix_editor_live_xlsx_export_api.py"
    ],
    "risk_reasons": [
      "Writes a formal Matrix workbook into the authoritative project Source Book folder.",
      "May archive or move an existing formal Matrix workbook to the Windows Recycle Bin after explicit user choice."
    ],
    "activation_head": "85a7beb1b3be78ba5342b3adc344fe05b34fee71",
    "started_at": "2026-08-28T22:42:18.682496Z",
    "updated_at": "2026-08-28T22:42:18.682496Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_TEST_REPORT_TEMPLATE_HEADING_COMPATIBILITY",
    "tier": "standard",
    "subject": "0d9b07160b63db113484d43c2b1b732e0a91de1c",
    "summary": "Diagnose and fix Test Report generation when the configured approved E-3707_H template heading is not recognized.",
    "disposition": "completed",
    "decision_ref": "用户明确回复：关闭",
    "closed_at": "2026-08-28T22:29:39.242372Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
