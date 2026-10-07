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
    "task_id": "TASK_TEMPERATURE_EXCEPTION_MAPPING_20261007",
    "summary": "Auto-group sample thermocouples and simplify exception-only channel adjustments",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Temperature tool import suggestions, channel exception editing, stable auxiliary current defaults and near-zero current review; preserve source files and confirmation.",
    "scope_paths": [
      "backend/application/temperature_data_preparation.py",
      "backend/application/tools_temperature_service.py",
      "backend/domain/temperature_data.py",
      "backend/api/temperature_schemas.py",
      "backend/api/routes_tools_temperature.py",
      "frontend/src/features/temperature",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/api/temperature.ts",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/integration/test_tools_temperature_api.py",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "83038fb2502d2d5d065737690455d1144cbac704",
    "started_at": "2026-10-06T22:53:34.408273Z",
    "updated_at": "2026-10-07T12:50:57.350772Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_EXCEPTION_MAPPING_20261007",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_EXCEPTION_MAPPING_20261007",
      "subject": "809d52aeebcbe8547d877dbc180cab52963dac2e",
      "summary": "Unit-aware compact preview delivered: right-click column operations, filtered role choices, display-only decimal formatting, dynamic widths and conflict guard. Existing unified editing and calculation precision preserved.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/temperature_channel_layout.py",
        "backend/application/temperature_data_preparation.py",
        "backend/application/tools_temperature_service.py",
        "backend/domain/temperature_data.py",
        "backend/domain/temperature_rise.py",
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "design-qa.md",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/ChannelMapping.tsx",
        "frontend/src/features/temperature/ColumnActions.tsx",
        "frontend/src/features/temperature/DataPreview.test.tsx",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/DataRegionCorrection.tsx",
        "frontend/src/features/temperature/sourceColumns.ts",
        "frontend/src/features/temperature/sourcePresentation.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useDataGridEditing.ts",
        "frontend/src/features/temperature/useSourceRowWindow.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py",
        "tests/unit/test_temperature_rise_calculations.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Final affected frontend matrix",
          "result": "39 tests passed: DataPreview 16, TemperatureRisePage 16, temperature API 2, TopBar 5; includes RED/GREEN regressions for right-click, clean rounded display, filtered exact-data submission and explicit-unit conflict."
        },
        {
          "status": "passed",
          "name": "TypeScript and Vite production build",
          "result": "npm run build passed sequentially after tests on final source/test state."
        },
        {
          "status": "passed",
          "name": "Isolated browser QA",
          "result": "Actual CSV: 403 rows, 31 temperature options, 4 current options. Native right-click block menu, Shift+F10 move and Undo passed. No data clipping; compact 56 px temperature columns. At 543x804 A/B stay fixed and popup/page fit. Zero warning/error logs. QA tab closed and viewport reset. Source SHA256 unchanged; User tab not operated."
        },
        {
          "status": "passed",
          "name": "Exact diff checks",
          "result": "git diff --check passed; same-agent Standards and Spec passes found zero outstanding findings. No backend, export numeric, dependency or source-file mutation changes in this revision."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "execution": "Same-agent Astra implementation with coherent TDD RED/GREEN slices; precision remains presentation-only."
        },
        "reviewer": {
          "status": "passed",
          "execution": "Separate same-agent Standards and Spec exact-diff passes, not independent-agent review; zero outstanding findings."
        },
        "qa": {
          "status": "passed",
          "execution": "Same-agent final 39-test matrix and sequential TypeScript/Vite build, then actual-CSV native browser and responsive checks."
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "subject": "809d52aeebcbe8547d877dbc180cab52963dac2e",
        "publication": "Local only; final Close not requested."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_AUTO_DATA_REGION_20261005",
    "tier": "standard",
    "subject": "caf291d79a6b45ce554a95b600691521f7f940a7",
    "summary": "Auto-detect scanner data region and show row settings only for detection exceptions",
    "disposition": "completed",
    "decision_ref": "User explicitly requested final closure after the accepted temperature import, CSV support and compact inline parameter refinements.",
    "closed_at": "2026-10-06T00:08:05.990507Z"
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
