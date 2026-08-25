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
    "updated_at": "2026-08-25T05:11:40.594471Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_SAMPLE_QUANTITY_FOOTNOTE_NORMALIZATION",
      "stage": "review-and-qa",
      "status": "running",
      "summary": "Standards and spec review found no remaining issue; preserved existing 5-sample workbook coverage, added a separate 3(a) API case, and 62 related parser/projection/API/release tests pass.",
      "requires_user": false
    },
    "report": null
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
