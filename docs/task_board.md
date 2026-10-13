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
    "task_id": "TASK_TEMPERATURE_MULTI_CURRENT_EXPORT_20261014",
    "summary": "Export stable auxiliary current rows above the selected main current in T-riseChart",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Use existing stable-current classification, stage endpoint source readings and actual current names; add gray bold centered integer-display current rows, preserve numeric precision, leave synthetic-origin auxiliary cells blank, and keep summary/chart/fit/calculator references correct without source mutation",
    "scope_paths": [
      "backend/application/temperature_data_preparation.py",
      "backend/infrastructure/office/temperature_workbook_gateway.py",
      "backend/infrastructure/office/temperature_rise_report_sheet.py",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/unit/test_temperature_workbook_gateway.py",
      "tests/integration/test_tools_temperature_api.py",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "b06621ad13a66848af3ac604b029a82ef3ba53c5",
    "started_at": "2026-10-13T23:44:54.493353Z",
    "updated_at": "2026-10-13T23:59:47.445709Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_MULTI_CURRENT_EXPORT_20261014",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "integration": {
        "status": "passed",
        "detail": "Clean local master exact subject, seven product/test/doc paths match user-approved scope; previous task closed by CloseAndSubmit checkpoint, no remote publication, awaiting this task explicit Close"
      },
      "changed_paths": [
        "backend/application/temperature_data_preparation.py",
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "docs/temperature_rise_tool.md",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "version": 1,
      "roles": {
        "developer": {
          "status": "passed",
          "detail": "TDD exported XLSX regressions failed before implementation and passed afterward; five targeted unit cases and one HTTP regression provided developer feedback before final matrix. Stable auxiliary metadata comes from existing application classification, workbook adapter owns layout."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Focused sequential same-agent Standards and Spec passes on exact diff found zero outstanding issues; dependencies, source identity, literal safety, cache/fit/chart references, default compatibility and scope checked. No independent reviewer claimed."
        },
        "qa": {
          "status": "passed",
          "detail": "Same-agent separate final QA pass: complete affected 119-test matrix once after implementation/review, plus three native Excel cases, PDF visual verification and actual localhost download. No independent QA agent claimed."
        }
      },
      "validation": [
        {
          "status": "passed",
          "detail": "119 final backend tests across preparation, numerical calculations, workbook export and HTTP API passed; one existing Starlette/httpx deprecation warning. Single-current compatibility, stage exclusion, CSV text coercion, real/synthetic origin, current names/literal safety, stable-only classification and shifted chart references covered."
        },
        {
          "status": "passed",
          "detail": "Three isolated read-only native Excel cases recalculated with no formula errors; displayed auxiliary values are integers while stored values remain precise, both zero-origin cases correct, chart XValues are main-current values, target edits recalculate correctly, auxiliary source edits update header values without changing fit/calculator. Excel print previews rendered and visually reviewed for recorded-zero and three-sample layouts; eight temporary outputs cleaned."
        },
        {
          "status": "passed",
          "detail": "Actual running localhost import/download with synthetic CSV returned correct three auxiliary headers, main values and retained 125.002 precision; direct loopback HTTP used after an environment-proxy 502. User files/session/project authority untouched. git diff --check passed; frontend code unchanged so no frontend build rerun."
        }
      ],
      "subject": "7f0f8f29af6c329e8afca979044e9e0813473a4e",
      "schema": "connlab.sol-task-report",
      "scope_ok": true,
      "task_id": "TASK_TEMPERATURE_MULTI_CURRENT_EXPORT_20261014",
      "summary": "Stable auxiliary current headers precede the named main current in T-riseChart; stage-endpoint values retain full precision and integer display, synthetic auxiliary origins remain blank, and all fits/charts/calculator references follow only the selected main current"
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_REVIEW_SIMPLIFICATION_20261014",
    "tier": "micro",
    "subject": "ac6da92dbc79c1b357dd029b5208bf3913d14a31",
    "summary": "Simplify temperature warning review and remove redundant row controls",
    "disposition": "completed",
    "decision_ref": "User closes the completed warning-review task and requests multi-current export implementation on 2026-10-14",
    "closed_at": "2026-10-13T23:44:54.493353Z"
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
