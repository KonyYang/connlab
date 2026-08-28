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
    "task_id": "TASK_AUTHORITY_AWARE_FEE_AND_TEST_RECORD_OUTPUT",
    "summary": "Route Fee Form and Test Record generation to draft downloads until the current page matches confirmed authority, then safely publish official files into an existing project folder.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Fee Evaluation Fee Form and Matrix Editor Test Record authority-aware draft/formal output only, including formal-file conflict handling and Confirm Matrix no-change enablement.",
    "scope_paths": [
      "backend/application/fee_form_publication_service.py",
      "backend/application/matrix_editor_test_record_authority.py",
      "backend/application/matrix_editor_test_record_publication_service.py",
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "backend/api/routes_matrix_editor_test_record_generation.py",
      "backend/api/dependencies.py",
      "backend/infrastructure/files/project_output_publication_gateway.py",
      "backend/infrastructure/files/test_record_publication_gateway.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/workbench.css",
      "tests/unit/test_fee_form_publication_service.py",
      "tests/unit/test_matrix_editor_test_record_authority.py",
      "tests/unit/test_matrix_editor_test_record_publication_service.py",
      "tests/integration/test_confirmed_matrix_fee_file_download_api.py",
      "tests/integration/test_matrix_editor_test_record_generation_api.py"
    ],
    "risk_reasons": [
      "Writes confirmed Fee Form and Test Record files into the authoritative official project folder.",
      "May archive or move an existing official workbook or document to the Windows Recycle Bin after explicit user choice."
    ],
    "activation_head": "efbf5545a26ad39f4beaa6b35cae11c781815e19",
    "started_at": "2026-08-28T05:10:31.438844Z",
    "updated_at": "2026-08-28T05:10:31.438844Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_REPORT_001_DRAFT_FIDELITY_REVISION",
    "tier": "standard",
    "subject": "b60b7dd50984a4cd992a09bd81fc986c3d75b3b6",
    "summary": "Revise the E-3707_H initialization report draft to match approved-report table typography, fills, result defaults, LLCR descriptions, and heading pagination.",
    "disposition": "completed",
    "decision_ref": "用户明确回复：关闭",
    "closed_at": "2026-08-28T05:01:05.765366Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
