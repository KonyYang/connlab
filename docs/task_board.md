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
    "updated_at": "2026-10-18T00:02:02.545387Z",
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
      "subject": "c6964ddd17c83d05032e44912ac5936c9bcaea4a",
      "summary": "Prior numerical/current precision and compact export refinements retained. Latest feedback tightens Derating numeric/spacer columns, scales native T-riseChart23.5x14cm to18.8x11.2cm and Derating24x14cm to19.2x11.2cm, each80percent dimensions. Bottom plot clearance separates axis titles/legends without shrinking text. User clarifies Word is final destination: actual configured report section text widths18.034/19.05cm checked, proportional Word image insertion validated; vector clipboard automation unavailable, not claimed. No user workbook/report/template overwritten. Local only.",
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
          "detail": "Final implementation83bc62d0 passed45Excel gateway tests in7.16s. Laterc6964ddd only adds Word placement guidance; implementation/test tree unchanged, git diff --check clean. Earlier43Tools API and56frontend/build checks retained for unchanged interface/frontend; not rerun for presentation-only changes.",
          "status": "passed"
        },
        {
          "detail": "Saved-XLSX chart extent contract TDD:2RED at old dimensions then2GREEN. A1body styles/numerical exports unchanged. Height tolerance1EMU handles integer conversion truncation of11.2cm; no visual variance. Removed obsolete private75percentplot-height assertion that conflicted with needed bottom clearance; dimensions tested at exported file seam. No new tests freezing column literals for reversible width-only edits.",
          "status": "passed"
        },
        {
          "detail": "Native isolated Excel final-compact-export on83bc62d0: actual chart sizes18.8/19.2x11.2cm asserted in points; centered bordered blocks/E5anchor and precision preserved;0formulaerrors. Ambient80C yields61.4903910777/49.1923128622, editedcoefficient/max-temperature65.6267043285/52.5013634628; table/point/guide updates retained. Both actual exported chart PNGs inspected; full titles/equations/axes/legends readable. Earlier boundary preview corrected QA-only print-area width after column shrink, no production print settings changed. Owned Excel closed without saving inputs.",
          "status": "passed"
        },
        {
          "detail": "Read-only current template resource discovery found E-3707_H/E-4515_F with actual18.034/19.05cm text widths. Independent Word documents used that geometry, inserted owned chart images proportionally: two pages per width, no overflow;18.034cm worst-case rendered pages inspected for both charts and fully readable. Native EMF clipboard transfer NOT validated: OLE restore preflight failed before any chart copy, so no clipboard chart write attempted and safe image insertion used. No user Word/template modified; owned Office instances closed.",
          "status": "passed"
        },
        {
          "detail": "Separate same-agent exact-diff Standards0 and Spec0findings. Latest4product/test/docpaths only;22cumulative. Width overrides bounded to generated Derating; chart sizes/plot margins only, no formula/domain/API/UI changes. Current Word image-placement QA supports geometry/readability only, not a claim of vector clipboard compatibility. No new automatic Word assembly or hidden font fitting introduced.",
          "status": "passed"
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Same running standard task incorporates successive User acceptance refinements: compact Derating columns, both native chart dimensions80percent and readability before compactness, Word report placement constraint. Preserve formulas and avoid unrequested Word assembly; test actual configured report widths."
        },
        "developer": {
          "status": "passed",
          "detail": "Main context targeted width map and two chart dimension/layout changes. Exported-size2RED/2GREEN regression; bounded bottom clearance resolves observed title/legend crowding while fonts stay readable. No formula edits. Word section geometry researched read-only and transfer guidance documented; no delivered Word file authored."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate same-agent Standards and Spec exact-diff passes,0findings each, not independent agents. Checked generated Derating-only width scope, fixed anchors/precision, true80percent dimensions, retained complete native labels, removed obsolete private layout threshold, source/Word authority preservation and transparent QA limitation."
        },
        "qa": {
          "status": "passed",
          "detail": "Final45gateway tests and native Excel dimensions/recalculation/actual chart image inspection passed. Actual Word image insertion at18.034/19.05cm verified two pages per width; narrow rendered chart pages inspected. EMF clipboard test unavailable before copy due OLE preflight, not counted as passed; no unsafe clipboard workaround. Prior interface/frontend evidence retained unchanged."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local masterc6964ddd17c83d05032e44912ac5936c9bcaea4a verified, implementation identical to validated83bc62d0. Latest4product/test/docpaths, exact22cumulative paths; no remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at cleanc6964ddd17c83d05032e44912ac5936c9bcaea4a; final implementation45tests/nativeExcel, subsequent docs-only Word guidance and Word QA. Exact22cumulative paths; sole-writer acceptance follows. No remote refs or authoritative source reports changed."
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
