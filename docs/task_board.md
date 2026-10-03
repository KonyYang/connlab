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
    "task_id": "TASK_TEMPERATURE_RISE_TOOL_20261003",
    "summary": "Standalone temperature rise and derating import preview and workbook tool",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Independent Tools workflow, read-only uploads, full precision calculation and new workbook output",
    "scope_paths": [
      "backend/modules/temperature_rise",
      "backend/application/tools_temperature_rise_service.py",
      "backend/infrastructure/office/temperature_rise_workbook_gateway.py",
      "backend/api/routes_tools.py",
      "backend/api/dependencies.py",
      "frontend/src",
      "tests"
    ],
    "risk_reasons": [],
    "activation_head": "184cdfe4e2101d183f44780c964f9d6bc0fcc1ee",
    "started_at": "2026-10-03T16:20:35.945809Z",
    "updated_at": "2026-10-03T16:20:35.945809Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_TOOLS_CONCISE_UI_20261003",
    "tier": "micro",
    "subject": "ca1b1dcb49af57973822820397646c7c98da8607",
    "summary": "精简 Tools 页面重复说明和正常状态信息",
    "disposition": "completed",
    "decision_ref": "User final close: 关闭任务",
    "closed_at": "2026-10-03T16:04:56.626365Z"
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
