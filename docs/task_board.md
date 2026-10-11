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
    "task_id": "TASK_TEMPERATURE_EXPORT_PRESENTATION_20261011",
    "summary": "Simplify temperature-rise XLSX source and report presentation",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Preserve original imported Initial Data with yellow stage-source rows; compact formatted measurement labels, MAX-only calculator and rounded space-efficient T-riseChart; add blank Setup and CR worksheets. Preserve analysis, native formulas and Derating behavior; never modify reference workbook.",
    "scope_paths": [
      "backend/infrastructure/office/temperature_workbook_gateway.py",
      "backend/infrastructure/office/temperature_rise_report_sheet.py",
      "tests/unit/test_temperature_workbook_gateway.py",
      "tests/integration/test_tools_temperature_api.py",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "b8e5ffbd0c8e3b0aea5edebeae12d29e87cea589",
    "started_at": "2026-10-11T03:11:15.207928Z",
    "updated_at": "2026-10-11T03:56:17.809408Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_EXPORT_PRESENTATION_20261011",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "task_id": "TASK_TEMPERATURE_EXPORT_PRESENTATION_20261011",
      "changed_paths": [
        "backend/infrastructure/office/temperature_rise_report_sheet.py",
        "backend/infrastructure/office/temperature_workbook_gateway.py",
        "docs/temperature_rise_tool.md",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "tests/integration/test_tools_temperature_api.py",
        "tests/unit/test_temperature_workbook_gateway.py"
      ],
      "validation": [
        {
          "method": "85 temperature frontend tests",
          "status": "passed"
        },
        {
          "method": "105 backend preparation/calculation/export/API tests",
          "status": "passed"
        },
        {
          "method": "Vite production build",
          "status": "passed"
        },
        {
          "method": "Native Excel read-only recalculation, extracted labels and bold orange current; source hash unchanged",
          "status": "passed"
        },
        {
          "method": "Artifact summary rendered and visually inspected; git diff --check",
          "status": "passed"
        }
      ],
      "integration": {
        "method": "Scoped local master commit; no remote publication",
        "status": "passed"
      },
      "version": 1,
      "roles": {
        "developer": {
          "method": "Coherent RED/GREEN public-seam tests then localized implementation",
          "status": "passed"
        },
        "reviewer": {
          "status": "passed",
          "independent": false,
          "method": "Sequential same-agent Standards and Spec reviews of exact diff",
          "spec_outstanding": 0,
          "standards_outstanding": 0
        },
        "qa": {
          "status": "passed",
          "method": "Final affected matrices and native Excel QA",
          "limitations": "Artifact preview does not evaluate existing LINEST array helper, so native Excel verified calculator values; no browser OS download exercised in this revision"
        }
      },
      "scope_ok": true,
      "summary": "Original-data export simplification plus literal label extraction, automatic MAX target current and bold orange XLSX result",
      "schema": "connlab.sol-task-report",
      "subject": "d4fdb00215f6cc73ebcc7c598df1418072998b7a"
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_COMPACT_UNPOWERED_REVIEW_20261011",
    "tier": "micro",
    "subject": "1b303c56f9bcdcf91d1c7d8186ba1af0e5f9c854",
    "summary": "Compact unpowered review warnings into consecutive scan ranges",
    "disposition": "completed",
    "decision_ref": "User authorization: 关闭上一任务，继续导出优化",
    "closed_at": "2026-10-11T03:11:15.207928Z"
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
