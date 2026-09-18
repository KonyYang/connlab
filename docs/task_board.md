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
    "task_id": "TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT",
    "summary": "Align the supported test runner with the ConnLab Python virtual environment and retire stale broad environment-debt assumptions.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Update only the test runner, its focused contract test, and the task board. Preserve normal versus Office test separation; do not change product code, dependencies, or host safe-delete policy.",
    "scope_paths": [
      "scripts/run_tests.ps1",
      "tests/unit/test_packaging_notes.py",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "867a155540148e372bc06a0f96ebf500cda84850",
    "started_at": "2026-09-18T15:01:17.305336Z",
    "updated_at": "2026-09-18T15:18:39.393237Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT",
      "subject": "ad0cbb757b4fa5f5549dcfb6746d7f20ed6528f3",
      "summary": "Aligned the supported Python test runner with the ConnLab virtual environment while preserving Office opt-in separation.",
      "scope_ok": true,
      "changed_paths": [
        "scripts/run_tests.ps1",
        "tests/unit/test_packaging_notes.py"
      ],
      "validation": [
        {
          "name": "focused script contracts",
          "status": "passed",
          "result": "6 passed"
        },
        {
          "name": "PowerShell syntax",
          "status": "passed"
        },
        {
          "name": "complete non-Office Python gate",
          "status": "passed",
          "result": "2954 passed, 7 skipped, 19 deselected"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented, self-reviewed, and validated the bounded test-entry repair."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "isolated_worktree_pending_primary_integration"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_361C_TMP_DISK_GOVERNANCE_INVENTORY",
    "tier": "standard",
    "subject": "Scan tmp/ and produce 26.75 GB disk-governance inventory",
    "summary": "Read-only scan of D:/PythonProject/connlab/tmp categorized 768 entries into repo_copy (16.12 GB), task_evidence (5.18 GB), pytest_artifact (820 MB), other (4.64 GB). No files deleted; report awaits user confirmation per batch.",
    "disposition": "completed",
    "decision_ref": "User requested execute recommended sequence on 2026-09-18; report-only, delete-after-confirm boundary preserved.",
    "closed_at": "2026-09-18T03:30:00.000000Z"
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
