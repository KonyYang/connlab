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
    "updated_at": "2026-08-23T00:23:00.912786Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_CONTACT_SOLDER_UNIT_TYPES",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_FEE_CONTACT_SOLDER_UNIT_TYPES",
      "subject": "53f5f16663b51922b53a3d09570d20554481b62a",
      "summary": "Mapped Contact Retention and Solder ability to per reading, and Resistance to soldering heat to per sample, without inferring unconfirmed solder quantities.",
      "scope_ok": true,
      "changed_paths": [
        "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
        "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
        "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_08_23_r10.json",
        "backend/modules/fee_evaluation/seeds/fee_rules_v2026_08_23_r10.json",
        "tests/integration/test_confirmed_matrix_fee_draft_api.py",
        "tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py",
        "tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py",
        "tests/integration/test_matrix_editor_session_api.py",
        "tests/unit/test_confirmed_matrix_fee_draft_service.py",
        "tests/unit/test_fee_default_fill.py",
        "tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py",
        "tests/unit/test_fee_rule_seed_loader.py",
        "tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py",
        "tests/unit/test_matrix_fee_rebase_promotion_service.py"
      ],
      "validation": [
        {
          "name": "backend QA",
          "status": "passed",
          "detail": "658 passed"
        },
        {
          "name": "frontend Fee tests",
          "status": "passed",
          "detail": "66 passed"
        },
        {
          "name": "frontend build",
          "status": "passed",
          "detail": "TypeScript and Vite build succeeded"
        },
        {
          "name": "browser verification",
          "status": "passed",
          "detail": "Three live rows displayed the confirmed Unit Types with no console errors"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented through three red-green public-seam slices."
        },
        "reviewer": {
          "status": "passed",
          "summary": "No standards or specification findings."
        },
        "qa": {
          "status": "passed",
          "summary": "Backend, frontend, build, and browser validation passed."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Active r10 seed and reviewed Unit Type defaults load through draft, persistence, export, rebase, and Matrix session paths."
      }
    }
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
