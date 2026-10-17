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
    "task_id": "TASK_TEMPERATURE_CURRENT_DECIMALS_20261017",
    "summary": "Unified current decimal precision for temperature zero detection calculations charts and Excel export",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Add0to4 integer current decimal spinner after Samples default0; decimal half-up quantization for current zero detection/calculation and consistent current display/export; preserve original imported data and included rows/sample roles; no unrelated identity/project changes or external authoritative file writes.",
    "scope_paths": [
      "backend/domain/temperature_data.py",
      "backend/application/temperature_data_preparation.py",
      "backend/api/temperature_schemas.py",
      "backend/infrastructure/office/temperature_workbook_gateway.py",
      "backend/infrastructure/office/temperature_rise_report_sheet.py",
      "frontend/src/api/temperature.ts",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/features/temperature",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/unit/test_temperature_workbook_gateway.py",
      "tests/integration/test_tools_temperature_api.py",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "4219ddb74e8bb009d370757e415daed45b0f1e85",
    "started_at": "2026-10-17T03:04:29.050372Z",
    "updated_at": "2026-10-17T23:36:08.720471Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_CURRENT_DECIMALS_20261017",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_CURRENT_DECIMALS_20261017",
      "subject": "68effc6a1ae6f873d7edb9e525ade03d00512485",
      "summary": "Prior current precision and compact header refinements retained. Latest export feedback adds solidFFFF00yellow only to copied KeyStageReadings data cells in T-riseChart, matching Initial Data selected endpoint rows. Grey header, lower calculated table, spacer rows, values, formulas, formats and native objects unchanged. Source attachment read-only and SHA256 preserved. Local only.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/temperature_schemas.py",
        "backend/application/temperature_channel_layout.py",
        "backend/application/temperature_data_preparation.py",
        "backend/domain/temperature_data.py",
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/DataPreview.test.tsx",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/TemperatureCharts.tsx",
        "frontend/src/features/temperature/currentPrecision.test.ts",
        "frontend/src/features/temperature/currentPrecision.ts",
        "frontend/src/features/temperature/sourceScan.test.ts",
        "frontend/src/features/temperature/sourceScan.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "validation": [
        {
          "detail": "Final clean68effc6a:85tests passed across Excel gateway unit tests and temperature Tools API integration tests in13.86s. One pre-existing Starlette/httpx deprecation warning. Initial sandbox run completed42gateway tests then stalled entering API tests and was interrupted; complete identical suite passed in escalated environment. No implementation/test changes afterward.",
          "status": "passed"
        },
        {
          "detail": "Public export seam TDD: new test failed before fill change then passed. It asserts every copied data cell solidFFFF00, grey header retained, lower calculation data/spacer not recolored. Existing suite verifies source preservation, raw literals, formulas/caches, axes/precision, charts, export roundtrip and API downloads.",
          "status": "passed"
        },
        {
          "detail": "Generated owned baseline workbook via existing production gateway, imported read-only into bundled Artifact Tool and rendered T-riseChart A48:H65. Preview inspected: grey headers, all raw data rows yellow, blank gap and lower calculations unfilled; displayed values/format preserved. No direct attachment overwrite. Before/after attachmentSHA256 bb564c924b1f46850c249623efdb73f6a694075533eee0f3e3b0d9d9c8cc4705 identical. Native Excel recalculation not repeated for fill-only code; no formula changes.",
          "status": "passed"
        },
        {
          "detail": "Same-agent separate exact-diff Standards0findings and Spec0findings. Latest changes only existing infrastructure fill loop, public export regression and tool docs, plus sole-writer board.22cumulative paths. git diff --check clean. Prior56frontend tests/build/browser evidence retained for unchanged frontend; not rerun.",
          "status": "passed"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Automatically revised same standard task for bounded export formatting feedback. Plan: fill only copied raw reading data rows with sameyellow as Initial Data; preserve grey headers, calculation table, values/formulas/source. No new design or authority."
        },
        "developer": {
          "status": "passed",
          "detail": "Main context public gateway export TDD RED then GREEN. Existing key-readings cell-format loop now reuses one solidFFFF00fill; no domain/API/UI/caching changes. Added scoped regression and documentation."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate same-agent Standards and Spec exact-diff passes, not independent contexts. Standards0 and Spec0findings. Correct bounded row/column limits, all copied columns including identifiers and blanks filled; shared table styling unchanged so grey headers/calculation blocks unaffected. No new dependencies or abstractions."
        },
        "qa": {
          "status": "passed",
          "detail": "Final clean68effc6a passed85gateway/API tests. Sandbox API stall separately recorded; complete escalated rerun passed, one existing deprecation warning. Actual production-generated output rendered through bundled Artifact Tool; changed range visually inspected. Supplied file SHA preserved. No nativeExcel recalculation rerun for style-only change."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local master68effc6a1ae6f873d7edb9e525ade03d00512485 verified; exact22cumulative product/test/docpaths, latest3paths plus board checkpoint. No remote publication or external authoritative mutation."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at clean68effc6a1ae6f873d7edb9e525ade03d00512485. Latest3product/test/docpaths only;22cumulative. Sole-writer acceptance record follows; no remote refs changed."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_LEGACY_PROJECT_READONLY_PREVIEW_20261017",
    "tier": "standard",
    "subject": "49dccfbc781ce2cccf0ea84713225fc8f7d11806",
    "summary": "Tools legacy-project read-only batch preview with project boundaries, duplicate detection and conflict explanations",
    "disposition": "completed",
    "decision_ref": "User explicitly closes the completed task locally, retaining all local commits and forbidding push or publication.",
    "closed_at": "2026-10-17T02:16:20.299223Z"
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
