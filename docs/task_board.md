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
    "updated_at": "2026-10-17T12:06:32.799872Z",
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
      "subject": "df2e9d7d03eba88ea576a73191c4f33dc9986fdc",
      "summary": "Current precision0to4(default0) unified across rounding/zero detection/calculation/charts/Excel with raw data and exclusions preserved. Acceptance refinement removes standalone source filename row and moves Confirm Data immediately left of Download Excel in sticky footer, retaining eligibility and confirmed state. Sheet Name hover shows complete filename; browser uploads expose no absolute disk path, a disclosed limitation, not fabricated. Local only; no publication.",
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
          "detail": "Original numerical implementation unchanged in UI refinement: retained145passing backend tests (102unit plus43API), native Excel read-only full recalculation of actual0dp/1dp downloads, raw .0087/10.05 preserved, matching current axes/formats/caches. No repeat of unaffected checks."
        },
        {
          "status": "passed",
          "detail": "UI TDD: new source-tooltip/footer grouping/confirmation/invalidation test RED before implementation and GREEN afterward. Final frontend matrix131passing tests across9files:83unchanged tests passed in initial affected run; two old filename-visible expectations updated to tooltip semantics, then all48page tests passed on final state. Sequential tsc-b and Vite production build passed."
        },
        {
          "status": "passed",
          "detail": "Real isolated Edge built-page checks: imported ownedCSV through real chooser; complete filename observed on Sheet Name title, no standalone source row; Confirm Data before Download Excel. At1280x720 and598x804 footer buttons visible before confirmation; actual footer confirmation generates both charts, shows Data Confirmed and enables download. At320x804 actions remain adjacent with wrapped status. Scrolled actual app-workspace to1288; confirm bounding box remains within598x804viewport. Screenshots inspected; console0errors0warnings. Owned browser and verified QA server33500 stopped; no user browser/data touched."
        },
        {
          "status": "passed",
          "detail": "Exact diff self-reviewed; git diff --check clean. Revision changes only TemperatureRisePage.tsx/test, temperature.css, tool documentation and sole-writer task board. No numerical/export/profile/project/backend edits in revision; no new filesystem path authority or dependency."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Main context standard plan for original current precision and bounded acceptance refinement; automatically Revise same ready task per AGENTS. No routine plan approval or unrelated task creation."
        },
        "developer": {
          "status": "passed",
          "detail": "Original decimal half-up TDD slices retained. Revision narrow public rendered-page seam proves hidden filename tooltip, footer button order, confirmation, and precision invalidation. Original busy/role/group conditions reused verbatim."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate sequential same-agent Standards and Spec passes, not independent contexts. Standards:0actionable findings; existing typed state and sticky bar reused, obsolete selectors removed, scoped CSS and no new authority. Spec:requested compactness and bottom action flow implemented; one disclosed capability limit is absolute disk path unavailable through current browser File upload, so complete filename is shown honestly. No other missing behavior or scope creep."
        },
        "qa": {
          "status": "passed",
          "detail": "Same main context separate QA:131affected frontend tests passed as83unchanged plus48finalpage; build passed sequentially. Isolated real Edge1280/598/320 and actual scrolling/confirm workflow verified. Original145backend/nativeExcel verification retained on identical numerical bytes; not falsely reported as rerun."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local master at exactdf2e9d7d03eba88ea576a73191c4f33dc9986fdc; cumulative20product/test/docpaths unchanged. No push or publication. Sole writer records ready_for_close."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Original current precision and UI acceptance refinement integrated locally on clean master. Exact cumulative20paths; no external writes or remote publication. Absolute disk path limitation disclosed in UI contract and user communication."
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
