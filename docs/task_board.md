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
    "task_id": "TASK_TEMPERATURE_EFFECTIVE_COLUMN_GROUPING_20261009",
    "summary": "Normalize temperature editor columns and preserve sample groups through balanced exclusions",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Temperature source grid ordering, sample grouping, exclusions, headers and regression protection",
    "scope_paths": [
      "frontend/src/features/temperature",
      "frontend/src/api/temperature.ts",
      "frontend/src/styles",
      "backend/domain/temperature_data.py",
      "backend/api/temperature_schemas.py",
      "backend/application/temperature_data_preparation.py",
      "tests/unit/test_temperature_data_preparation.py",
      "tests/integration/test_temperature_api.py",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "ab95f5e485be65a6626bc67e8f493b66b0fbc42b",
    "started_at": "2026-10-09T00:07:00.551432Z",
    "updated_at": "2026-10-09T23:12:56.110272Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_EFFECTIVE_COLUMN_GROUPING_20261009",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "version": 1,
      "roles": {
        "qa": {
          "details": "Complete affected tests, build and isolated UI verification passed on final code/test state.",
          "status": "passed",
          "context": "same-agent final QA"
        },
        "reviewer": {
          "details": "Exact diff: zero outstanding findings per axis. CSS is feature-scoped, black triangle follows explicit User request, native accessibility/focus retained, no speculative abstractions or scope expansion.",
          "status": "passed",
          "context": "same-agent sequential Standards and Spec passes"
        },
        "developer": {
          "details": "TDD RED/GREEN at DataPreview public seam; native select retained without new state or dependencies.",
          "status": "passed",
          "context": "same agent"
        }
      },
      "scope_ok": true,
      "changed_paths": [
        "backend/api/temperature_schemas.py",
        "backend/application/temperature_data_preparation.py",
        "backend/domain/temperature_data.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/ColumnActions.tsx",
        "frontend/src/features/temperature/DataPreview.test.tsx",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/sampleGroups.ts",
        "frontend/src/features/temperature/sourceColumns.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useDataGridEditing.ts",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py"
      ],
      "subject": "8fc5c950f57f65d54f31b9e04ecaaec9a4007d91",
      "integration": {
        "details": "Clean exact local commit 8fc5c950f57f65d54f31b9e04ecaaec9a4007d91; prior task changes retained, no push or Close.",
        "status": "passed",
        "context": "local master"
      },
      "schema": "connlab.sol-task-report",
      "task_id": "TASK_TEMPERATURE_EFFECTIVE_COLUMN_GROUPING_20261009",
      "summary": "Effective sample columns and immediate movement retained; Move Before is now a single native dropdown row with a black triangle, without the separate Choose Column field.",
      "validation": [
        {
          "name": "Single-row regression",
          "details": "Amended public grid/menu test RED on old Choose Column presentation then GREEN. Empty destination still cannot trigger movement on open.",
          "status": "passed"
        },
        {
          "name": "Affected frontend matrix",
          "details": "58 tests passed on final code/test bytes: 27 DataPreview and 31 TemperatureRisePage. Existing immediate movement, protected roles, spare/block moves, Undo and focus behavior retained.",
          "status": "passed"
        },
        {
          "name": "Production build",
          "details": "TypeScript and Vite production build passed.",
          "status": "passed"
        },
        {
          "name": "Isolated browser",
          "details": "Borderless one-row Move Before, black triangle rgb(0,0,0), native AX expanded candidate menu after click; selection immediately moves F before C and dismisses popup; Undo restores. Zero console warning/error logs. User tab not operated.",
          "status": "passed"
        },
        {
          "name": "Prior unchanged numerical/API baseline",
          "details": "88 backend preparation/calculation/workbook/API tests passed in initial grouping revision, not rerun for this presentation-only change. API/numerical behavior unchanged.",
          "status": "passed"
        }
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_TOOLS_CUSTOMER_REPORT_SINGLE_ACTION_20261008",
    "tier": "micro",
    "subject": "1a0399c45c629356d0a75d1867c8013fabd409e3",
    "summary": "Use one file-picker action to generate a customer report in Tools",
    "disposition": "completed",
    "decision_ref": "User final authorization: 关闭任务",
    "closed_at": "2026-10-08T22:59:04.069000Z"
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
