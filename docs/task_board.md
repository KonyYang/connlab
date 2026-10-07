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
    "updated_at": "2026-10-07T11:29:27.919100Z",
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
      "subject": "d90e0d059006d6e91144f2951267d7fc37d0a456",
      "summary": "Unified continuous temperature editor with compact fixed scan/time indexes and independent whole-row highlighting.",
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
          "name": "Final affected frontend QA",
          "result": "35 editor/page/API/TopBar tests passed; TypeScript and Vite build passed sequentially after final source/test edits. Page fixtures now retain the same workflow assertions using A scan and B time."
        },
        {
          "status": "passed",
          "name": "Isolated browser QA",
          "result": "Disposable 19999-data-row CSV: Original Row and A/B column controls absent; A/B positions fixed after horizontal scroll; compact column widths verified; cell clicks highlight without batch selection; Shift 2 to 10 selects nine rows; exclude and Undo verified; 543px page width contained; logs zero; viewport reset and QA tab closed."
        },
        {
          "status": "passed",
          "name": "Scope and source preservation",
          "result": "git diff --check passed; this revision does not change backend, fitting, workbook export or original source data; user draft tab untouched."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "execution": "Same-agent TDD RED/GREEN: three new index/highlight regressions and updated excluded-row assertion failed before implementation; final 14 grid cases pass."
        },
        "reviewer": {
          "status": "passed",
          "execution": "Separate same-agent Standards and Spec exact-diff passes; zero outstanding findings; not independent-agent review."
        },
        "qa": {
          "status": "passed",
          "execution": "Same-agent final affected test/build and isolated browser QA."
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "subject": "d90e0d059006d6e91144f2951267d7fc37d0a456",
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
