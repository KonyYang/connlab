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
    "task_id": "TASK_FEE_FORM_AUTHORITY_AND_HEADER_REPAIR",
    "summary": "Fix Fee Form header population and make current confirmed authority status reliable and visible.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Repair draft and official Fee Form generation so Basic Information fills controlled header fields, eliminate false draft classification caused by page hydration drift, and show a simple current/unconfirmed Fee status without exposing revision history.",
    "scope_paths": [
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "backend/application/fee_form_publication_service.py",
      "backend/infrastructure/office/fee_evaluation_workbook_gateway.py",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts",
      "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts",
      "tests/integration/test_confirmed_matrix_fee_file_download_api.py",
      "tests/unit/test_fee_form_publication_service.py",
      "tests/unit/test_fee_evaluation_workbook_gateway.py",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts"
    ],
    "risk_reasons": [],
    "activation_head": "238be05f22a03d2a8a3b7cdf1c74a9ba00636be9",
    "started_at": "2026-09-16T13:09:43.575748Z",
    "updated_at": "2026-09-16T13:50:45.531916Z",
    "checkpoint": {
      "stage": "qa-complete",
      "status": "running",
      "schema": "connlab.sol-task-checkpoint",
      "summary": "Fee Form draft downloads now receive confirmed Basic Information headers; current confirmed authority status is derived from matching saved values. Targeted backend/frontend tests and production build pass; unrelated baseline failures are documented.",
      "version": 1,
      "task_id": "TASK_FEE_FORM_AUTHORITY_AND_HEADER_REPAIR",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_MATRIX_SINGLE_BUTTON_PREVIEW_CONFIRMATION",
    "tier": "standard",
    "subject": "4c3fd2a23e274b656b47db9b3c4477a3c841395f",
    "summary": "Apply the Test Record single-button preview and official-save interaction to Fee Form and Export Matrix.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closure after accepting the completed Fee Form and Export Matrix single-button flow.",
    "closed_at": "2026-09-16T11:52:49.288859Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
