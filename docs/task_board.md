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
    "task_id": "TASK_FEE_REMOVE_REUSE_BUTTONS_20260930",
    "summary": "Remove per-row Fee price reuse action",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove Apply price to matching rows UI and unused local bulk-copy logic; keep manual row editing and Fee Form import.",
    "scope_paths": [
      "frontend/src/features/fee-evaluation",
      "frontend/src/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "b298da84b696846652faefeaf3aa7d49311c295a",
    "started_at": "2026-09-29T23:01:38.868864Z",
    "updated_at": "2026-09-29T23:07:26.919794Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_FEE_REMOVE_REUSE_BUTTONS_20260930",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationPreviewTable.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.test.ts",
        "frontend/src/features/fee-evaluation/feeEvaluationPreviewModel.ts",
        "frontend/src/workbench.css"
      ],
      "integration": {
        "detail": "Clean master HEAD; no publication",
        "status": "passed"
      },
      "schema": "connlab.sol-task-report",
      "roles": {
        "developer": {
          "detail": "Implementation and focused self-review passed",
          "status": "passed"
        }
      },
      "version": 1,
      "subject": "591b69d21a62b070510ec7c902fd2a34782baf29",
      "summary": "Removed per-row cross-group price copy action and its unused matching logic; individual price editing and Fee Form import remain.",
      "validation": [
        {
          "name": "targeted frontend",
          "detail": "40 tests passed; red test reproduced repeated actions before change",
          "status": "passed"
        },
        {
          "name": "production build",
          "detail": "TypeScript and Vite build passed",
          "status": "passed"
        },
        {
          "name": "browser",
          "detail": "No bulk price buttons, Import Fee Form present, 100 editable price fields visible",
          "status": "passed"
        }
      ],
      "task_id": "TASK_FEE_REMOVE_REUSE_BUTTONS_20260930"
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_REFERENCE_20260915_RULE_OPTIMIZATION",
    "tier": "standard",
    "subject": "14e522976833ddfbc71d8d6d7e9a44856a567ecc",
    "summary": "Upgrade Fee Evaluation pricing reference and improve confirmed Matrix quantity and rule matching",
    "disposition": "completed",
    "decision_ref": "User explicit final close request in side conversation on 2026-09-30.",
    "closed_at": "2026-09-29T22:52:45.287224Z"
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
