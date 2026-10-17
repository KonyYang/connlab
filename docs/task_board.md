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
    "updated_at": "2026-10-17T23:47:47.389736Z",
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
      "subject": "f7c113737cf75fff9427370b9ea76c72beb2138f",
      "summary": "Prior precision, compact UI and yellow copied-readings export retained. Latest Derating export removes generated title/subtitle; coefficients/max temperature A1:D2, ambient point/results F1:H2 and guide J1:K2 are horizontal; blocks and A5:C main table bordered/centered. Native chart moved fromE17 toE5. All affected formulas, caches, point and guide chart references relocated coherently. Source/other sheet content untouched. Local only.",
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
          "detail": "Final implementation0ef9c0cc passed86tests across43gateway unit and43Tools API integration tests,36.71s. One existing Starlette/httpx deprecation warning. Laterf7c11373 changes only historical documentation wording; backend/frontend/tests identical to QA implementation. git diff --check clean."
        },
        {
          "status": "passed",
          "detail": "Coherent public-export TDD slice: new layout test and relocated existing guide/precision checks4failed before implementation,4passed after. Final suite verifies bordered/centered blocks, removed old prose, chartE5 anchor, updated live formulas and caches,0/1decimal source-label precision, original data, native charts and downloads. No private function mocks."
        },
        {
          "status": "passed",
          "detail": "Isolated native Excel read-only open of owned production-generated workbook, CalculateFullRebuild and in-memory edits. Initial75C Basic68.3438319367/Derated54.6750655494 preserved. F2=80C yields61.4903910777/49.1923128622; guide endpoints and actual point/guide series follow. Then a multiplied1.1 and max110 yields65.6267043285/52.5013634628. First/middle/last main table formulas reconcile against independent domain calculations for each edit.0native formula errors; centered/bordered ranges and E5 chart actual geometry asserted. All edits closed without saving; owned Excel quit in finally."
        },
        {
          "status": "passed",
          "detail": "Owned native Excel exported one-page PDF after restoring initial inputs; bundled PDFium rasterized and visual image inspected. Coefficients, ambient summary, guide across top; left complete data table, right chart aligned atE5; no overlap, clipped headers or old title/subtitle. Existing curve colors/labels/legend preserved. No attached/source file overwritten. Intermediate preview remains ignored QA evidence, not a user deliverable."
        },
        {
          "status": "passed",
          "detail": "Separate same-agent exact-diff Standards0 and Spec0findings, not independent agents. Formatting remains workbook infrastructure; bounded style helper prevents generic title styling from overwriting parameter headers. All affected formula/caches/chart references moved, placeholder when no Derating remains usable, current formats retained. Exact22cumulative paths. Frontend unchanged: prior56tests/build/browser evidence retained, not rerun."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Same standard task revised automatically for current Derating presentation feedback. Chosen literal layout replaces title rows with A1:D2coefficients, F1:H2ambient results and J1:K2guide, keeps main tableA5 and moves chartE5. Preserve source data/calculations/precision; native recalculation required for moved dependencies."
        },
        "developer": {
          "status": "passed",
          "detail": "Main context public-export TDD coherent layout/reference slice4RED then4GREEN. Existing formula expressions and numerical model preserved; only references/caches/series source positions updated. Dedicated bounded formatting helper owns borders/centering/header styling; no new dependencies or UI changes."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate same-agent Standards and Spec exact-diff review. Standards0findings; Spec0findings. Scoped table fill/font/alignment bounds and fallback styling checked. Legacy G10/F13 references removed from live implementation and tests, all dependent point/guide references follow relocated inputs. No authority/source mutation or numerical redesign."
        },
        "qa": {
          "status": "passed",
          "detail": "Final implementation86gateway/API tests passed; native isolated Excel recalculation, ambient/coefficient/max-temp edit propagation through table/point/guide, formatting and chart geometry assertions passed;0formulaerrors. Native PDF preview inspected. Subsequent documentation-only clarification checked with unchanged implementation tree; no unnecessary frontend matrix repeated."
        },
        "integrator": {
          "status": "passed",
          "detail": "Verified clean local masterf7c113737cf75fff9427370b9ea76c72beb2138f and unchanged tested implementation tree from0ef9c0cc; exact22cumulative paths, latest3product/test/docpaths plus sole-writer checkpoint. No remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at cleanf7c113737cf75fff9427370b9ea76c72beb2138f; code/test validation from identical0ef9c0cc implementation tree, laterdocclarification only. Exact22cumulative paths. Acceptance record through sole writer follows; no remote refs changed."
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
