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
    "task_id": "TASK_FEE_CONTAINMENT_UNIT_TYPES",
    "summary": "Extend reviewed Fee matching for durability, dust, thermal cycling, and contact retention labels.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Match the supplied Matrix labels to existing Fee families; set Durability to per cycle, Dust contamination to Dust (Benign), unqualified Thermal Cycling to per hour without choosing a rate-specific price, and Contact Retention variants to per reading, preserving existing Units and output authority.",
    "scope_paths": [
      "backend/modules/fee_evaluation/fee_rule_matcher.py",
      "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
      "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
      "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_08_23_r11.json",
      "backend/modules/fee_evaluation/seeds/fee_rules_v2026_08_23_r11.json",
      "tests/unit/test_fee_rule_matcher.py",
      "tests/unit/test_fee_default_fill.py",
      "tests/unit/test_fee_rule_seed_loader.py",
      "tests/unit/test_confirmed_matrix_fee_draft_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "dd6a66ae9e5fd0940ecd77d1a7dc2812de16dc7a",
    "started_at": "2026-08-23T00:31:48.462458Z",
    "updated_at": "2026-08-23T00:31:48.462458Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_CONTACT_SOLDER_UNIT_TYPES",
    "tier": "standard",
    "subject": "53f5f16663b51922b53a3d09570d20554481b62a",
    "summary": "Set reviewed Contact Retention and solder-related Fee Unit Types to their confirmed business values.",
    "disposition": "completed",
    "decision_ref": "User confirmed close on 2026-08-23",
    "closed_at": "2026-08-23T00:24:23.058057Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
