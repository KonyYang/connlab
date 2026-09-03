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
    "task_id": "TASK_MATRIX_DRAFT_DUPLICATE_ROW_IDENTITY",
    "summary": "Prevent Matrix Editor session restoration from duplicating repeated test rows and step sequences.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Reproduce and fix Matrix Editor draft/source row reconciliation when multiple rows share the same test item and section identity.",
    "scope_paths": [
      "docs/task_board.md",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.test.ts"
    ],
    "risk_reasons": [],
    "activation_head": "e1d24db2ffc0e12f4130036016d048052d1f9286",
    "started_at": "2026-09-03T15:57:58.369750Z",
    "updated_at": "2026-09-03T23:26:23.212891Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_DRAFT_DUPLICATE_ROW_IDENTITY",
      "stage": "revision",
      "status": "running",
      "summary": "user: latest imported PDF does not contain the duplicated Section 6.2 IR rows; investigate stale source/draft carry-over",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-003B-R2",
    "tier": "standard",
    "subject": "bd0f9b689acdca3c3646e611fb0338873123eefa",
    "summary": "Align controlled internal-report typography and Equipment List output with the approved business format while preserving calibration waivers.",
    "disposition": "completed",
    "decision_ref": "user:关闭 REPORT-003B-R2 并立即建立回归测试并实施修复",
    "closed_at": "2026-09-03T15:56:25.654791Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
