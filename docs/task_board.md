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
    "task_id": "TASK_FEE_ADDITIVE_SAMPLE_QUANTITY_DEFAULTS",
    "summary": "Fee Evaluation automatically sums additive Matrix sample quantity expressions such as 3+3 for Units and keeps Sample preparation fully discounted by default.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fee draft default calculation, safe draft rebase behavior, and focused frontend/API verification for additive sample quantities and Sample preparation discount.",
    "scope_paths": [
      "backend/modules/fee_evaluation",
      "backend/application",
      "tests/unit",
      "tests/integration",
      "frontend/src/features/fee-evaluation"
    ],
    "risk_reasons": [],
    "activation_head": "53d063e35ce570a2735226c708e5496b96372e07",
    "started_at": "2026-09-08T22:43:11.360327Z",
    "updated_at": "2026-09-08T23:37:51.662560Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_ADDITIVE_SAMPLE_QUANTITY_DEFAULTS",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_FEE_ADDITIVE_SAMPLE_QUANTITY_DEFAULTS",
      "subject": "cc1da9f56f05e8dfaafb7186319d92faa0c0f881",
      "summary": "Fee defaults now sum additive quantities for Sample preparation while keeping it fully discounted, and unmatched test rows default to per sample with Units from the first valid quantity term, including 3+3 to 3, without guessing price.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/confirmed_matrix_fee_draft_line_builder.py",
        "backend/modules/fee_evaluation/fee_default_fill.py",
        "backend/modules/fee_evaluation/fee_default_fill_common.py",
        "tests/integration/test_confirmed_matrix_fee_draft_api.py",
        "tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py",
        "tests/unit/test_confirmed_matrix_fee_draft_service.py",
        "tests/unit/test_fee_default_fill.py"
      ],
      "validation": [
        {
          "name": "red regression",
          "status": "passed",
          "result": "Observed prior empty unit_label for unmatched 3+3 row."
        },
        {
          "name": "affected tests",
          "status": "passed",
          "result": "129 passed after implementation; 48 passed after contract alignment."
        },
        {
          "name": "complete Python suite",
          "status": "passed",
          "result": "2632 passed, 4 skipped, 19 deselected."
        },
        {
          "name": "frontend tests",
          "status": "passed",
          "result": "499 passed, 1 skipped."
        },
        {
          "name": "frontend production build",
          "status": "passed",
          "result": "151 modules transformed."
        },
        {
          "name": "live project API",
          "status": "passed",
          "result": "Pull Ring Lateral Force returned sample units from its actual group quantity while remaining no_rule_match with price pending."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "result": "Implemented valid primary sample quantity parsing and unmatched-line defaults with unit and API regression coverage."
        },
        "reviewer": {
          "status": "passed",
          "result": "Standards and spec review found no findings; unmatched pricing authority remains manual."
        },
        "qa": {
          "status": "passed",
          "result": "Complete backend, frontend, and production-build gate passed on committed state."
        }
      },
      "integration": {
        "status": "passed",
        "result": "Committed implementation and test alignment; live project Fee Draft API verified."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_SCHEDULE_AUTHORITY",
    "tier": "high_risk",
    "subject": "e05cc7594605e6d2a38a50951978cf5d534830bc",
    "summary": "Establish Project Schedule as an independent authority, remove duplicate schedule inputs from Basic Information, and source official document dates from the confirmed schedule.",
    "disposition": "completed",
    "decision_ref": "User: 关闭",
    "closed_at": "2026-09-08T22:17:38.248101Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
