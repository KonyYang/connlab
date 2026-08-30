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
    "task_id": "TASK_MATRIX_TEST_POINT_RECORD_DOWNLOAD_ACTIONS",
    "summary": "Move LLCR and CR draft workbook downloads into their corresponding Test points rows and remove the redundant standalone panel.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Integrate the existing LLCR and CR draft workbook download actions and per-action status into the Test points summary card without changing generation authority, availability, or download behavior; preserve responsive and accessibility behavior.",
    "scope_paths": [
      "frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.tsx",
      "frontend/src/features/contact-measurement-plan/ContactMeasurementPlanSummaryCard.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/LlcrCrRecordWorkbookPanel.tsx",
      "frontend/src/contact-measurement-plan.css"
    ],
    "risk_reasons": [],
    "activation_head": "a367b7a93f7cae8d9ed6552f1c54b2ffefc92262",
    "started_at": "2026-08-30T00:00:00.283113Z",
    "updated_at": "2026-08-30T00:00:00.283113Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-002",
    "tier": "high_risk",
    "subject": "ff9f5fb421feb1b161dd8ce74b99c0048e417e04",
    "summary": "Implement the LLCR Result Dataset vertical slice and Report Workspace with immutable import revisions and safe non-overwriting Word report synchronization.",
    "disposition": "completed",
    "decision_ref": "User explicit close: 关闭",
    "closed_at": "2026-08-29T10:44:29.180522Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
