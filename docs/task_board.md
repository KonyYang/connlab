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
    "task_id": "TASK_TEMPERATURE_TEST_INFO_20261011",
    "summary": "Add editable temperature report metadata and optional project association",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Test Info editor, confirmed project defaults with protected manual overrides, compact T-riseChart header and remove blank CR; no project authority writes",
    "scope_paths": [
      "frontend/src/features/temperature",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/api/temperature.ts",
      "backend/application/tools_temperature_service.py",
      "backend/application/temperature_report_metadata.py",
      "backend/api/temperature_schemas.py",
      "backend/api/routes_tools_temperature.py",
      "backend/infrastructure/office/temperature_rise_report_sheet.py",
      "backend/infrastructure/office/temperature_workbook_gateway.py",
      "tests/unit/test_temperature_workbook_gateway.py",
      "tests/integration/test_tools_temperature_api.py",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "86d450a73d025a234bcdd51249084de00273d471",
    "started_at": "2026-10-11T13:28:37.916192Z",
    "updated_at": "2026-10-11T14:29:52.090204Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_TEST_INFO_20261011",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "summary": "Editable Test Info with optional confirmed project defaults; XLSX metadata starts at A1 in a vertical pale-yellow label/value table, main report precedes supporting detail and CR is removed",
      "scope_ok": true,
      "roles": {
        "reviewer": {
          "summary": "Separate sequential same-agent Standards and Spec passes; 0 outstanding findings, no independent-agent review claimed",
          "status": "passed"
        },
        "developer": {
          "summary": "HTTP regression RED at A21 then GREEN at A1; blank/zero humidity and dynamic source reference tests passed",
          "status": "passed"
        },
        "qa": {
          "summary": "Final 111-test affected Python matrix and native Excel numeric/visual QA passed; Initial Data preserved",
          "status": "passed"
        }
      },
      "version": 1,
      "subject": "650c3a655a8c24f0db9f7341ee51fa49f02633a7",
      "integration": {
        "summary": "Exact local master commit, clean worktree; no remote publication",
        "status": "passed"
      },
      "changed_paths": [
        "backend/api/routes_tools_temperature.py",
        "backend/api/temperature_schemas.py",
        "backend/application/temperature_report_metadata.py",
        "backend/application/tools_temperature_service.py",
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/TestInfo.tsx",
        "frontend/src/features/temperature/reportInfo.test.ts",
        "frontend/src/features/temperature/reportInfo.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureReportInfo.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "validation": [
        {
          "summary": "111 tests passed on final revision state",
          "name": "temperature Python matrix",
          "status": "passed"
        },
        {
          "summary": "A1:I6 metadata and single-page A1:W44 visually checked, no formula errors, 30 C -> 66.5 A, 35 C -> 72.860807 A; relocated endpoint edit updates linked summary",
          "name": "native Excel layout and recalculation",
          "status": "passed"
        },
        {
          "summary": "Prior feature validation: 103 frontend tests and TypeScript/Vite build; revision contains no frontend changes",
          "name": "unchanged frontend validation retained",
          "status": "passed"
        }
      ],
      "task_id": "TASK_TEMPERATURE_TEST_INFO_20261011",
      "schema": "connlab.sol-task-report"
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_EXPORT_PRESENTATION_20261011",
    "tier": "standard",
    "subject": "d4fdb00215f6cc73ebcc7c598df1418072998b7a",
    "summary": "Simplify temperature-rise XLSX source and report presentation",
    "disposition": "completed",
    "decision_ref": "User final authorization: 关闭; local close only because remote publication was blocked by security review",
    "closed_at": "2026-10-11T04:04:55.372856Z"
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
