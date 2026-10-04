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
    "task_id": "TASK_TEMPERATURE_RISE_DERATING_20261004",
    "summary": "Temperature rise and Derating tool with confirmed data preparation and native Excel charts",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Implement the approved third layout, channel mapping/replacement/reordering, reversible row/column exclusions, human-confirmed anomaly review, macro-equivalent calculations, charts and independent Excel download. Verify original preservation, existing Tools, tests and browser flow; deliver ready_for_close.",
    "scope_paths": [
      "backend/domain",
      "backend/application",
      "backend/infrastructure/office",
      "backend/api",
      "frontend/src",
      "tests",
      "docs/PROJECT_CONTEXT.md",
      "docs/temperature_rise_tool.md",
      "design-qa.md"
    ],
    "risk_reasons": [],
    "activation_head": "6a12e5dc00ab14180b07fcffb32301d8ec10d8f1",
    "started_at": "2026-10-04T01:53:59.879053Z",
    "updated_at": "2026-10-04T03:23:19.467183Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_RISE_DERATING_20261004",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_RISE_DERATING_20261004",
      "subject": "de90125ee1acff07cd6ccfe0ed8dd6bdf9af9006",
      "summary": "Implemented confirmed scanner preparation, native temperature-rise/Derating curves and independent Excel export; ready for operator acceptance.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/main.py",
        "backend/api/routes_tools_temperature.py",
        "backend/api/temperature_schemas.py",
        "backend/application/temperature_data_preparation.py",
        "backend/application/tools_temperature_service.py",
        "backend/domain/temperature_data.py",
        "backend/domain/temperature_rise.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "design-qa.md",
        "docs/PROJECT_CONTEXT.md",
        "docs/temperature_rise_tool.md",
        "frontend/src/App.tsx",
        "frontend/src/api/client.ts",
        "frontend/src/api/temperature.test.ts",
        "frontend/src/api/temperature.ts",
        "frontend/src/features/temperature/ChannelMapping.tsx",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/TemperatureCharts.tsx",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx",
        "frontend/src/pages/ToolsPage.tsx",
        "tests/fixtures/temperature_rise/scanner.json",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_data_preparation.py",
        "tests/unit/test_temperature_rise_calculations.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "validation": [
        {
          "status": "passed",
          "check": "62 affected backend tests on ConnLab Python 3.11; existing Tools and Office-boundary coverage included"
        },
        {
          "status": "passed",
          "check": "Full frontend 820 passed / one existing skip; final chart-label adjustment followed by six affected tests and TypeScript/Vite build"
        },
        {
          "status": "passed",
          "check": "Live browser import, spare-channel replacement, reversible exclusions, confirmation/invalidation, both curves, current and download feedback; wide/narrow screenshots; no console errors"
        },
        {
          "status": "passed",
          "check": "Final export read-only opened in desktop Excel; both native charts rendered, formula and trendline baseline matched; original source SHA unchanged"
        },
        {
          "status": "passed",
          "check": "Sequential standards/spec review and iterative source-versus-render design QA; git diff check clean"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "mode": "same-agent implementation with RED/GREEN behavioral slices"
        },
        "reviewer": {
          "status": "passed",
          "mode": "same-agent sequential standards and specification passes; not independent-agent review",
          "evidence": "docs/temperature_rise_tool.md and design-qa.md"
        },
        "qa": {
          "status": "passed",
          "mode": "same-agent final affected matrix, browser and desktop Excel verification",
          "limitation": "In-app automation does not expose completed OS download event; HTTP/filename and exported workbook independently verified"
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "publication": "Local only; user acceptance/Close still required"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_RISE_TOOL_20261003",
    "tier": "standard",
    "subject": "94d346807ace21cb0b0b51ab6062664c3e5dcd5b",
    "summary": "Standalone temperature rise and derating import preview and workbook tool",
    "disposition": "cancelled",
    "decision_ref": "User cancelled and requested complete withdrawal because the core temperature-rise curve output did not meet the original workbook. Feature withdrawn in 94d346807ace21cb0b0b51ab6062664c3e5dcd5b; 31 Python regressions, 814 frontend tests, backend compilation and TypeScript/Vite build passed. Preserve data and Git history; do not publish.",
    "closed_at": "2026-10-03T23:36:11.959485Z"
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
