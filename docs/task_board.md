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
    "task_id": "TASK_TEST_SUITE_TRUST_RESTORATION",
    "summary": "Restore a high-signal green test baseline, remove obsolete implementation-coupled tests, isolate Office integration, and fix confirmed residual regressions.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Only test architecture, validation entrypoints, stale fixtures, and the three diagnosed runtime defects: Point Profile fallback, SQLite locked diagnostics, and Matrix source-picker dismissal.",
    "scope_paths": [
      "AGENTS.md",
      "README.md",
      "pyproject.toml",
      "scripts/run_tests.ps1",
      "tests/test_basic.py",
      "tests/unit/test_frontend_shell_files.py",
      "tests/unit/test_frontend_architecture.py",
      "tests/unit/test_phase5_ux_decision.py",
      "tests/unit/test_phase6_scope_activation.py",
      "tests/unit/test_phase7_validation_summary.py",
      "tests/unit/test_phase9_scope_activation.py",
      "tests/unit/test_phase10a_scope_activation.py",
      "tests/unit/test_intake_precheck_business_gap_audit.py",
      "backend/application/confirmed_matrix_fee_draft_line_builder.py",
      "backend/infrastructure/storage/standard_record_method_sync_schema_migration.py",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixImportOptionalStandardFallback.test.tsx",
      "tests/integration/test_confirmed_matrix_fee_draft_api.py",
      "tests/integration/test_contact_measurement_plan_schema_check_compatibility_startup.py",
      "tests/integration/test_customer_feedback_form_generation_api.py",
      "tests/integration/test_matrix_to_test_record_smoke_flow_api.py",
      "tests/integration/test_project_test_plan_preview_api.py",
      "tests/integration/test_project_test_plan_source_candidates_api.py",
      "tests/unit/test_confirmed_matrix_fee_draft_step_quantities.py",
      "tests/unit/test_contact_measurement_plan_schema.py",
      "tests/unit/test_external_resource_service.py",
      "tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py",
      "tests/unit/test_standard_record_method_sync_schema_migration.py"
    ],
    "risk_reasons": [],
    "activation_head": "d9b829399a270798b2366d33c8f1583f74a2ce5e",
    "started_at": "2026-08-20T23:46:38.452100Z",
    "updated_at": "2026-08-21T00:17:47.087442Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEST_SUITE_TRUST_RESTORATION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "task_id": "TASK_TEST_SUITE_TRUST_RESTORATION",
      "changed_paths": [
        "AGENTS.md",
        "README.md",
        "backend/application/confirmed_matrix_fee_draft_line_builder.py",
        "backend/application/contact_point_profile_confirmed_consumer_adapter.py",
        "backend/infrastructure/storage/standard_record_method_sync_schema_migration.py",
        "docs/project_management/SOL_NATIVE_WORKFLOW.md",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "pyproject.toml",
        "scripts/connlab_sol_task.py",
        "scripts/run_tests.ps1",
        "tests/integration/test_customer_feedback_form_generation_api.py",
        "tests/integration/test_matrix_to_test_record_smoke_flow_api.py",
        "tests/integration/test_project_test_plan_preview_api.py",
        "tests/integration/test_project_test_plan_source_candidates_api.py",
        "tests/test_basic.py",
        "tests/unit/test_confirmed_matrix_fee_draft_step_quantities.py",
        "tests/unit/test_connlab_sol_native_workflow.py",
        "tests/unit/test_contact_point_profile_confirmed_consumer_adapter.py",
        "tests/unit/test_external_resource_service.py",
        "tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py",
        "tests/unit/test_frontend_architecture.py",
        "tests/unit/test_frontend_shell_files.py",
        "tests/unit/test_intake_precheck_business_gap_audit.py",
        "tests/unit/test_packaging_notes.py",
        "tests/unit/test_phase10a_scope_activation.py",
        "tests/unit/test_phase5_ux_decision.py",
        "tests/unit/test_phase6_scope_activation.py",
        "tests/unit/test_phase7_validation_summary.py",
        "tests/unit/test_phase9_scope_activation.py",
        "tests/unit/test_standard_record_method_sync_schema_migration.py"
      ],
      "validation": [
        {
          "result": "2252 Python passed, 421 frontend passed, production build passed",
          "status": "passed",
          "name": "full quality gate"
        },
        {
          "result": "18 passed",
          "status": "passed",
          "name": "Sol-native workflow contracts"
        }
      ],
      "subject": "ecfb8f503a3718b175378cb00f70ddffc1c3b44f",
      "schema": "connlab.sol-task-report",
      "summary": "Restored a trusted validation baseline, fixed diagnosed regressions, and removed the standard-task frozen path blocker.",
      "roles": {
        "developer": {
          "summary": "Implemented and self-reviewed exact diff.",
          "status": "passed"
        },
        "reviewer": {
          "summary": "Standards and specification review passed with no findings.",
          "status": "passed"
        },
        "qa": {
          "summary": "Full gate and affected workflow contracts passed.",
          "status": "passed"
        }
      },
      "scope_ok": true,
      "integration": {
        "status": "passed",
        "mode": "direct_primary",
        "head": "ecfb8f503a3718b175378cb00f70ddffc1c3b44f"
      },
      "version": 1
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_EDITOR_CANCEL_DISCARD_IMPORTED_DRAFT",
    "tier": "standard",
    "subject": "e8f9116407003ddd0aea999b30e2167c24cf83ae",
    "summary": "Ensure Matrix Editor Cancel discards the exact current imported draft before returning to Workbench.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭 on 2026-08-21 after browser-verified delivery.",
    "closed_at": "2026-08-20T23:36:14.036702Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
