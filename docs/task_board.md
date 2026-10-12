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
    "task_id": "TASK_TEMPERATURE_COMPACT_MANUAL_INFO_20261013",
    "summary": "Simplify temperature Test Info to compact manual entry without project association",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove temperature tool project selection and lookups, preserve manual export metadata and source suggestions, compact inline responsive Test Info fields",
    "scope_paths": [
      "frontend/src/features/temperature/TestInfo.tsx",
      "frontend/src/features/temperature/useTemperatureReportInfo.ts",
      "frontend/src/features/temperature/useTemperatureTool.ts",
      "frontend/src/features/temperature/temperature.css",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "287bb7a2bd92400ce7510f6fbc28fe47fa748e24",
    "started_at": "2026-10-12T22:34:10.482463Z",
    "updated_at": "2026-10-12T23:19:14.761404Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_COMPACT_MANUAL_INFO_20261013",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "subject": "386280e9129aef94f306b5747cf45da860b732ed",
      "changed_paths": [
        "docs/temperature_rise_tool.md",
        "frontend/src/features/temperature/TestInfo.tsx",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureReportInfo.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx"
      ],
      "validation": [
        {
          "name": "Final affected frontend regression",
          "status": "passed",
          "detail": "58 tests across page, report metadata and API on final code; RED/GREEN hidden humidity, numeric 50 export, retained original ambient selection/readings and defaults across reimport verified"
        },
        {
          "name": "Final TypeScript and Vite build",
          "status": "passed"
        },
        {
          "name": "Independent Edge browser smoke",
          "status": "passed",
          "detail": "Six editable fields, no ambient/humidity inputs or heading/collapse; 7 viewport widths including 721px, no overflow/page errors; narrow editor reduced to three rows"
        },
        {
          "name": "Exact revised diff review",
          "status": "passed",
          "detail": "Sequential same-agent Standards 0 findings, Spec 0 findings; fixed values limited to report metadata, no source/calculation/authority mutation; git diff --check passed"
        }
      ],
      "task_id": "TASK_TEMPERATURE_COMPACT_MANUAL_INFO_20261013",
      "roles": {
        "developer": {
          "detail": "Micro implementation and self-review by current agent, no independent role claim",
          "status": "passed"
        }
      },
      "summary": "Six compact manual report fields, no project selector or heading/collapse; ambient and humidity inputs hidden, exported report defaults 23 C and numeric 50 percent RH without altering calculation data.",
      "integration": {
        "detail": "Clean local master exact subject; no remote publication",
        "status": "passed"
      },
      "scope_ok": true,
      "version": 1,
      "schema": "connlab.sol-task-report"
    }
  },
  "last_closed": {
    "task_id": "TASK_DRAFT_DOWNLOAD_AVAILABLE_INFO_20261012",
    "tier": "standard",
    "subject": "94286484b58dbd880af04fcf4b6fcc76ebf7be99",
    "summary": "Populate available project information in draft downloads without authority writeback",
    "disposition": "completed",
    "decision_ref": "User accepted completed draft download information changes and requested close on 2026-10-13",
    "closed_at": "2026-10-12T22:24:54.882393Z"
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
