# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_FEE_REFERENCE_20260915_RULE_OPTIMIZATION",
    "summary": "Upgrade Fee Evaluation pricing reference and improve confirmed Matrix quantity and rule matching",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Versioned 2026-09-15 Unit Price Reference seed, confirmed Matrix-derived fee defaults, safe matching and same-condition manual reuse, with regression tests; no external workbook mutation or IR/DWV Test points schema",
    "scope_paths": [
      "backend/modules/fee_evaluation",
      "backend/application/confirmed_matrix_fee_draft_service.py",
      "backend/application/confirmed_matrix_fee_draft_line_builder.py",
      "frontend/src/features/fee-evaluation",
      "tests/unit",
      "tests/integration"
    ],
    "risk_reasons": [],
    "activation_head": "587cddc10cc5a5a27d06933a114ec4073d5f6720",
    "started_at": "2026-09-29T09:59:15.465452Z",
    "updated_at": "2026-09-29T16:30:44.590210Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_REFERENCE_20260915_RULE_OPTIMIZATION",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "roles": {
        "reviewer": {
          "detail": "Focused exact-diff review; no actionable findings",
          "status": "passed"
        },
        "qa": {
          "status": "passed"
        },
        "developer": {
          "status": "passed"
        }
      },
      "integration": {
        "detail": "Clean master HEAD; no publication",
        "status": "passed"
      },
      "changed_paths": [
        "backend/api/confirmed_matrix_fee_evaluation_export_dtos.py",
        "backend/api/routes_confirmed_matrix_fee_evaluation_pricing_draft.py",
        "backend/application/confirmed_matrix_fee_base_fee_policy.py",
        "backend/application/confirmed_matrix_fee_draft_build_support.py",
        "backend/application/confirmed_matrix_fee_draft_service.py",
        "backend/application/confirmed_matrix_fee_manual_defaults.py",
        "backend/infrastructure/office/fee_form_import_gateway.py",
        "backend/modules/fee_evaluation/fee_default_fill.py",
        "backend/modules/fee_evaluation/fee_reference_snapshot.py",
        "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
        "backend/modules/fee_evaluation/fee_rule_extensions.py",
        "backend/modules/fee_evaluation/fee_rule_matcher.py",
        "backend/modules/fee_evaluation/fee_rule_models.py",
        "backend/modules/fee_evaluation/fee_rule_seed_loader.py",
        "backend/modules/fee_evaluation/seeds/active_fee_rule_seed.json",
        "backend/modules/fee_evaluation/seeds/fee_reference_rows_v2026_09_15.json",
        "backend/modules/fee_evaluation/seeds/fee_rule_extensions_v2026_09_15.json",
        "backend/modules/fee_evaluation/seeds/fee_rules_v2026_09_15.json",
        "docs/fee_reference_20260915.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts",
        "frontend/src/features/fee-evaluation/feeEvaluationPricingDraftHydration.ts",
        "frontend/src/workbench.css",
        "scripts/build_fee_reference_20260915.py",
        "tests/integration/test_confirmed_matrix_fee_draft_api.py",
        "tests/integration/test_confirmed_matrix_fee_draft_dependent_fields_api.py",
        "tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py",
        "tests/integration/test_fee_evaluation_pricing_draft_api.py",
        "tests/integration/test_fee_pricing_draft_measurement_plan_rebase_attestation.py",
        "tests/integration/test_matrix_editor_session_api.py",
        "tests/unit/test_confirmed_matrix_fee_draft_rule_resolution.py",
        "tests/unit/test_confirmed_matrix_fee_draft_service.py",
        "tests/unit/test_fee_default_fill.py",
        "tests/unit/test_fee_default_fill_explicit_hour_authority.py",
        "tests/unit/test_fee_evaluation_pricing_draft_persistence_service.py",
        "tests/unit/test_fee_reference_snapshot.py",
        "tests/unit/test_fee_rule_matcher.py",
        "tests/unit/test_fee_rule_seed_loader.py",
        "tests/unit/test_fee_rule_temperature_force_alias_safe_rebase.py",
        "tests/unit/test_matrix_fee_rebase_promotion_service.py",
        "tests/unit/test_task_365c_fee_compatibility.py"
      ],
      "scope_ok": true,
      "version": 1,
      "summary": "Versioned Fee price rules and confirmed-Matrix-derived defaults; preserve manually confirmed Units for unchanged Matrix and reject stale pricing payloads after Matrix revision.",
      "schema": "connlab.sol-task-report",
      "task_id": "TASK_FEE_REFERENCE_20260915_RULE_OPTIMIZATION",
      "subject": "14e522976833ddfbc71d8d6d7e9a44856a567ecc",
      "validation": [
        {
          "status": "passed",
          "name": "frontend",
          "detail": "706 passed, 1 skipped; TypeScript and Vite production build passed"
        },
        {
          "status": "passed",
          "name": "python",
          "detail": "3143 passed, 8 skipped, 19 deselected"
        },
        {
          "status": "passed",
          "name": "browser",
          "detail": "Read-only smoke on current project; revision transition covered in isolated tests"
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_CONFIRM_STATE_AND_FOLDER_HINT",
    "tier": "standard",
    "subject": "c6940c6bd4218ab1f801c0057872e2f8e96b4ecb",
    "summary": "Fix Fee confirmation re-entry state and explain unavailable project folder on Fee Form action",
    "disposition": "completed",
    "decision_ref": "User explicit close request.",
    "closed_at": "2026-09-29T05:04:11.430731Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_361A_FEE_SUMMARY_ACCEPTANCE_CONTRACT",
      "tier": "standard",
      "closed_at": "2026-09-18T03:01:50.000000Z"
    },
    {
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS_COMPLETE",
      "tier": "high_risk",
      "closed_at": "2026-09-17T11:59:24.022479Z"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.

## Pending engineering-debt tasks ( backlog / not active )

These items are not in-flight; they are recorded here for prioritization. They do not
change the `active` field above.

### TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT

**Tier:** micro
**Revised from:** the stale broad test-environment proposal discovered during TASK_361A
**Goal:** Keep the supported test entry point on the same Python runtime as ConnLab development.

The original diagnosis was rechecked before implementation:

- `C:/PythonEnvs/connlab/.venv` is Python 3.11.9 and imports Tkinter 8.6 successfully; no
  dependency installation is needed.
- Office-dependent integration tests already use the `office_integration` marker. The normal gate
  excludes them and `-Suite Office` remains the explicit installed-Office check.
- WorkBuddy or Codex temporary-directory and safe-delete restrictions are host permissions, not
  ConnLab product behavior. They must be handled by the runner environment or an explicitly
  permitted pytest temp location, not by weakening repository cleanup or test semantics.

The remaining defect was limited to `scripts/run_tests.ps1`: it invoked the ambient `py` launcher,
which selected Python 3.13.3 instead of the Python 3.11.9 environment used by ConnLab. The revised
runner defaults to `C:/PythonEnvs/connlab/.venv/Scripts/python.exe`, supports an explicit
`-PythonExe` override, fails clearly when that interpreter is missing, and preserves the existing
normal/Office split.

**Validation:** the focused runner contract passes, and the complete non-Office Python gate passes
with 2954 tests, 7 skips, and 19 Office tests deselected on Python 3.11.9. No product code,
dependencies, Office implementation, or host safety policy changed.
