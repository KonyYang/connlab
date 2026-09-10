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
    "task_id": "TASK_FEE_FORM_IMPORT",
    "summary": "Import Fee Form into editable draft with same-Matrix restoration and cross-project price reuse.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Read ConnLab xls/xlsx Fee Forms, preview matches and conflicts, explicitly apply to current draft only. Same-Matrix groups require identical ordered descriptions; cross-project imports only unit price/type/base fee with explicit ambiguous price selection. Preserve unmatched rows, totals recomputation and Update Fee authority.",
    "scope_paths": [
      "backend/infrastructure/office/fee_form_import_gateway.py",
      "backend/api/routes_fee_form_import.py",
      "backend/api/main.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/fee-evaluation",
      "tests/unit/test_fee_form_import_gateway.py",
      "tests/integration/test_fee_form_import_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "160b4dade8f2d4b6633f4030de33f49ff50ab5ca",
    "started_at": "2026-09-10T13:00:20.656265Z",
    "updated_at": "2026-09-10T13:00:20.656265Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_LOCK_RESILIENT_UPDATE",
    "tier": "high_risk",
    "subject": "f810b9562a3b1ec7ecde9f151a3114619ea3ee86",
    "summary": "Make Update project folder safe and recoverable when the existing official workspace contains files held open by Windows processes.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested: 关闭任务",
    "closed_at": "2026-09-10T11:41:57.034736Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
