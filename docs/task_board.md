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
    "task_id": "TASK_TEMPERATURE_CURRENT_MAX_STYLE_20261008",
    "summary": "Match calculated current color to Max curve and use bold text",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Calculated Current display only; preserve calculation and Derating summary styling",
    "scope_paths": [
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/features/temperature/TemperatureCharts.tsx",
      "frontend/src/features/temperature/temperature.css"
    ],
    "risk_reasons": [],
    "activation_head": "63a7ef4009379a772b5fd5ebf2e0bdac1978f7a0",
    "started_at": "2026-10-07T23:59:05.591125Z",
    "updated_at": "2026-10-08T00:00:21.687062Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_CURRENT_MAX_STYLE_20261008",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "integration": {
        "branch": "master",
        "subject": "67cbe7fa6a329299a67917d7a86afefbabb6a2b8",
        "publication": "not requested",
        "status": "passed"
      },
      "changed_paths": [
        "frontend/src/features/temperature/TemperatureCharts.tsx",
        "frontend/src/features/temperature/temperature.css",
        "frontend/src/pages/TemperatureRisePage.tsx"
      ],
      "validation": [
        {
          "result": "30 passed",
          "command": "npm run test -- src/pages/TemperatureRisePage.test.tsx",
          "status": "passed"
        },
        {
          "result": "TypeScript/Vite passed",
          "command": "npm run build",
          "status": "passed"
        },
        {
          "result": "Current 66.54 A and Max equation both rgb(220,112,33); current weight 700; Derating summary remains blue/400; user state untouched; screenshot saved",
          "command": "read-only browser style verification",
          "status": "passed"
        },
        {
          "command": "git diff --check",
          "status": "passed"
        }
      ],
      "summary": "Calculated Current reuses exact Max curve orange and has 700 bold text; calculation and Derating summary unchanged.",
      "task_id": "TASK_TEMPERATURE_CURRENT_MAX_STYLE_20261008",
      "scope_ok": true,
      "schema": "connlab.sol-task-report",
      "version": 1,
      "roles": {
        "developer": {
          "review": "Exact diff self-review: style only, same color constant, no calculation change, separate modifier avoids changing Derating summary; no findings",
          "status": "passed"
        }
      },
      "subject": "67cbe7fa6a329299a67917d7a86afefbabb6a2b8"
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_DERATING_COMPACT_LAYOUT_20261008",
    "tier": "micro",
    "subject": "fe0a9426773ab46bc81af9d839ef90a12c9ae494",
    "summary": "Compact Derating inputs and align Generate Derating at row right",
    "disposition": "completed",
    "decision_ref": "User final authorization: 关闭任务",
    "closed_at": "2026-10-07T23:55:43.716788Z"
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
