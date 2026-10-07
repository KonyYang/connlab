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
    "task_id": "TASK_TEMPERATURE_AUTO_COEFFICIENTS_20261007",
    "summary": "Automatically populate fitted coefficients when generating T-riseChart",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Remove the redundant coefficient retrieval step; preserve manual edits, invalidation and default Excel export values.",
    "scope_paths": [
      "frontend/src/features/temperature/useTemperatureTool.ts",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "b3cf34600c4368e734484660d8d5e8bc53c287a3",
    "started_at": "2026-10-07T15:37:55.665299Z",
    "updated_at": "2026-10-07T23:33:26.152302Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_AUTO_COEFFICIENTS_20261007",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "version": 1,
      "validation": [
        {
          "result": "Absence-and-calculation/export regression failed before removal and passed after; final page30, preview18, API2, TopBar5: 55/55 passed.",
          "status": "passed",
          "name": "TDD and final affected frontend matrix"
        },
        {
          "result": "TypeScript/Vite passed sequentially on final source/test bytes.",
          "status": "passed",
          "name": "Production build"
        },
        {
          "result": "No coefficient display before/after generation; both automatic charts, equations and 38.01 A calculation verified using disposable CSV. Console warnings/errors zero; User tab untouched; QA tab closed.",
          "status": "passed",
          "name": "Isolated browser"
        },
        {
          "result": "Separate sequential same-agent exact-diff passes found no outstanding issues. Table/editor-specific styles and unused edit action removed; API, numerical algorithms, internal coefficients and export unchanged.",
          "status": "passed",
          "name": "Standards and Spec review"
        }
      ],
      "scope_ok": true,
      "schema": "connlab.sol-task-report",
      "roles": {
        "developer": {
          "execution": "One Astra micro work unit; TDD and same-agent review, not independent agents.",
          "status": "passed"
        }
      },
      "changed_paths": [
        "docs/temperature_rise_tool.md",
        "frontend/src/features/temperature/DataPreview.test.tsx",
        "frontend/src/features/temperature/DataPreview.tsx",
        "frontend/src/features/temperature/TemperatureCharts.tsx",
        "frontend/src/features/temperature/sourceScan.ts",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/features/temperature/useTemperatureTool.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx"
      ],
      "subject": "e493138e6313c1c7da0223969f265177858fab75",
      "summary": "Removed redundant coefficient display/editor while preserving internal fitted values for calculation/export, chart equations and confirmation-triggered generation; scan-based feedback refinements retained.",
      "integration": {
        "status": "passed",
        "subject": "e493138e6313c1c7da0223969f265177858fab75",
        "publication": "Local only; final Close not requested.",
        "branch": "master"
      },
      "task_id": "TASK_TEMPERATURE_AUTO_COEFFICIENTS_20261007"
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_EXCEPTION_MAPPING_20261007",
    "tier": "standard",
    "subject": "683bcfccd170acd414fc67f9107414ff1e5f5da4",
    "summary": "Auto-group sample thermocouples and simplify exception-only channel adjustments",
    "disposition": "completed",
    "decision_ref": "User explicitly requested final task closure after the accepted temperature preview refinements and verified delivery.",
    "closed_at": "2026-10-07T15:20:08.452766Z"
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
