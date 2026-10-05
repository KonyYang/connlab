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
    "task_id": "TASK_RISE_CHART_LABELS_20261005",
    "summary": "Align T-riseChart panes and linked full curve labels with reference",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove T-riseChart frozen panes, link curve/equation names to column A and position bold colored labels at upper left; retain calculations and other sheets",
    "scope_paths": [
      "backend/infrastructure/office/temperature_rise_report_sheet.py",
      "tests/unit/test_temperature_workbook_gateway.py",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "be2c5e699449a85eb99c3752c22afe80320b3809",
    "started_at": "2026-10-05T08:45:40.816466Z",
    "updated_at": "2026-10-05T09:43:35.255373Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_RISE_CHART_LABELS_20261005",
      "stage": "revision",
      "status": "running",
      "summary": "User requests reference-style Derating chart and no frozen A column; preserve calculations and previous T-rise refinements.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_RISE_DERATING_20261004",
    "tier": "standard",
    "subject": "0bcfe3009fe00a22ef8c9cf773777a644d2cf657",
    "summary": "Temperature rise and Derating tool with confirmed data preparation and native Excel charts",
    "disposition": "completed",
    "decision_ref": "User accepted the completed temperature-rise and report-ready Excel work and explicitly requested task closure on 2026-10-04.",
    "closed_at": "2026-10-04T06:55:34.579747Z"
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
