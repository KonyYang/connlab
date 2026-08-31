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
    "task_id": "REPORT-004A",
    "summary": "Simplify report History naming, correct Test Record replacement to archive the actual Submitted Material authority, and keep Fee Evaluation open after authority confirmation with a save-draft return action.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Change only report archive placement/naming, Matrix Editor Test Record target alignment, Fee Evaluation completion navigation, their focused tests, and report architecture documentation. Do not mutate real project files.",
    "scope_paths": [
      "backend/application/matrix_editor_test_record_publication_service.py",
      "backend/infrastructure/files/report_publication_gateway.py",
      "docs/report_generation_architecture.md",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "tests/integration/test_matrix_editor_test_record_generation_api.py",
      "tests/unit/test_current_report_update_service.py",
      "tests/unit/test_matrix_editor_test_record_publication_service.py",
      "tests/unit/test_report_publication_gateway.py"
    ],
    "risk_reasons": [
      "Changes the archival layout for authoritative internal and customer Word reports.",
      "Changes which existing Test Record file is archived and replaced in an official project folder."
    ],
    "activation_head": "585d6302d8aba5849e589656dee009a5e44bbabc",
    "started_at": "2026-08-31T23:31:26.185774Z",
    "updated_at": "2026-08-31T23:52:03.621197Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "REPORT-004A",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "REPORT-004A",
      "subject": "362ad76af700ace1fd0ccac1c577a83efe8b51a1",
      "summary": "Report history now uses compact flat filenames with collision protection; Matrix Editor replaces the canonical Submitted Material Test Record; Fee authority confirmation stays on page and a separate save-draft return action is available.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/matrix_editor_test_record_publication_service.py",
        "backend/infrastructure/files/report_publication_gateway.py",
        "docs/report_generation_architecture.md",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "tests/integration/test_matrix_editor_test_record_generation_api.py",
        "tests/unit/test_current_report_update_service.py",
        "tests/unit/test_matrix_editor_test_record_publication_service.py",
        "tests/unit/test_report_publication_gateway.py"
      ],
      "validation": [
        {
          "name": "focused backend and integration regressions",
          "status": "passed",
          "detail": "56 passed"
        },
        {
          "name": "frontend full regression suite",
          "status": "passed",
          "detail": "467 passed"
        },
        {
          "name": "frontend production build",
          "status": "passed",
          "detail": "tsc and vite build passed"
        },
        {
          "name": "backend compile check",
          "status": "passed",
          "detail": "changed modules compiled"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "authority boundaries and rollback behavior defined"
        },
        "developer": {
          "status": "passed",
          "detail": "TDD implementation complete"
        },
        "reviewer": {
          "status": "passed",
          "detail": "standards and specification review found no actionable findings"
        },
        "qa": {
          "status": "passed",
          "detail": "focused backend, full frontend, and build validations passed"
        },
        "integrator": {
          "status": "passed",
          "detail": "clean exact diff matches corrected approved scope"
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Current clean HEAD contains the reviewed implementation and exact scoped paths."
      }
    }
  },
  "last_closed": {
    "task_id": "REPORT-003E",
    "tier": "high_risk",
    "subject": "b9e2d41f7fb7f0b673b2ad81cc8b674bee14f7ff",
    "summary": "Recover safely when a customer report is deleted or moved after page preview by refreshing state and requiring explicit confirmation before generating a new report.",
    "disposition": "completed",
    "decision_ref": "User explicitly replied 关闭 on 2026-09-01.",
    "closed_at": "2026-08-31T22:53:43.533501Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
