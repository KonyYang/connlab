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
    "updated_at": "2026-10-17T14:23:45.560058Z",
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
      "subject": "50005ef919616d82aded109766c0d588b57b9120",
      "summary": "Current precision, source controls and live row-count refinements retained. Latest feedback pins compact Confirm Data then Download Excel at far right of header after Current Decimals; import/parameter strip scrolls as one unit on constrained windows. Large Data Needs Review panel replaced by feedback-only sticky single line with ellipsis and complete newline-separated hover text. Original eligibility, error blocking, highlighted rows and numerical/export behavior unchanged. Empty feedback bar omitted. Local only; no publication.",
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
          "detail": "Affected matrix140frontend tests across10files passed on2d92c678. Real browser discovered long review min-content stretching page; bounded CSS grid-column/footer min-width fix and Data Confirmed hover added in50005ef9. Final affected51page+5TopBar tests56passed, sequential TypeScript/Vite production build passed.84unchanged feature/API/App tests retained from passing matrix, not duplicated. No code/test edits after final validation."
        },
        {
          "status": "passed",
          "detail": "TDD two coherent rendered-page slices: header action group after Current Decimals RED before relocation then GREEN; compact footer full-hover review/error-block/highlight test RED before relocation then GREEN. Existing multi-warning scan compaction and all original review tests retained; no acknowledgement/exclusion changes."
        },
        {
          "status": "passed",
          "detail": "Real isolated Edge706/1920 verification: Confirm Data and Download Excel pinned right, measured88.734px and102.047px widths/32px height, labels nowrap with scrollWidth=clientWidth; wide full workflow row inspected. Actual top confirmation generated both charts and enabled top download; actual XLSX downloaded to owned QA directory. Warning rows retained6included0excluded. Footer has0buttons and no old large review panel. Initial empty feedback omitted."
        },
        {
          "status": "passed",
          "detail": "Final50005ef9 real706x804 multi-error fixture: screenshot inspected and geometry asserted review client615/content1602,height17,textOverflowellipsis; footer right679 within706 viewport. Complete hover contains3newline-separated actual zero-current/missing-reading messages. Error class retained, no charts, Download disabled, highlighted source rows retained. Console0errors0warnings. Owned browsers and verified QA servers50064/5512 closed; no user data/browser touched."
        },
        {
          "status": "passed",
          "detail": "Same-agent sequential Standards/Spec exact-diff review:0remaining findings after fixing QA-discovered intrinsic-width issue. Existing handlers/state/portal/semantic paragraph messages retained; scoped compact styles and keyboard focus preserved. git diff --check clean. No numerical/API/backend/export changes; prior145backend/nativeExcel evidence retained for identical paths only, not rerun. Exact22cumulative paths."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Main context automatically revised same standard task for latest combined feedback: compact header-right confirm/download actions, bottom feedback-only single-line review/full-hover, no automatic row exclusion or validation change. Prior compact review proposal executed as directly explained to user."
        },
        "developer": {
          "status": "passed",
          "detail": "Two public page TDD RED/GREEN slices for header actions and compact review. Existing eligibility/click handlers reused verbatim. Original issue projection/paragraphs and highlights retained. Bounded QA fix constrains page grid track and footer min-width; full feedback text retained in native hover and accessible DOM."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Separate sequential same-agent Standards and Spec exact-diff review, not independent agents. Final Standards0 and Spec0 actionable findings. One QA-discovered intrinsic grid min-content overflow fixed and reverified; no new state/dependency/backend/file authority. Action labels fit, top-right pinning/overflow works, messages remain complete and error blocking unchanged."
        },
        "qa": {
          "status": "passed",
          "detail": "Main separate QA:140affected matrix passed then final56page/topbar tests and sequential build rerun after bounded layout fix;84unchanged tests retained. Real Edge706/1920 screenshots, button geometry, top confirm/chart/download and final706long-error ellipsis/full3line hover/error blocking passed,0consoleerrors. Original numerical/Office checks retained unchanged, not rerun."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local master50005ef919616d82aded109766c0d588b57b9120; exact22cumulative paths verified. Sole-writer final acceptance record only afterward; no remote publication or user data mutation."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Integrated locally at clean50005ef919616d82aded109766c0d588b57b9120. Latest5paths(page/test/CSS/tool docs/sole-writer board), exact22cumulative product/test/docpaths. Standard sequential passes accurately recorded. No remote refs changed."
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
