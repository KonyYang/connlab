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
    "updated_at": "2026-10-09T22:50:16.911199Z",
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
      "subject": "05dbaa7e388896aca063718ba6ba53433dcf2c69",
      "version": 1,
      "roles": {
        "qa": {
          "context": "same-agent final QA",
          "details": "Risk-proportionate complete preview matrix, build and isolated browser passed.",
          "status": "passed"
        },
        "reviewer": {
          "context": "same-agent sequential Standards and Spec passes",
          "details": "Zero outstanding findings per axis on exact popup diff; unused title prop/styles removed, accessible dialog name retained.",
          "status": "passed"
        },
        "developer": {
          "context": "same agent",
          "details": "TDD at actual grid/menu seam; first Close test RED then GREEN, amended heading test RED then GREEN.",
          "status": "passed"
        }
      },
      "scope_ok": true,
      "summary": "Sample-preserving effective columns and header multi-selection retained; popup now contains actions only, without redundant Close or column heading. Outside click, Escape and keyboard focus remain functional.",
      "validation": [
        {
          "status": "passed",
          "details": "26 preview tests passed on final code/test state; meaningful RED/GREEN for removal and dismissal/focus behavior.",
          "name": "Popup refinement preview matrix"
        },
        {
          "status": "passed",
          "details": "TypeScript/Vite passed sequentially after tests.",
          "name": "Production build"
        },
        {
          "status": "passed",
          "details": "No visible popup heading or Close; outside click dismisses, Escape dismisses and restores source-header focus; zero console warning/error logs. User tab not operated.",
          "name": "Isolated browser"
        },
        {
          "status": "passed",
          "details": "Earlier 56 header-selection frontend tests and 88 grouping backend tests passed in prior implementation/revision. Current change is popup presentation-only; API, numerical and selection logic unchanged. Evidence retained in docs/temperature_rise_tool.md.",
          "name": "Prior unchanged behavior"
        }
      ],
      "schema": "connlab.sol-task-report",
      "integration": {
        "context": "local master",
        "details": "Exact in-scope popup revision committed at clean HEAD 05dbaa7e; prior task work retained, no push or Close.",
        "status": "passed"
      },
      "task_id": "TASK_TEMPERATURE_EFFECTIVE_COLUMN_GROUPING_20261009",
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
