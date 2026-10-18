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
    "updated_at": "2026-10-18T00:10:29.365032Z",
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
      "subject": "ae8f8fcef70c716940cf0ebfd4996786bc5d9624",
      "summary": "Prior compact widths,80percent charts, precision and Word placement refinements retained. Latest feedback moves both linked T-rise equation labels close to white plot upper-left, x.11/y.10,.20, with left-aligned equation and R2 lines.11pt fonts/colors/full formula content/live links remain unchanged. Native baseline and flat nonzero-intercept cases verify separated label boxes, full visibility and curve clearance. No numerical/API/UI/source/Word-authority changes; local only.",
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
          "detail": "Same standard task automatically revised for user equation overlap feedback. Minimal plan: move labels near white plot top-left, left-align full equations/R2, preserve size/fonts/live references; test exported contract and inspect rising/nonzero-intercept native cases. Direct fixed-anchor evidence allows bounded layout fix rather than broad diagnostic instrumentation."
        },
        "developer": {
          "status": "passed",
          "detail": "Main context existing export regression extended to both intercept modes;2RED then2GREEN at public saved-XLSX seam. Production change only label paragraph alignment and normalized anchors. Native label heights exposed overly tight initial y.18; refined to y.20 with2pt separation, original fonts retained."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate same-agent Standards and Spec exact-diff passes,0remaining findings each. No calculations/formula strings/chart series/axis format/Word dimensions changed. Helper defaultTrue preserves all existing fixture behavior, addedFalse coverage; supported label placement contract tested relative to plot rather than private source text. No new abstractions."
        },
        "qa": {
          "status": "passed",
          "detail": "Final46gateway tests passed. Native Excel2cases verified alignment, complete labels, chart bounds, disjoint boxes and11pt fonts; refreshed actual PNGs visually inspected. Final nonzero image hash matches reviewed artifact. No frontend/API or Word rerun because this edit only moves text within unchanged chart bounds."
        },
        "integrator": {
          "status": "passed",
          "detail": "Verified clean local masterae8f8fcef70c716940cf0ebfd4996786bc5d9624, latest3product/test/docpaths plus sole-writer board checkpoint, exact22cumulative paths. Validation matches final code; no remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at cleanae8f8fcef70c716940cf0ebfd4996786bc5d9624. Final46tests and native2case label geometry/visual evidence; exact22cumulative paths. Acceptance record through sole writer follows, no remote refs changed."
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
