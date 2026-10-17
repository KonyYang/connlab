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
    "updated_at": "2026-10-17T14:00:11.112795Z",
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
      "subject": "f8d4957ec6dd36f7c4414d3603c53de3675498dd",
      "summary": "Current precision and accepted compact header/footer refinements retained. Latest feedback replaces sample/channel summary beside Data Preview heading with live Included/Excluded row counts, removes duplicate below-table footer, and preserves exclude/restore/undo and grouping warnings. Local only; no publication.",
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
          "status": "passed",
          "detail": "Final affected frontend matrix139tests passed across10files covering temperature feature/page/API, App and TopBar. Sequential TypeScript/Vite production build passed exactf8d4957e. New public DataPreview regression RED before relocation then GREEN, proves unique title-adjacent count and exclude/selected-row-restore/undo updates.3old removed-summary assertions updated to existing grouping accessibility/topbar parameters, not discarded."
        },
        {
          "status": "passed",
          "detail": "Real isolated Edge imported owned six-row workbook at873x804. Screenshot visually inspected: Data Preview followed by6Included/0ExcludedRows, no sample/channel summary and no bottom count. DOM verified countCopies1 and oldSummaryfalse. Actual selected-row exclude changes to5/1; reselect excluded row and Restore returns6/0. Console0errors0warnings. Owned browser and verified test server45184 stopped; no user browser or data touched."
        },
        {
          "status": "passed",
          "detail": "No numerical/API/Excel changes in latest display refinement. Retained prior145backend tests and native Excel full recalculation for identical numerical/export bytes; not rerun. Explicit exclusions and existing count expression unchanged."
        },
        {
          "status": "passed",
          "detail": "Same-agent sequential Standards/Spec exact-diff reviews0actionable findings each. Removed unused sample-count projection/import and dead footer CSS only; grouping validation/header descriptions and controls unchanged. git diff --check clean. Latest6paths are DataPreview.tsx/test, page test, CSS, tool docs, sole-writer board; cumulative22product/test/docpaths verified."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Main context automatically revised same standard task for acceptance feedback: move existing row-count projection next to Data Preview title, remove old sample/channel caption and duplicate footer, preserve editing/grouping behavior."
        },
        "developer": {
          "status": "passed",
          "detail": "Public DataPreview seam regression observed RED/GREEN. Row count expression moved unchanged; excluded rows remain selected/restored through original grid workflow, undo covered. Removed obsolete sampleCount/import and footer-only styles. Adjusted removed-caption tests to actual surviving grouping controls/descriptions."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate sequential same-agent Standards and Spec passes, not independent agents. Standards0: minimal existing-state projection, no new state/dependency or business changes, dead CSS removed after checking all references. Spec0: title-right unique count, no duplicate footer, live exclude/restore/undo, grouping warnings preserved."
        },
        "qa": {
          "status": "passed",
          "detail": "Separate main-context QA139affected frontend tests and sequential production build passed exactf8d4957e. Real Edge873 title/counter uniqueness and6/0to5/1to6/0 exclude/restore passed;0consoleerrors. Prior numerical/Office checks retained only for unchanged code, not claimed rerun."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local masterf8d4957ec6dd36f7c4414d3603c53de3675498dd; cumulative22product/test/docpaths verified, including two newly affected DataPreview files within existing feature scope. Sole-writer acceptance update only; no publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Local cleanf8d4957ec6dd36f7c4414d3603c53de3675498dd integrates row-count placement and prior accepted refinements. Exact22cumulative paths; no user data or remote refs changed."
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
