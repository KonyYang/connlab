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
    "updated_at": "2026-10-17T12:15:06.439761Z",
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
      "subject": "8ebe96507acd65bebb38381f9fb5f7d89c87d1bd",
      "summary": "Unified current precision0to4(default0), raw data and exclusions preserved; compact source and footer confirmation retained. Latest acceptance refinement removes visible Sheet Name label and places accessible worksheet selector immediately before Load Initial Data in header, with complete filename hover and unchanged sheet reload/reconfirmation. Browser absolute disk path remains unavailable, disclosed previously. Local only; no publication.",
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
          "detail": "Latest UI revision:137tests passed across10affected frontend files including temperature feature/page/API, App and TopBar. Sequential TypeScript and Vite production build passed on exact final source8ebe9650. New header-sheet-switch test RED before implementation then GREEN afterward; no code/test edits after final matrix.",
          "status": "passed"
        },
        {
          "detail": "Real isolated Edge imported owned three-sheet XLSX. At717x804 and598x804, header worksheet select precedes Load Initial Data, no visible Sheet Name text, complete filename title retained. At598 select bounds340.953..436.625 and load444.625..571 do not overlap. Confirmed real data, then switched Sheet1 toSheet2; Sheet2 selected, charts cleared,6included0excluded, Confirm Data enabled and Download disabled. Screenshots inspected. Console0errors0warnings. Owned browser and verified QA server38620 closed; no user sessions/data touched.",
          "status": "passed"
        },
        {
          "detail": "Original numerical/export implementation unchanged by layout refinements: prior145backend tests and native Excel full recalculation of actual0dp/1dp downloads remain applicable. Raw .0087/10.05 preserved; no repeated unaffected numerical or Office matrix.",
          "status": "passed"
        },
        {
          "detail": "Separate same-agent exact-diff Standards and Spec reviews found0actionable findings. CSS applies in both portalled header and standalone fallback; aria-label retains accessible name without visible copy; sheet import/confirmation handlers reused without new state/dependency/path authority. git diff --check clean; revision touches only page/test/CSS/tool doc plus sole-writer board, cumulative20product/test/docpaths.",
          "status": "passed"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Same main context standard plan and automatic Revise for bounded acceptance feedback: move existing sheet selector, remove visible label, preserve hover and reload/confirmation. No new task or routine approval."
        },
        "developer": {
          "status": "passed",
          "detail": "Original precision TDD retained. Latest public rendered-page TDD RED/GREEN proves header portal location/order, hidden visible label, filename tooltip, and sheet change invalidates confirmed results. Existing selection and load state reused."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate sequential same-agent Standards and Spec passes, not independent contexts. Standards0 and Spec0 actionable findings. Existing portal composition and scoped token CSS retained; no new business/state/authority. Previously disclosed disk absolute-path limitation remains unchanged."
        },
        "qa": {
          "status": "passed",
          "detail": "Separate QA in main context:137affected frontend tests and sequential production build passed on final8ebe9650; real Edge717/598 and actual three-sheet import/confirm/switch flow passed, console0errors. Original145backend/nativeExcel checks retained only for unchanged numerical/export code, not reported as rerun."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local master8ebe96507acd65bebb38381f9fb5f7d89c87d1bd, cumulative20paths verified. Sole-writer acceptance update; no remote push or publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at exact clean8ebe96507acd65bebb38381f9fb5f7d89c87d1bd. Same task revisions; exact cumulative20paths. No user data, authoritative external files or remote refs changed."
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
