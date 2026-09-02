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
    "task_id": "REPORT-003B-R2",
    "summary": "Align controlled internal-report typography and Equipment List output with the approved business format while preserving calibration waivers.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Preserve Not applicable in both Equipment Last Cal. and Cal. Due; render bold-underlined report chapter headings at 12 pt and other generated report/table content at 11 pt; widen the Equipment ID Number column so standard lab IDs do not wrap; remove Word keep-with-next pagination-control marks from generated and section-updated reports; protect manual edits and external source files.",
    "scope_paths": [
      "backend/infrastructure/office/test_report_document_gateway.py",
      "tests/unit/test_test_report_document_gateway.py",
      "tests/unit/test_equipment_report_update_service.py",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [],
    "activation_head": "c392cf98fc6c6dcd6ea6100e6c3b4cbba32dd8fb",
    "started_at": "2026-09-02T10:34:25.613709Z",
    "updated_at": "2026-09-02T10:34:25.613709Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-003B-R1",
    "tier": "high_risk",
    "subject": "6d570521a4ec03724112d36100c91bc1fcdfa97d",
    "summary": "Allow Equipment List updates to proceed when a source reference is absent from the calibration workbook by publishing an ID-only placeholder row and warning the operator to complete it manually in Word.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭 after reviewing the revised non-blocking Equipment List behavior.",
    "closed_at": "2026-09-02T05:01:06.203160Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
