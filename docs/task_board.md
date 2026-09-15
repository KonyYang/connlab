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
    "task_id": "TASK_FEE_FORM_XLSX_NATIVE_GENERATION",
    "summary": "Migrate Fee Form generation to native XLSX without Excel COM",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Use the approved FDQF-E-176 XLSX template to generate Fee Forms without Excel COM; preserve fee authority, formulas, formatting, history and both publication entry points; verify performance and packaged runtime.",
    "scope_paths": [
      "backend/application/fee_evaluation_template_discovery.py",
      "backend/application/fee_form_publication_service.py",
      "backend/application/project_folder_required_forms_service.py",
      "backend/infrastructure/office/fee_evaluation_workbook_gateway.py",
      "backend/infrastructure/office/fee_evaluation_sheet_ops.py",
      "backend/infrastructure/office/fee_evaluation_anchor_snapshot.py",
      "backend/infrastructure/office/fee_evaluation_matrix_basic_fill_writer.py",
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "tests/unit/test_fee_evaluation_template_discovery.py",
      "tests/unit/test_fee_evaluation_workbook_gateway.py",
      "tests/unit/test_fee_form_publication_service.py",
      "tests/unit/test_project_folder_required_forms_service.py",
      "tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py",
      "tests/integration/test_fee_evaluation_export_child_transaction.py",
      "docs/packaging_notes.md"
    ],
    "risk_reasons": [],
    "activation_head": "1ef24c762495feca071e007213a6f65ce937584f",
    "started_at": "2026-09-15T12:10:43.003929Z",
    "updated_at": "2026-09-15T12:10:43.003929Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_CUSTOMER_REPORT_PROGRESS",
    "tier": "high_risk",
    "subject": "81fa309ecad02aa0cb1d54425b59db2c79b7e7cb",
    "summary": "Project customer report background generation with real progress and recoverable results",
    "disposition": "cancelled",
    "decision_ref": "User requested closing the task. Preserve implemented commit 81fa309e and verified core functionality; discontinue the unapproved Word-owned-process timeout-cleanup extension without claiming full acceptance.",
    "closed_at": "2026-09-15T12:00:14.421292Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
