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
    "updated_at": "2026-10-17T13:36:05.299757Z",
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
      "subject": "577c7e000e8642b8f2b58d753c13d0b0af974ca2",
      "summary": "Unified current precision0to4(default0), raw data and manual exclusions preserved. Latest accepted layout places Ambient Column/Current Column/Samples/Current Decimals after Load Initial Data in same header line, with narrow64px column selectors and complete selected-source tooltips. Import and worksheet controls stay fixed; parameter group alone scrolls horizontally on constrained windows. No duplicate body parameter row. Footer confirm/download and all calculation contracts unchanged. Local only; no publication.",
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
          "detail": "Latest UI revision138tests passed across10affected frontend files, including temperature features/page/API, App and TopBar. Sequential TypeScript and Vite production build passed on final577c7e00. New rendered-page parameter-group test RED before implementation then GREEN; verifies header order, no duplicate body controls, column tooltips and Samples/Current Decimals edits used by calculation. No code/test changes after final matrix."
        },
        {
          "status": "passed",
          "detail": "Real isolated Edge imported owned three-sheet XLSX. At1280x804 all header controls visible on one row; screenshot inspected. At890x804 all parameter controls share top11px, column selects64px, spinners40px; parameter group409px client versus604px content scrolls rather than wrapping; Sheet/Load remain fixed. Complete selected source header tooltips verified. Scrolled group, used native Current Decimals ArrowUp0to1, clicked footer Confirm Data; both real charts generated,6included0excluded, Data Confirmed and Download enabled.890initial/scrolled screenshots inspected. At598x804 parameter overflow confined to129px container within viewport. Console0errors0warnings; owned browser and verified test server37320 stopped, no user sessions/data touched."
        },
        {
          "status": "passed",
          "detail": "Original numerical/export implementation unchanged in this UI refinement: prior145backend tests and native Excel full recalculation of actual0dp/1dp downloads retained for identical bytes, not rerun. Raw .0087/10.05 and explicit exclusions remain preserved."
        },
        {
          "status": "passed",
          "detail": "Exact revision self-reviewed in separate sequential Standards and Spec passes:0actionable findings each. Existing page-owned state/handlers and header portal reused; scoped compact input styles cover portal and fallback, accessible label/group and focus rings retained. Existing sheet/cancel/busy/role/group flows covered by affected suite. git diff --check clean; revision only page/test/CSS/tool docs and sole-writer board; cumulative20product/test/docpaths."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Same main context standard task automatically revised for requested single-line header refinement; shrink column selectors, preserve labels and data behavior, use parameter-only horizontal overflow when physically constrained. No extra scope, new task or approval ceremony."
        },
        "developer": {
          "status": "passed",
          "detail": "Original numerical TDD retained. Latest public rendered-page TDD RED/GREEN verifies moving all parameter controls after import in header, eliminating duplicate body controls, full source tooltips, and outgoing edited sample count/current precision. No new state or API changes."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate same-agent Standards and Spec exact-diff reviews, not independent agents. Standards0: scoped token CSS, existing portal/state/handlers, accessible group/labels/focus retained. Spec0: same-row right-of-import composition, narrowed selectors, full-name hover, no body row, confined horizontal overflow on small windows, calculation/confirmation unchanged. Absolute disk-path browser limitation remains previously disclosed."
        },
        "qa": {
          "status": "passed",
          "detail": "Separate main-context QA:138affected frontend tests and sequential build passed exact577c7e00; actual Edge1280/890/598 geometry, screenshots, native precision ArrowUp and live confirm/charts passed.0consoleerrors. Original145backend/nativeExcel evidence retained only for unchanged numerical/export bytes, not claimed rerun."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local master577c7e000e8642b8f2b58d753c13d0b0af974ca2; exact cumulative20paths unchanged. Sole-writer final acceptance update; no remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Local clean577c7e000e8642b8f2b58d753c13d0b0af974ca2 contains accepted current precision and single-row compact header refinements. No numerical/API/backend changes in latest revision, no user data mutation or remote refs changed."
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
