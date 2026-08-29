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
    "task_id": "TASK_MATRIX_XLSX_ROUND_TRIP",
    "summary": "Implement two-phase ConnLab Matrix XLSX import: strict visible-format fallback with Day default 0 and non-blocking warning, then hidden metadata with fingerprint-validated lossless round-trip.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Matrix XLSX import/export, preview UI, source pickers, draft propagation, metadata/fingerprint validation, and focused regression coverage.",
    "scope_paths": [
      "backend/application",
      "backend/api",
      "backend/desktop",
      "backend/infrastructure/office",
      "backend/modules/test_plan",
      "frontend/src/api",
      "frontend/src/features/matrix-editor",
      "tests/unit",
      "tests/integration",
      "docs/task_board.md"
    ],
    "risk_reasons": [
      "Imports external Excel files into a draft that can later become authoritative through Confirm Matrix.",
      "Changes the supported Matrix round-trip contract and generated workbook structure.",
      "Requires coordinated backend, frontend, Office-format, and compatibility behavior."
    ],
    "activation_head": "71c519b22eb48baf3685ab70acbfac066d3f3090",
    "started_at": "2026-08-29T04:13:35.511871Z",
    "updated_at": "2026-08-29T04:13:35.511871Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-001D",
    "tier": "high_risk",
    "subject": "42f3887ca38327f54937dc101631c407e9a5b46d",
    "summary": "Carry confirmed application-form Test Sample Information through structured persistence and Basic Information authority into the E-3707_H SAMPLE DESCRIPTION table.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭.",
    "closed_at": "2026-08-29T04:06:23.444332Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
