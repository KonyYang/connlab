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
    "task_id": "TASK_FEE_DEFAULT_FILL_REMAINING_RULE_EXTENSIONS",
    "summary": "Extend deterministic Fee default filling for the four reviewed pricing mappings and other audit-proven unambiguous aliases.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Implement reviewed defaults for Contact Retention Force, Mechanical Shock, Crimping/Wending Tensile Strength, and Current Rating as the Temperature rise alias; audit current coverage and add only unambiguous matches while preserving Pending for ambiguous pricing.",
    "scope_paths": [
      "backend/modules/fee_evaluation/fee_default_fill.py",
      "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
      "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
      "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_08_22.json",
      "backend/modules/fee_evaluation/seeds/fee_rules_v2026_08_22.json",
      "tests/unit/test_fee_default_fill.py",
      "tests/unit/test_fee_rule_matcher.py",
      "tests/unit/test_fee_rule_seed_loader.py",
      "tests/unit/test_confirmed_matrix_fee_draft_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "e02ccfcf1757999d7c09355696e9cb32f33c8ab1",
    "started_at": "2026-08-22T06:18:55.362811Z",
    "updated_at": "2026-08-22T06:18:55.362811Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_FORM_DRAFT_PREVIEW_AUTHORITY_SEPARATION",
    "tier": "standard",
    "subject": "5e07ab92900826fdc1f83ec85f68fff75b1a2a82",
    "summary": "Make Fee Form an always-available draft preview while preserving Project Workbench as the only official output authority.",
    "disposition": "completed",
    "decision_ref": "User confirmed close on 2026-08-22",
    "closed_at": "2026-08-22T06:10:05.341304Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
