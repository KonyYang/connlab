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
    "task_id": "TASK_MATRIX_IMPORT_SAMPLE_SIZE_CASE_COMPATIBILITY",
    "summary": "Accept a legacy ConnLab Matrix XLSX footer labeled Sample Size without weakening the controlled footer structure.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Fix the reproduced Import Matrix rejection for 9.7matrix.xlsx by making the controlled Sample size footer label case-insensitive, with regression coverage.",
    "scope_paths": [
      "backend/infrastructure/office/connlab_matrix_xlsx_gateway.py",
      "tests/unit/test_connlab_matrix_xlsx_gateway.py"
    ],
    "risk_reasons": [],
    "activation_head": "7af05a382159fdf994a78ec8331da7242c24b0b5",
    "started_at": "2026-09-07T15:53:14.687615Z",
    "updated_at": "2026-09-07T15:59:19.800685Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SAMPLE_SIZE_CASE_COMPATIBILITY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "task_id": "TASK_MATRIX_IMPORT_SAMPLE_SIZE_CASE_COMPATIBILITY",
      "validation": [
        {
          "status": "passed",
          "name": "TDD RED: title-case footer regression"
        },
        {
          "name": "Gateway and XLSX upload related pytest",
          "detail": "8 passed",
          "status": "passed"
        },
        {
          "name": "Real 9.7matrix.xlsx parse",
          "detail": "12 groups, 24 rows, no blockers",
          "status": "passed"
        },
        {
          "status": "passed",
          "name": "git diff --check"
        }
      ],
      "changed_paths": [
        "backend/infrastructure/office/connlab_matrix_xlsx_gateway.py",
        "tests/unit/test_connlab_matrix_xlsx_gateway.py"
      ],
      "summary": "Matrix XLSX import now accepts title-case Sample Size, Time, and Fee footer labels while preserving the required order and structure.",
      "subject": "9e4bcda7666e7277e50520b4c74f244980fdafbe",
      "integration": {
        "mode": "direct_primary",
        "status": "passed"
      },
      "roles": {
        "developer": {
          "summary": "Implemented the minimal case-insensitive footer-label compatibility and self-reviewed the exact diff.",
          "status": "passed"
        }
      },
      "schema": "connlab.sol-task-report",
      "scope_ok": true,
      "version": 1
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_OPTIMIZATION_6_10",
    "tier": "high_risk",
    "subject": "3ba3fa366a75c5c5d753b7225b8825f13e2665e3",
    "summary": "Complete original Matrix optimization items 6-10 in verified batches.",
    "disposition": "completed",
    "decision_ref": "user: close completed optimization items 6-10",
    "closed_at": "2026-09-05T05:52:43.755198Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
