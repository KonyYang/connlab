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
    "task_id": "TASK_FEE_FORM_DRAFT_PREVIEW_AUTHORITY_SEPARATION",
    "summary": "Make Fee Form an always-available draft preview while preserving Project Workbench as the only official output authority.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Separate Fee Evaluation draft preview generation and download from official Fee Form output registration and project-folder generation; preserve Workbench authority and add focused frontend, API, application, and regression validation.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/api/client.ts",
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "backend/application/confirmed_matrix_fee_evaluation_export_service.py",
      "tests/integration/test_confirmed_matrix_fee_file_download_api.py",
      "tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py",
      "tests/unit/test_project_folder_required_forms_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "efe6a8a2d2895ad194df805c99011501f4ec22ba",
    "started_at": "2026-08-22T05:54:02.225018Z",
    "updated_at": "2026-08-22T06:08:39.854597Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_FORM_DRAFT_PREVIEW_AUTHORITY_SEPARATION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_FEE_FORM_DRAFT_PREVIEW_AUTHORITY_SEPARATION",
      "subject": "5e07ab92900826fdc1f83ec85f68fff75b1a2a82",
      "summary": "Fee Form now downloads an always-available current-page draft preview without pricing-draft authority binding or ProjectOutput registration; Project Workbench official generation and registration remain unchanged.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
        "backend/application/confirmed_matrix_fee_evaluation_export_service.py",
        "backend/application/confirmed_matrix_fee_evaluation_export_timeout_service.py",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
        "tests/integration/test_confirmed_matrix_fee_file_download_api.py",
        "tests/unit/test_confirmed_matrix_fee_evaluation_export_service.py",
        "tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py"
      ],
      "validation": [
        {
          "name": "backend authority boundary suite",
          "status": "passed",
          "detail": "84 passed"
        },
        {
          "name": "frontend Fee Evaluation suite",
          "status": "passed",
          "detail": "33 passed"
        },
        {
          "name": "frontend production build",
          "status": "passed",
          "detail": "tsc and vite build passed"
        },
        {
          "name": "browser acceptance",
          "status": "passed",
          "detail": "Pending pricing with disabled Update Fee retained enabled Fee Form, authority notice visible, draft download success shown"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented with TDD and exact-scope commits."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards and specification review found no actionable findings."
        },
        "qa": {
          "status": "passed",
          "summary": "Backend, frontend, build, and browser acceptance passed."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Committed on master at 5e07ab92; Workbench official output regression remains green."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_EVALUATION_DETERMINISTIC_DEFAULT_FILL_EXTENSION",
    "tier": "standard",
    "subject": "6e15e88c970e09aaca34c1d28084168a02b0a3fd",
    "summary": "Extend deterministic Fee Evaluation defaults for MFG and specified-current CR labels, and safely repair confirmed-duration consumption where current authority already exists.",
    "disposition": "completed",
    "decision_ref": "User request 2026-08-22: 关闭",
    "closed_at": "2026-08-22T05:46:11.751625Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
