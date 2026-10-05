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
    "task_id": "TASK_TEMPERATURE_TOOLS_RETURN_ICON_20261005",
    "summary": "Replace temperature tool text return with Tools title-bar icon",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Move Back To Tools into the existing top action slot immediately to the right of Tools; reuse the Tools icon with accessible label and tooltip; retain return navigation and all calculation behavior.",
    "scope_paths": [
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/features/temperature/temperature.css"
    ],
    "risk_reasons": [],
    "activation_head": "81263f74335a1b4694102bbd7e2afc3ff9384326",
    "started_at": "2026-10-05T13:05:12.555802Z",
    "updated_at": "2026-10-05T13:45:48.786442Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_TOOLS_RETURN_ICON_20261005",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_TOOLS_RETURN_ICON_20261005",
      "subject": "effaf89ade660d3b6524f25f6221a4f4e4ce5b67",
      "summary": "Temperature tool return icon beside Tools remains verified; follow-up Workspace navigation label simplified from Test Report to Report with navigation unchanged.",
      "scope_ok": true,
      "changed_paths": [
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/TestReportDraftButton.test.tsx",
        "frontend/src/features/project-workbench/TestReportDraftButton.tsx",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx"
      ],
      "validation": [
        {
          "status": "passed",
          "check": "Current final copy adjustment: 78 tests passed in TestReportDraftButton and ProjectWorkbenchLayout suites. git diff --check passed. Only button literal and affected test expectations changed."
        },
        {
          "status": "passed",
          "check": "Live browser: Workspace Report label present; clicking opens Report page with existing project identity. Returned to Workspace; screenshot saved."
        },
        {
          "status": "passed",
          "check": "Prior unchanged temperature icon files retain verified 12 affected tests, TypeScript/Vite build, mouse/keyboard navigation and screenshot evidence recorded before revision. Literal-only follow-up does not affect these files or build structure; full build not repeated."
        },
        {
          "status": "passed",
          "check": "Same-agent exact-diff inspection: no scope, safety or navigation regressions; no backend, source data or report generation changes."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "mode": "same-agent micro implementation, self-review and targeted validation; no independent review claims"
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "publication": "Local only; final User Close remains required"
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_RISE_CHART_LABELS_20261005",
    "tier": "micro",
    "subject": "fbd9955434208b8c1a8f992d6bbb1166c3c77afc",
    "summary": "Align T-riseChart panes and linked full curve labels with reference",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closure after accepting the completed T-rise and Derating export refinements on 2026-10-05.",
    "closed_at": "2026-10-05T12:26:27.993602Z"
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
