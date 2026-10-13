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
    "updated_at": "2026-10-13T00:09:15.568202Z",
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
      "task_id": "TASK_TEMPERATURE_COMPACT_MANUAL_INFO_20261013",
      "subject": "22b4249410287335433e789cfb0d103cad35c551",
      "integration": {
        "status": "passed",
        "detail": "Clean local master exact subject; no remote publication"
      },
      "validation": [
        {
          "status": "passed",
          "detail": "Latest exact implementation: 98 frontend tests in TemperatureRisePage, reportInfo, temperature API, Sidebar and Basic Information workspace; RED proved blank default before implementation, GREEN verifies default and manual/cleared overrides through reimport/export"
        },
        {
          "status": "passed",
          "detail": "Latest exact implementation: sequential npm run build (TypeScript and Vite) and git diff --check passed"
        },
        {
          "status": "passed",
          "detail": "Prior task slices: 64 backend workbook/API tests and actual synthetic browser-download/native Excel verification for latest date and final blank Remark row; backend/export code unchanged by current-user adjustment, not rerun in this slice"
        }
      ],
      "schema": "connlab.sol-task-report",
      "changed_paths": [
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/currentUser.ts",
        "frontend/src/features/project-basic-information/currentUserDisplay.ts",
        "frontend/src/features/temperature/TestInfo.tsx",
        "frontend/src/features/temperature/reportInfo.test.ts",
        "frontend/src/features/temperature/reportInfo.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureReportInfo.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_tools_temperature_api.py"
      ],
      "summary": "Compact manual temperature metadata, fixed hidden report defaults, latest included source date, final Excel Remark row, and Tested By default shared with offline sidebar name; manual edits and clearing survive reimport and export",
      "scope_ok": true,
      "roles": {
        "developer": {
          "status": "passed",
          "detail": "Same-agent sequential Standards and Spec exact-diff reviews: zero outstanding findings. Shared static offline name remains Lab User; no authenticated profile or OS-user inference introduced. No independent review claimed."
        }
      },
      "version": 1
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
