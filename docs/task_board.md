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
    "updated_at": "2026-10-17T23:06:17.078334Z",
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
      "subject": "7904e7659476bccd082606d11fd9ab000094fe2d",
      "summary": "Previous current precision, compact header actions and single-line review feedback retained. Latest acceptance adjustment places worksheet selector immediately after Load Initial Data and before existing parameters; unchanged144px width, source filename hover, accessible label, load handler and reload/reconfirmation contract. Local only; no publication.",
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
          "detail": "Latest7904e765 final51page+5TopBar tests56passed, followed sequentially by TypeScript/Vite production build. No implementation or test changes afterward. git diff --check clean.",
          "status": "passed"
        },
        {
          "detail": "TDD existing worksheet switching public page test: new immediate Load-button-to-select adjacency assertion failed before the source move and passed afterward. Existing filename title, sheet reload, result invalidation and re-confirmation checks retained.",
          "status": "passed"
        },
        {
          "detail": "Real isolated Edge1920x804 and706x804 screenshots inspected. DOM order BUTTON then SELECT, button text Load Initial Data, selector144px and source filename title confirmed. Actual Confirm then Sheet2 switch reloaded6included0excluded and reset results/Download eligibility. Confirm and Download remain fixed top right. Console0errors0warnings. Own browser and verified server34204 closed; snapshots retained in ignored QA directory.",
          "status": "passed"
        },
        {
          "detail": "Same-agent separate Standards and Spec review of exact latest3product/test/docpaths: Standards0findings, Spec0findings. Source edit only moves existing button with handler unchanged; no CSS, API, business, data or Excel changes.22cumulative paths verified. Earlier matrix140frontend and145backend/nativeExcel evidence retained only for unchanged code, not rerun for this ordering change.",
          "status": "passed"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Latest in-scope feedback automatically revised same standard task. Minimal plan: swap import button and worksheet selector, update existing observable order regression test and tool documentation, preserve all other behavior."
        },
        "developer": {
          "status": "passed",
          "detail": "Main context moved existing button before conditional sheet selector without changing props, handlers or CSS. Existing worksheet-switch test updated to immediate adjacency; meaningful RED then GREEN recorded."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Main context separate sequential Standards and Spec exact-diff passes, not independent agents. Standards0findings; Spec0findings. No new state/dependency/abstraction, unrelated changes or numerical/file authority mutation."
        },
        "qa": {
          "status": "passed",
          "detail": "Final reviewed clean7904e765:56page/TopBar tests passed and sequential production build passed. Actual isolated Edge wide/narrow screenshots,144px width, filename title and sheet reload/reconfirmation inspected;0consoleerrors/warnings. Other numerical/Office validation retained unchanged, not rerun."
        },
        "integrator": {
          "status": "passed",
          "detail": "Verified clean local master7904e7659476bccd082606d11fd9ab000094fe2d, exact22cumulative paths and latest3product/test/docpaths plus sole-writer board checkpoint. No remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at clean7904e7659476bccd082606d11fd9ab000094fe2d. Latest source/test/docs order refinement only;22cumulative paths. Board acceptance record follows through sole writer, no remote refs changed."
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
