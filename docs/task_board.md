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
    "updated_at": "2026-10-09T00:21:05.359845Z",
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
      "summary": "Normalized source-grid ordering and single-header sample colors; balanced exclusions preserve sample identity and automatically adjust counts with restore/undo; unequal groups block frontend and API confirmation.",
      "scope_ok": true,
      "integration": {
        "context": "local master",
        "status": "passed",
        "details": "Exact in-scope reviewed implementation committed at clean HEAD; no push or closure."
      },
      "task_id": "TASK_TEMPERATURE_EFFECTIVE_COLUMN_GROUPING_20261009",
      "roles": {
        "qa": {
          "context": "same-agent final QA pass",
          "status": "passed",
          "details": "Risk-proportionate complete affected matrix, build and isolated browser; only failed test-assertion file rerun after correction."
        },
        "reviewer": {
          "context": "same-agent separate sequential Standards and Spec passes",
          "status": "passed",
          "details": "Zero outstanding findings on either axis; request-compatible validation, group metadata/slot recovery and source-file protection reviewed."
        },
        "developer": {
          "context": "same agent",
          "status": "passed",
          "details": "TDD failure-before-fix and focused checks at grid, page and API seams."
        }
      },
      "changed_paths": [
        "backend/api/temperature_schemas.py",
        "backend/application/temperature_data_preparation.py",
        "backend/domain/temperature_data.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/api/temperature.ts",
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
      "schema": "connlab.sol-task-report",
      "version": 1,
      "validation": [
        {
          "details": "59 tests: final preview rerun 21 passed after test-only A/B assertion correction; unchanged Page31/API2/TopBar5 passed.",
          "status": "passed",
          "name": "Frontend affected tests"
        },
        {
          "details": "88 preparation, numerical calculation, workbook gateway and real API tests passed; one pre-existing Starlette/httpx deprecation warning.",
          "status": "passed",
          "name": "Backend affected matrix"
        },
        {
          "details": "npm run build passed, sequentially after Vitest.",
          "status": "passed",
          "name": "TypeScript/Vite"
        },
        {
          "details": "4-to-3 TC2 exclusion, alternate header colors, protected role order, actual chart, unequal blocking and right-click restore verified. Console warnings/errors zero. Local API restarted through official script; user tab not manually operated, React HMR rebuilt the session and source needs reimport.",
          "status": "passed",
          "name": "Isolated browser"
        }
      ],
      "subject": "66c0e23f3d02eb62319950d47616d34fa5dee2e7"
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
