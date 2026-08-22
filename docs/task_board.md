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
    "task_id": "TASK_FEE_DURATION_LABELS_PER_HOUR",
    "summary": "Ensure reviewed high-temperature and temperature-humidity Matrix labels default Fee Unit Type to per hour.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Match High Temp. Life, Cycling Temperature & Humidity, and Thermal distrubance to their existing authoritative Fee duration rules so Unit Type is per hour, without changing price, duration, Units, or output authority.",
    "scope_paths": [
      "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
      "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_08_23_r9.json",
      "backend/modules/fee_evaluation/seeds/fee_rules_v2026_08_23_r9.json",
      "tests/unit/test_fee_rule_matcher.py",
      "tests/unit/test_fee_default_fill.py",
      "tests/unit/test_fee_rule_seed_loader.py",
      "tests/unit/test_confirmed_matrix_fee_draft_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "2aa1b7728f10a7b4c1a85dd9cfa11a2d1bed7d1b",
    "started_at": "2026-08-22T23:45:22.606992Z",
    "updated_at": "2026-08-22T23:45:22.606992Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_DEFAULT_FILL_REMAINING_RULE_EXTENSIONS",
    "tier": "standard",
    "subject": "eec597852a37aaa6dc35b4aced7fc37851b3a88a",
    "summary": "Extend deterministic Fee default filling for the four reviewed pricing mappings and other audit-proven unambiguous aliases.",
    "disposition": "completed",
    "decision_ref": "User confirmed close on 2026-08-22",
    "closed_at": "2026-08-22T10:55:23.741542Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
