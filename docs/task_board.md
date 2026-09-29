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
  "state": "running",
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
    "updated_at": "2026-09-29T09:59:15.465452Z",
    "checkpoint": null,
    "report": null
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
