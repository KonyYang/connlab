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
    "task_id": "TASK_MATRIX_SECTION_COLUMN_WIDTH",
    "summary": "Widen the Matrix Editor Section column so its header stays on one line.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Increase the existing Section column width in the Matrix Editor main table just enough for the Section header to remain on one line at narrow viewport widths; preserve cell content, editing behavior, and all other columns.",
    "scope_paths": [
      "frontend/src/workbench.css"
    ],
    "risk_reasons": [],
    "activation_head": "37bd8a6d6ef4e5b01f18e302e25383b6a351f3a2",
    "started_at": "2026-09-27T02:14:40.461812Z",
    "updated_at": "2026-09-27T02:19:01.765679Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_SECTION_COLUMN_WIDTH",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_SECTION_COLUMN_WIDTH",
      "subject": "e95575dc90a23c557500ad6810a5a2cacd8e1981",
      "summary": "Widened the Matrix Editor Section column from 48px to 64px so the header remains on one line, with other table behavior unchanged.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/workbench.css"
      ],
      "validation": [
        {
          "status": "passed",
          "summary": "Browser visual/DOM check at 654px viewport: Section header text rendered on one line in a 64px column."
        },
        {
          "status": "passed",
          "summary": "npm.cmd run build"
        },
        {
          "status": "passed",
          "summary": "git diff --check"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Reviewed the exact CSS diff; both duplicated main-table column-width rules now use 64px."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "direct_primary",
        "summary": "Committed the verified change as e95575dc90a23c557500ad6810a5a2cacd8e1981."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_SCHEDULE_COMPACT_HEADER",
    "tier": "micro",
    "subject": "38fc4aca6a63f7b156191de666237d492e1db257",
    "summary": "Reduce Project Schedule card height by putting its title and four editable controls on one desktop row, and enlarge the title to match Test points.",
    "disposition": "completed",
    "decision_ref": "User final response: 关闭 (2026-09-27)",
    "closed_at": "2026-09-27T02:11:24.372783Z"
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
