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
    "task_id": "TASK_REPOSITORY_TEST_BASELINE_REPAIR",
    "summary": "Repair the repository test baseline by resolving Draft Measurement Plan Excel gateway import errors and the Product Spec Matrix Group P label contract mismatch.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Restore test collection and align the Group P parser contract without changing unrelated product behavior.",
    "scope_paths": [
      "backend/infrastructure/office/draft_measurement_plan_workbook_gateway.py",
      "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
      "backend/modules/test_plan/product_spec_matrix_parser.py",
      "backend/modules/test_plan/product_spec_matrix_parser_support.py",
      "tests/unit/test_draft_measurement_plan_workbook_gateway.py",
      "tests/unit/test_draft_measurement_plan_workbook_generation_service.py",
      "tests/unit/test_task_368b_product_spec_matrix_group_p_header.py"
    ],
    "risk_reasons": [],
    "activation_head": "058d7db51dbf4cefffd9faa0278b20db5b545394",
    "started_at": "2026-09-04T09:54:36.229118Z",
    "updated_at": "2026-09-04T09:54:36.229118Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_DRAFT_LIFECYCLE_GOVERNANCE",
    "tier": "high_risk",
    "subject": "5122fdd93888992e6c377bf634749fa9ea287945",
    "summary": "Govern Matrix draft lifecycle so only one working draft is current, authority-linked lineage is explicit, and stale unreferenced drafts can be cleaned safely.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closing the completed Matrix draft lifecycle task and opening the repository test baseline repair task.",
    "closed_at": "2026-09-04T09:54:36.229118Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
