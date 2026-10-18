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
    "updated_at": "2026-10-18T00:42:20.979037Z",
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
      "subject": "2bd164ff1c9a1106cbd066a551e6d9503d11c2fe",
      "summary": "Prior precision, Excel and compact card refinements retained. Latest feedback hides only the web temperature-rise plot visible duplicate title. Card heading, SVG accessible title/name, axes, traces, all calculations and web Derating title retained; backend/native Excel chart title unchanged.",
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
          "detail": "Final51page tests passed in15.46s; TypeScript/Vite build passed; exact diff clean. Real browser SVG visible texts omit only internal title, retain current/temperature axes and2fit curves; accessible name unchanged; screenshot inspected. No backend edits or new implementation-mirroring tests for presentation-only fix."
        },
        {
          "status": "passed",
          "detail": "Latest exact state:56 page/topbar tests passed in22.75s; TypeScript and Vite production build passed. Initial5 failures identified duplicate banner semantics from card header tags, fixed using neutral div containers; all56 now green. Real browser current873px,1920px,598px,400px checks: no card/header overflow, wide controls one row, narrow complete readable labels; viewport reset. Same-agent Standards0/Spec0 findings. No new implementation-mirroring tests for presentation-only changes."
        },
        {
          "status": "passed",
          "detail": "Final cleanae8f8fce:46Excel gateway tests passed in8.16s; git diff --check clean; no code/test edits afterward. Existing equation/name linkage regression extended to zero-interceptTrue/False, checks placement relative to plot left/top and all paragraphs left-aligned.2RED before layout move then2GREEN. Numerical, native chart, precision, source preservation and dimensions regressions retained."
        },
        {
          "status": "passed",
          "detail": "Native isolated Excel original rising baseline plus synthetic flat nonzero-intercept data resembling user screenshot. CalculateFullRebuild, actual linked labels verified left-aligned, inside left boundary, full width in chart, nonoverlapping bounding boxes. Left54.6205pt; top27.7480/59.4961pt, height29.86pt, separation1.888pt;11pt unchanged. Nonzero full equation widths241.490/345.945pt remain inside18.8cm chart. Linked texts include intercepts and completeR2."
        },
        {
          "status": "passed",
          "detail": "Actual refreshed Excel PNGs inspected for baseline and flat nonzero-intercept cases: equations/R2 left-aligned at white top-left and blue formula clear of fit; axes/title/legend complete. Final nonzero PNG SHA256FE2F5199D6A16A2B7D6770F19AA873A80AF617E80109BACE4CE775BC089D7178 identical to reviewed preview. QA refresh avoids transient missing tick labels in background Excel export; no production axis changes. Owned instance closed without saving, no clipboard used."
        },
        {
          "status": "passed",
          "detail": "Developer native-box check found initially too-tight label shape spacing at y.18 despite visible ink; bounded y.20 refinement preserves top-left placement and gives disjoint rectangles. No speculative collision engine or font reduction introduced. Exact latest3product/test/docpaths reviewed: Standards0findings and Spec0findings in separate same-agent passes, not independent agents.22cumulative paths."
        },
        {
          "status": "passed",
          "detail": "Chart dimensions/fonts/Word widths unchanged; prior45gateway/nativeExcel/Word-image placement checks retained for unaffected paths. Earlier43API/56frontend/build not rerun for label-placement-only change. Prior EMF clipboard automation limitation unchanged and not represented as passed. No user report/template/workbook modified."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "In-scope same-task revision: hide web rise title only; preserve Excel titles."
        },
        "developer": {
          "status": "passed",
          "detail": "Existing shared chart adds showTitle defaultTrue; only RiseChart passesFalse. No data, geometry, ARIA or export changes."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Same-agent separate Standards and Spec passes:0findings; optional display parameter has present use; default preserves Derating. No independent review claimed."
        },
        "qa": {
          "status": "passed",
          "detail": "Final51page tests/build passed; live DOM and screenshot show no visible internal rise title and unchanged axes/curves/accessibility. Backend not rerun for frontend-only edit."
        },
        "integrator": {
          "status": "passed",
          "detail": "Verified clean exact local subject,22cumulative paths; no remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Local clean master includes exact reviewed frontend display change; no push."
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
