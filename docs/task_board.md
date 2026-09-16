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
    "task_id": "TASK_FEE_MATRIX_SINGLE_BUTTON_PREVIEW_CONFIRMATION",
    "summary": "Apply the Test Record single-button preview and official-save interaction to Fee Form and Export Matrix.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Keep one Fee Form button and one Export Matrix button. Require one clear confirmation before unconfirmed or no-folder browser downloads, preserve immediate official save for confirmed current authority with an available project folder and no conflict, preserve one safe conflict dialog for existing official files, and revalidate download authority and folder state at execution time.",
    "scope_paths": [
      "frontend/src/api/client.ts",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.ts",
      "frontend/src/features/matrix-editor/useMatrixEditorXlsxExport.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "backend/application/fee_form_publication_service.py",
      "backend/application/matrix_editor_live_xlsx_publication_service.py",
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "backend/api/routes_matrix_editor_live_xlsx_export.py",
      "tests/unit/test_fee_form_publication_service.py",
      "tests/unit/test_matrix_editor_live_xlsx_publication_service.py",
      "tests/integration/test_confirmed_matrix_fee_file_download_api.py",
      "tests/integration/test_matrix_editor_live_xlsx_export_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "9112a30b7a208fd4e1cce37bd014221f9e3281b1",
    "started_at": "2026-09-16T09:38:48.810138Z",
    "updated_at": "2026-09-16T09:38:48.810138Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_TEST_RECORD_SINGLE_BUTTON_HEADER",
    "tier": "standard",
    "subject": "a003fe68e1685e0fff1ddc286517a8ef1f9300f8",
    "summary": "Keep one Matrix Editor Test Record button, add one state-driven confirmation flow for draft preview versus official save, and make downloaded draft headers use the same reliable metadata mapping as official Test Records.",
    "disposition": "completed",
    "decision_ref": "User explicitly approved delivery and requested closure.",
    "closed_at": "2026-09-16T04:37:52.546836Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
