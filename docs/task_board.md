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
    "updated_at": "2026-10-17T13:50:07.215435Z",
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
      "subject": "ca78b57cae6cc9584ca87c357199bbd7f2d1fb91",
      "summary": "Unified current precision0to4 and compact single-line header retained. Latest acceptance refinement doubles worksheet selector72to144px and ambient/current selectors64to128px, and moves dynamic TC/Sample immediately before Current Decimals. Numeric spinners, confirmation/calculation/export and narrow-window parameter-only scrolling unchanged. Local only; no publication.",
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
          "detail": "Final affected UI matrix55tests passed across TemperatureRisePage(50) and TopBar(5), followed sequentially by TypeScript/Vite production build on finalca78b57c. Existing header parameter test extended with TC/Sample immediately before Current Decimals assertion: RED before moving span then GREEN. No later production/test edits."
        },
        {
          "status": "passed",
          "detail": "Real isolated Edge imported owned three-sheet XLSX.1920x804 screenshot visually inspected: complete one-line header. Actual measured worksheet width144px and ambient/current128px each, exactly doubled from72/64/64. Parameter children order Ambient,Current,Samples,dynamic1TC/Sample,CurrentDecimals verified; wide group client=scroll1363(no overflow).890x804 group client337/content732 remains same row and horizontally scrolls, sheet/import controls fixed. Console0errors0warnings. Owned browser and verified QA server17060 closed without touching user sessions/data."
        },
        {
          "status": "passed",
          "detail": "Latest revision only changes selector sizing, summary position, regression assertion and documentation/sole-writer board. Numerical/API/export code unchanged: prior138affected frontend broad-suite evidence,145backend tests and native Excel recalculation retained for unchanged paths only, not reported as rerun."
        },
        {
          "status": "passed",
          "detail": "Separate sequential same-agent exact-diff Standards and Spec review0actionable findings each. Dynamic TC count unchanged, native controls/aria names/tooltips/focus and existing overflow preserved. No new state, dependency or path authority. git diff --check clean and cumulative20product/test/docpaths unchanged."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Main context automatically Revise same task for bounded acceptance feedback: double three selector widths using spare space, put TC/Sample before Current Decimals, preserve existing single-row overflow and business behavior."
        },
        "developer": {
          "status": "passed",
          "detail": "Small CSS/JSX change:72to144worksheet,64to128two column selectors, move existing dynamic summary span without changing expression. Public page test extended and observed RED/GREEN for summary order. No calculation handlers changed."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Sequential same-agent Standards and Spec review, not independent contexts. Standards0: minimal scoped existing CSS/JSX, no duplicated logic or new state. Spec0: exact2xwidths and requested dynamic summary order, single-row/narrow overflow retained; no unrelated behavior."
        },
        "qa": {
          "status": "passed",
          "detail": "Final55affected page/topbar tests and sequential production build passed exactca78b57c. Real Edge1920widths/order/nooverflow visually and geometrically verified,890horizontaloverflow retained;0consoleerrors. Prior unaffected calculation/export evidence retained, not rerun."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local masterca78b57cae6cc9584ca87c357199bbd7f2d1fb91 with exact cumulative20paths. Sole-writer acceptance record only afterward, no remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at cleanca78b57cae6cc9584ca87c357199bbd7f2d1fb91. Latest diff scoped to CSS widths, JSX span order, test and docs/board. No user data or remote refs changed."
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
