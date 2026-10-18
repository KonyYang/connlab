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
    "updated_at": "2026-10-18T04:14:57.898054Z",
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
      "subject": "e61e1857168a2c26b2b8a458e8c39cccf8889479",
      "summary": "Prior current precision, dual-mode fitting/export, compact analysis cards and source preview retained. Latest localized layout revision narrows only Tested By input to60percent of former width; name value and all other fields unchanged.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/temperature_schemas.py",
        "backend/application/temperature_channel_layout.py",
        "backend/application/temperature_data_preparation.py",
        "backend/domain/temperature_data.py",
        "backend/domain/temperature_rise.py",
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/DataPreview.test.tsx",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/TemperatureCharts.tsx",
        "frontend/src/features/temperature/TestInfo.tsx",
        "frontend/src/features/temperature/currentPrecision.test.ts",
        "frontend/src/features/temperature/currentPrecision.ts",
        "frontend/src/features/temperature/sourceScan.test.ts",
        "frontend/src/features/temperature/sourceScan.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useSourceRowWindow.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py",
        "tests/unit/test_temperature_rise_calculations.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "validation": [
        {
          "status": "passed",
          "detail": "Latest exact state52TemperatureRisePage tests passed in25.49s; TypeScript/Vite production build passed. Browser observed Tested By180px before and108px after, retaining Even Yang; LTR180px,Equipment142.40625px,Condition162.640625px unchanged. No user input/data changed. Same-agent exact diff review and git diff --check passed. Only semantic class and scoped width/maxwidth changed; backend/Excel unaffected and not rerun."
        },
        {
          "status": "passed",
          "detail": "Latest exact state135temperature/frontendAPI/topbar tests across9files passed then TypeScript/Vite production build passed sequentially. Existing cross-screen Shift tests initially failed because hardcoded1000px now points to different source rows; tests now scroll by rendered row height, preserving all27-row interval/exclude/undo assertions.7focusedShiftchecks GREEN, then full135GREEN. No implementation-mirroring literal tests added for reversible density change."
        },
        {
          "status": "passed",
          "detail": "Browser real source before:450px viewport,36px rows,13px text,16px checkbox,80.5px header. Final:320px viewport,28px real rows,12px text,13px checkbox,middle alignment,49.195px header. Shared variable prevents CSS/virtual height drift. Original user source only observed; no selection/input mutation. Independent synthetic60-row tab End reaches row60 with scrollTop1411/scrollHeight1729/clientHeight318,18mountedrows of28px; Shift selected60,exclude0included/60excluded,Undo60included/0excluded.671px narrow view checked; viewport reset and temporary tab closed."
        },
        {
          "status": "passed",
          "detail": "Same-agent separate Standards0/Spec0 exact-diff findings. Only latest5product/test/docfiles plus sole-writer board. Backend/nativeExcel tests not repeated because code paths unchanged; prior dual-mode/native4case evidence retained. Diff check clean."
        },
        {
          "status": "passed",
          "detail": "Backend affected matrix: initial164cases had162passes and2obsolete auxiliary-origin expectations. Updated only those test expectations to blank auxiliary cells for synthetic origin; final50Excel gateway tests passed in8.37s. Other114passed domain/preparation/API cases unchanged afterward. Includes18numerical,6newAPI combinations and4newworkbook mode/baseline combinations. Existing Starlette TestClient deprecation warning remains."
        },
        {
          "status": "passed",
          "detail": "Final135frontend tests across9files passed, then TypeScript/Vite build passed sequentially. After new fit-range behavior targeted RED/GREEN and full affected frontend rerun on exact code. Test covers warning/full hover, no artificial-origin row unchecked, toggle clears stale warning, checked origin retained, Derating disabled unchecked, fit line begins at first selected point."
        },
        {
          "status": "passed",
          "detail": "Native isolated hidden Excel4combinations measured-zero present/absent x forced/free. CalculateFullRebuild confirms summary and actual series [0,10,20,30] with forcedzero first0, measuredfree first2C, or missingfree [10,20,30]; freefit c2 versus forcedc0; equations/R2 update and no formula errors. Raw source cells unchanged, warning present only missingfree. Actual chart PNGs and PDF warning/table rendering inspected, complete and readable. Owned Excel closed without saving or clipboard use."
        },
        {
          "status": "passed",
          "detail": "Isolated live browser uploads only syntheticCSV: missing baseline freefit shows 3measured rows, c.8 and full warninghover; measuredfree first0A/.8C; toggling checked replaces with artificial0A/0C while raw8rows included and Derating stays restricted. Final browser checks fit starts at same x208.7673 as first10A marker, not0A; compactwarning17.5px with0margin. Test tabs closed, original user tab/state untouched."
        },
        {
          "status": "passed",
          "detail": "TDD:4initialdomainRED thenGREEN; missingbaseline insufficient-stages RED/GREEN; XLSX missingwarning RED then4GREEN; frontend warningRED/GREEN and fit-rangeRED/GREEN. Sequential same-agent Standards0 and Spec0 findings. git diff --check clean. No automatic thermal-equilibrium inference added; existing1percent current stability rule retained."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "detail": "Localized in-scope same-task feedback: shrink only Tested By input40percent; retain values and other fields."
        },
        "developer": {
          "status": "passed",
          "detail": "Main agent added semantic input class and scoped width60percent/max108px; no behavior or data modifications."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Sequential main-agent exact diff self-review: requirement met, selectors limited to Tested By, no unrelated changes or remaining findings. No independent review claimed."
        },
        "qa": {
          "status": "passed",
          "detail": "52page tests and production build passed; real browser before/after measures confirm40percent reduction and unchanged values/other widths. No new implementation-mirroring tests for reversible style-only change."
        },
        "integrator": {
          "status": "passed",
          "detail": "Clean local product commit verified; cumulative paths resolved from activation HEAD. No remote publication."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Local reviewed Tested By width revision integrated at e61e1857168a2c26b2b8a458e8c39cccf8889479;52page tests, build and browser width evidence correspond to exact product state. No remote refs changed."
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
