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
    "task_id": "TASK_TEMPERATURE_AUTO_DATA_REGION_20261005",
    "summary": "Auto-detect scanner data region and show row settings only for detection exceptions",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Hide header/first/last row inputs on successful scanner-region detection; preserve source and ambiguous/failed imports for manual correction with generation blocked until confirmation; retain channel, ambient/current and anomalous-row review.",
    "scope_paths": [
      "backend/application/temperature_data_preparation.py",
      "backend/application/tools_temperature_service.py",
      "backend/api/routes_tools_temperature.py",
      "frontend/src/api/temperature.ts",
      "frontend/src/features/temperature/useTemperatureTool.ts",
      "frontend/src/features/temperature/temperature.css",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/features/temperature/DataRegionCorrection.tsx",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/integration/test_tools_temperature_api.py",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/api/temperature.test.ts",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "5419b7d3883a6ab3ecfe78c32730e266ebca26c0",
    "started_at": "2026-10-05T14:37:57.566451Z",
    "updated_at": "2026-10-05T23:32:14.230202Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_AUTO_DATA_REGION_20261005",
      "stage": "revision",
      "status": "running",
      "summary": "User requested removing the duplicate Temperature Rise & Derating content heading, retaining the top title and Tools return control.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_TOOLS_RETURN_ICON_20261005",
    "tier": "micro",
    "subject": "effaf89ade660d3b6524f25f6221a4f4e4ce5b67",
    "summary": "Replace temperature tool text return with Tools title-bar icon",
    "disposition": "completed",
    "decision_ref": "User explicitly requested final closure after accepting the Tools return icon and Workspace Report navigation label refinements.",
    "closed_at": "2026-10-05T14:03:34.747734Z"
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
