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
    "task_id": "TASK_MATRIX_SAMPLE_QUANTITY_FOOTNOTE_NORMALIZATION",
    "summary": "Recognize footnoted whole-number Matrix sample quantities such as 3(a) throughout import and confirmation.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Reproduce and fix sample quantity normalization at the existing Matrix import/confirmation authority seam, preserve legitimate expressions and rebuild the ConnLab_Web release.",
    "scope_paths": [
      "backend/modules/test_plan",
      "backend/application",
      "backend/domain",
      "backend/api",
      "frontend/src/features/matrix-editor",
      "tests/unit",
      "tests/integration",
      "scripts/build_windows_browser_release.ps1",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "93c3ee11b91f36948e02331b4c71f73a687387df",
    "started_at": "2026-08-25T05:02:00.971348Z",
    "updated_at": "2026-08-25T05:12:46.292484Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_SAMPLE_QUANTITY_FOOTNOTE_NORMALIZATION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_SAMPLE_QUANTITY_FOOTNOTE_NORMALIZATION",
      "subject": "11326fc4f9b5537cd6f2beab8aa2c19058d91c41",
      "summary": "Recognize a positive whole-number Matrix sample count with alphabetic footnote markers across current, confirmed, and legacy record projections while preserving composite allocation review.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
        "backend/application/draft_measurement_plan_workbook_projection.py",
        "backend/application/matrix_record_sample_quantity.py",
        "scripts/build_windows_browser_release.ps1",
        "tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py",
        "tests/unit/test_confirmed_matrix_llcr_cr_record_projection.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tests/unit/test_draft_measurement_plan_workbook_projection.py",
        "tests/unit/test_matrix_editor_llcr_cr_record_projection.py",
        "tests/unit/test_matrix_record_sample_quantity.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "red-green",
          "summary": "Exact 3(a) Matrix Editor projection failed before and passed after the shared parser fix"
        },
        {
          "status": "passed",
          "name": "related-suite",
          "summary": "62 parser, projection, API, workbook, and release tests passed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed"
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards and spec review passed; preserved composite ambiguity and prior 5-sample coverage"
        },
        "qa": {
          "status": "passed",
          "summary": "Current Matrix Editor, confirmed authority, legacy draft, and network API paths passed"
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Matrix Editor API generated the LLCR workbook with 3 samples from 3(a)"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_SUPPORT_DIAGNOSTIC_BUNDLE",
    "tier": "standard",
    "subject": "e5e44a946628550fc3a5df411adc1288705841b7",
    "summary": "Add persistent packaged-runtime diagnostics and a safe operator-exportable support bundle.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-25T04:39:04.138013Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
