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
    "task_id": "TASK_FEE_CONTACT_SOLDER_UNIT_TYPES",
    "summary": "Set reviewed Contact Retention and solder-related Fee Unit Types to their confirmed business values.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Map Contact Retention and Solder ability to per reading, and Resistance to soldering heat to per sample, while preserving existing prices, Units authority, Pending fields, and output authority.",
    "scope_paths": [
      "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
      "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
      "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_08_23_r10.json",
      "backend/modules/fee_evaluation/seeds/fee_rules_v2026_08_23_r10.json",
      "tests/unit/test_fee_rule_matcher.py",
      "tests/unit/test_fee_default_fill.py",
      "tests/unit/test_fee_rule_seed_loader.py",
      "tests/unit/test_confirmed_matrix_fee_draft_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "8a477347e9f52e066e02688cfb8e53ea9c094205",
    "started_at": "2026-08-23T00:14:05.837063Z",
    "updated_at": "2026-08-23T00:14:05.837063Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_DURATION_LABELS_PER_HOUR",
    "tier": "standard",
    "subject": "114366a9949e7351767ee1d2b257d32e930a64f1",
    "summary": "Ensure reviewed high-temperature and temperature-humidity Matrix labels default Fee Unit Type to per hour.",
    "disposition": "completed",
    "decision_ref": "User confirmed close and requested the next Unit Type correction on 2026-08-23",
    "closed_at": "2026-08-23T00:14:05.837063Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
