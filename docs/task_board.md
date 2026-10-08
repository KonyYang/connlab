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
    "updated_at": "2026-10-08T11:21:18.971625Z",
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
      "changed_paths": [
        "frontend/src/pages/ToolsPage.test.tsx",
        "frontend/src/pages/ToolsPage.tsx",
        "frontend/src/tools.css"
      ],
      "integration": {
        "subject": "2114210d924dc43176635a1ae3a2501941ed533c",
        "branch": "master",
        "publication": "not requested",
        "status": "passed"
      },
      "scope_ok": true,
      "schema": "connlab.sol-task-report",
      "version": 1,
      "subject": "2114210d924dc43176635a1ae3a2501941ed533c",
      "summary": "Select Internal Report is now the title above a content-width Generate Customer Report button; existing single-picker automatic generation workflow retained.",
      "validation": [
        {
          "result": "11 tests passed on final state; RED first failed for missing source heading, then GREEN verifies title before short button, chooser and cancellation",
          "command": "npm run test -- src/pages/ToolsPage.test.tsx",
          "status": "passed"
        },
        {
          "result": "TypeScript and Vite production build passed on final state",
          "command": "npm run build",
          "status": "passed"
        },
        {
          "result": "Title above content-width button visually verified in temporary Tools tab; screenshot saved; user tab untouched",
          "command": "In-app browser layout check",
          "status": "passed"
        },
        {
          "result": "No whitespace errors",
          "command": "git diff --check",
          "status": "passed"
        }
      ],
      "roles": {
        "developer": {
          "review": "Same-agent Standards and Spec passes on exact revision diff: zero findings in each. Scoped CSS changes only customer report picker button; other tools and APIs unchanged.",
          "status": "passed"
        }
      },
      "task_id": "TASK_TOOLS_CUSTOMER_REPORT_SINGLE_ACTION_20261008"
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
