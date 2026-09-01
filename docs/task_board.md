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
    "task_id": "REPORT-003B-R1",
    "summary": "Allow Equipment List updates to proceed when a source reference is absent from the calibration workbook by publishing an ID-only placeholder row and warning the operator to complete it manually in Word.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Change only unmatched-equipment preview, validation, update eligibility, user copy, tests, and current architecture documentation; preserve blockers for ambiguity, incomplete catalog data, invalid complete overrides, and preserve the controlled report publication transaction.",
    "scope_paths": [
      "backend/application/equipment_report_update_service.py",
      "tests/unit/test_equipment_report_update_service.py",
      "tests/integration/test_report_workspace_api.py",
      "frontend/src/features/report-workspace/reportWorkspaceModel.ts",
      "frontend/src/features/report-workspace/reportWorkspaceModel.test.ts",
      "frontend/src/features/report-workspace/ReportWorkspace.tsx",
      "frontend/src/features/report-workspace/ReportWorkspace.test.tsx",
      "docs/report_generation_architecture.md",
      "docs/task_board.md"
    ],
    "risk_reasons": [
      "The change alters which Equipment List preview conditions may publish rows into the authoritative current Internal Report."
    ],
    "activation_head": "6d822c3a0445dc3c1ed34cd95770087695ccf2f8",
    "started_at": "2026-09-01T22:56:08.677490Z",
    "updated_at": "2026-09-01T23:09:00.525054Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "REPORT-003B-R1",
      "stage": "revision",
      "status": "running",
      "summary": "User requested that row-level incomplete or incorrect equipment data warn without blocking; operators may correct or skip it and update confirmed content.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "RELEASE-007A",
    "tier": "standard",
    "subject": "6b5052114ef11271ed31171fbebad4897e5036cf",
    "summary": "Bundle the pywin32 win32timezone dependency in portable browser and desktop releases so packaged Excel COM can read the approved legacy equipment calibration workbook.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭 after reviewing the RELEASE-007A delivery.",
    "closed_at": "2026-09-01T22:42:05.168941Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
