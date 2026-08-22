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
    "task_id": "TASK_FEE_EVALUATION_DETERMINISTIC_DEFAULT_FILL_EXTENSION",
    "summary": "Extend deterministic Fee Evaluation defaults for MFG and specified-current CR labels, and safely repair confirmed-duration consumption where current authority already exists.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Implement reviewed MFG IIA/IIIA precedence and pricing, map CR HP labels onto existing confirmed authority, audit duration-backed pending rows and fix only proven propagation gaps; exclude Fee Form preview workflow and unresolved business rules.",
    "scope_paths": [
      "backend/modules/fee_evaluation/fee_rule_matcher.py",
      "backend/modules/fee_evaluation/fee_default_fill.py",
      "backend/modules/fee_evaluation/mfg_duration.py",
      "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
      "backend/modules/fee_evaluation/seeds/fee_rules_v2026_07_17.json",
      "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_07_17.json",
      "backend/application/confirmed_matrix_fee_draft_service.py",
      "tests/unit/test_fee_rule_matcher.py",
      "tests/unit/test_fee_default_fill.py",
      "tests/unit/test_confirmed_matrix_fee_draft_service.py",
      "tests/unit/test_confirmed_matrix_fee_cr_specified_current_authority.py",
      "tests/integration/test_confirmed_matrix_fee_draft_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "0d87367ba62258066d6b0f44e163d8f062bc9e2f",
    "started_at": "2026-08-22T05:11:23.737053Z",
    "updated_at": "2026-08-22T05:38:24.851217Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_EVALUATION_DETERMINISTIC_DEFAULT_FILL_EXTENSION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_FEE_EVALUATION_DETERMINISTIC_DEFAULT_FILL_EXTENSION",
      "subject": "6e15e88c970e09aaca34c1d28084168a02b0a3fd",
      "summary": "Added versioned deterministic MFG IIA/IIIA and specified-current HP CR defaults, preserved confirmed authority precedence, and repaired typed duration consumption without changing unresolved fee rules or Fee Form workflow.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/confirmed_matrix_fee_base_fee_policy.py",
        "backend/modules/fee_evaluation/fee_default_fill.py",
        "backend/modules/fee_evaluation/mfg_duration.py",
        "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
        "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_08_22.json",
        "backend/modules/fee_evaluation/seeds/fee_rules_v2026_08_22.json",
        "tests/integration/test_confirmed_matrix_fee_draft_api.py",
        "tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py",
        "tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py",
        "tests/integration/test_matrix_editor_session_api.py",
        "tests/unit/test_confirmed_matrix_fee_base_fee_policy.py",
        "tests/unit/test_confirmed_matrix_fee_draft_service.py",
        "tests/unit/test_fee_default_fill_explicit_hour_authority.py",
        "tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py",
        "tests/unit/test_fee_rule_matcher.py",
        "tests/unit/test_fee_rule_seed_loader.py",
        "tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py",
        "tests/unit/test_matrix_fee_rebase_promotion_service.py"
      ],
      "validation": [
        {
          "name": "Affected backend and API suite",
          "status": "passed",
          "detail": "334 passed"
        },
        {
          "name": "Fee Evaluation frontend suite",
          "status": "passed",
          "detail": "66 passed"
        },
        {
          "name": "Frontend production build",
          "status": "passed",
          "detail": "tsc and Vite build passed"
        },
        {
          "name": "Current-project read-only API smoke",
          "status": "passed",
          "detail": "MFG matched IIA with 1000/day and duration pending; specified-current CR calculated 10 per reading x 12"
        },
        {
          "name": "Exact diff checks",
          "status": "passed",
          "detail": "git diff --check and active seed identity/alias probes passed"
        }
      ],
      "roles": {
        "qa": {
          "detail": "Backend/API, frontend tests, build, and read-only runtime smoke passed",
          "status": "passed"
        },
        "developer": {
          "detail": "TDD red-green and affected checks passed",
          "status": "passed"
        },
        "reviewer": {
          "detail": "Standards and specification review found no remaining actionable findings",
          "status": "passed"
        }
      },
      "integration": {
        "subject": "6e15e88c970e09aaca34c1d28084168a02b0a3fd",
        "status": "passed",
        "clean": true,
        "detail": "Implementation committed on master; exact scope verified"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_EDITOR_RENDER_AND_TEST_ORGANIZATION",
    "tier": "standard",
    "subject": "5ab574a1c0cbc248e1317b478bc8c46d73873bff",
    "summary": "Organize Matrix Editor rendering and split public UI tests into at most three behavioral groups without changing observable behavior.",
    "disposition": "completed",
    "decision_ref": "User request 2026-08-22: 关闭",
    "closed_at": "2026-08-22T05:08:44.476150Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
