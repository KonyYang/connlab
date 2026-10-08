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
    "task_id": "TASK_TOOLS_CUSTOMER_REPORT_SINGLE_ACTION_20261008",
    "summary": "Use one file-picker action to generate a customer report in Tools",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Customer report card only: one visible button opens file chooser and selecting a file immediately runs existing conversion; preserve cancellation, progress, error, download, and other tools",
    "scope_paths": [
      "frontend/src/pages/ToolsPage.tsx",
      "frontend/src/pages/ToolsPage.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "d11e507e111e8de817faacce2268f09d0daad8f3",
    "started_at": "2026-10-08T10:53:22.399537Z",
    "updated_at": "2026-10-08T11:18:06.879843Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TOOLS_CUSTOMER_REPORT_SINGLE_ACTION_20261008",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "task_id": "TASK_TOOLS_CUSTOMER_REPORT_SINGLE_ACTION_20261008",
      "integration": {
        "status": "passed",
        "subject": "2f5b95d9d859ce9bd080f8f34e506106d5b65927",
        "branch": "master",
        "publication": "not requested"
      },
      "scope_ok": true,
      "version": 1,
      "validation": [
        {
          "status": "passed",
          "command": "npm run test -- src/pages/ToolsPage.test.tsx",
          "result": "All 11 tests passed on final revised state, including labelled button opens picker, cancellation, automatic conversion, retry, progress and unmount protection"
        },
        {
          "status": "passed",
          "command": "git diff --check",
          "result": "No whitespace errors; current revision changes only one button literal and two matching test expectations"
        }
      ],
      "roles": {
        "developer": {
          "review": "Same-agent exact revision diff review: requirement and standards satisfied; no findings. Prior implementation reviewed separately. Copy-only revision needs no additional build or browser matrix.",
          "status": "passed"
        }
      },
      "subject": "2f5b95d9d859ce9bd080f8f34e506106d5b65927",
      "summary": "One-button customer report workflow retained; button now explicitly says Select Internal Report → Generate Customer Report.",
      "changed_paths": [
        "frontend/src/pages/ToolsPage.test.tsx",
        "frontend/src/pages/ToolsPage.tsx"
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_CURRENT_MAX_STYLE_20261008",
    "tier": "micro",
    "subject": "67cbe7fa6a329299a67917d7a86afefbabb6a2b8",
    "summary": "Match calculated current color to Max curve and use bold text",
    "disposition": "completed",
    "decision_ref": "User final authorization: 关闭任务",
    "closed_at": "2026-10-08T00:00:46.691359Z"
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
