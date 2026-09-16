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
    "updated_at": "2026-09-16T13:53:15.235800Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_FORM_AUTHORITY_AND_HEADER_REPAIR",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "task_id": "TASK_FEE_FORM_AUTHORITY_AND_HEADER_REPAIR",
      "summary": "Fee Form downloads now populate confirmed Basic Information headers and the page reliably distinguishes matching confirmed authority from unconfirmed current values.",
      "version": 1,
      "validation": [
        {
          "status": "passed",
          "name": "fee-form backend and workbook regression",
          "summary": "64 passed"
        },
        {
          "status": "passed",
          "name": "fee-evaluation frontend regression",
          "summary": "43 passed"
        },
        {
          "status": "passed",
          "name": "frontend production build",
          "summary": "TypeScript and Vite build passed"
        }
      ],
      "schema": "connlab.sol-task-report",
      "scope_ok": true,
      "roles": {
        "developer": {
          "summary": "Implemented with TDD and self-reviewed.",
          "status": "passed"
        },
        "qa": {
          "summary": "Affected backend/frontend regressions and production build passed; unrelated baseline failures recorded separately.",
          "status": "passed"
        },
        "reviewer": {
          "summary": "Focused diff review found no in-scope defects or scope drift.",
          "status": "passed"
        }
      },
      "changed_paths": [
        "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
        "backend/application/fee_form_publication_service.py",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts",
        "tests/integration/test_confirmed_matrix_fee_file_download_api.py",
        "tests/unit/test_fee_form_publication_service.py"
      ],
      "integration": {
        "mode": "direct_primary",
        "status": "passed"
      },
      "subject": "ae3f0b544efeb0fa6dac9f413096dfa8fa9cff92"
    }
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
