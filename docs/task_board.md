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
    "task_id": "TASK_FEE_MATRIX_SELECTIVE_REUSE_20260930",
    "summary": "Selectively reuse confirmed Fee edits across Matrix revisions",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Use last manually Confirmed Fee; preserve unaffected manual pricing; recompute changed sample, point, and duration units; retain original sample expression display; no new buttons",
    "scope_paths": [
      "backend/application/matrix_fee_draft_rebase_service.py",
      "backend/application/matrix_fee_rebase_promotion_service.py",
      "backend/application/matrix_fee_pending_rebase_service.py",
      "backend/application/matrix_fee_pending_rebase_source.py",
      "backend/application/matrix_fee_rebase_promotion_values.py",
      "backend/application/confirmed_fee_pricing_snapshot.py",
      "backend/application/fee_evaluation_pricing_draft_v2_rebase.py",
      "backend/modules/fee_evaluation",
      "frontend/src/features/fee-evaluation",
      "tests/unit",
      "tests/integration"
    ],
    "risk_reasons": [],
    "activation_head": "855aab3bdc2d1d02e5dffb5144b41813170d3c27",
    "started_at": "2026-09-29T23:36:50.997026Z",
    "updated_at": "2026-09-30T00:34:27.616779Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_MATRIX_SELECTIVE_REUSE_20260930",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "subject": "c426f24799a74609aeddb0a76ca716b3ff262f3c",
      "integration": {
        "status": "passed",
        "mode": "direct_primary"
      },
      "task_id": "TASK_FEE_MATRIX_SELECTIVE_REUSE_20260930",
      "scope_ok": true,
      "version": 1,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/application/matrix_fee_draft_rebase_service.py",
        "backend/application/matrix_fee_pending_rebase_source.py",
        "backend/application/matrix_fee_rebase_promotion_service.py",
        "backend/application/matrix_fee_rebase_promotion_values.py",
        "backend/modules/fee_evaluation/fee_default_fill.py",
        "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
        "backend/modules/fee_evaluation/fee_step_quantity_defaults.py",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
        "tests/integration/test_confirmed_matrix_fee_draft_api.py",
        "tests/integration/test_matrix_editor_session_api.py",
        "tests/unit/test_confirmed_matrix_fee_draft_service.py",
        "tests/unit/test_fee_default_fill.py",
        "tests/unit/test_matrix_fee_draft_rebase_service.py",
        "tests/unit/test_matrix_fee_rebase_promotion_service.py"
      ],
      "summary": "Selectively reuse operator-confirmed Fee values across Matrix revisions; recalculate quantity-dependent Units and totals, retain first Matrix sample count for pricing, preserve original expression display.",
      "validation": [
        {
          "name": "Python non-Office full gate: 3154 passed, 8 skipped",
          "status": "passed"
        },
        {
          "name": "Frontend Vitest suite",
          "status": "passed"
        },
        {
          "name": "Frontend Vite production build",
          "status": "passed"
        }
      ],
      "roles": {
        "qa": {
          "status": "passed",
          "summary": "Full Python non-Office, frontend tests, and production build completed on final code state."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Focused same-agent standards and spec review; no outstanding findings."
        },
        "developer": {
          "status": "passed",
          "summary": "TDD red/green, implementation, and targeted checks completed."
        }
      },
      "schema": "connlab.sol-task-report"
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_REMOVE_REUSE_BUTTONS_20260930",
    "tier": "micro",
    "subject": "591b69d21a62b070510ec7c902fd2a34782baf29",
    "summary": "Remove per-row Fee price reuse action",
    "disposition": "completed",
    "decision_ref": "User explicit final close request on 2026-09-30.",
    "closed_at": "2026-09-29T23:20:07.390640Z"
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
