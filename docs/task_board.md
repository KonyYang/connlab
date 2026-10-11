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
    "task_id": "TASK_TEMPERATURE_COMPACT_UNPOWERED_REVIEW_20261011",
    "summary": "Compact unpowered review warnings into consecutive scan ranges",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Presentation-only zero-current warning copy and consecutive A-column scan ranges; retain original issue rows, selections and confirmation semantics",
    "scope_paths": [
      "frontend/src/features/temperature/sourceScan.ts",
      "frontend/src/pages/TemperatureRisePage.tsx",
      "frontend/src/pages/TemperatureRisePage.test.tsx",
      "frontend/src/features/temperature/sourceScan.test.ts",
      "docs/temperature_rise_tool.md"
    ],
    "risk_reasons": [],
    "activation_head": "a123f58ec33d3b57459df079e61ca07d7e672558",
    "started_at": "2026-10-11T02:06:25.288323Z",
    "updated_at": "2026-10-11T02:09:05.779058Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_TEMPERATURE_COMPACT_UNPOWERED_REVIEW_20261011",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "changed_paths": [
        "docs/temperature_rise_tool.md",
        "frontend/src/features/temperature/sourceScan.test.ts",
        "frontend/src/features/temperature/sourceScan.ts",
        "frontend/src/pages/TemperatureRisePage.test.tsx",
        "frontend/src/pages/TemperatureRisePage.tsx"
      ],
      "scope_ok": true,
      "task_id": "TASK_TEMPERATURE_COMPACT_UNPOWERED_REVIEW_20261011",
      "version": 1,
      "subject": "1b303c56f9bcdcf91d1c7d8186ba1af0e5f9c854",
      "summary": "Shortened unpowered warnings and compacted ascending consecutive A-column scan IDs into ranges such as Scan 51~53. Preserves raw issues, severity, selection/exclusion and acknowledgement; gaps/duplicate/non-numeric/reset IDs and intervening issues stay separate.",
      "validation": [
        {
          "status": "passed",
          "name": "affected frontend matrix",
          "tests": 81,
          "command": "npm test -- src/features/temperature/sourceScan.test.ts src/pages/TemperatureRisePage.test.tsx src/features/temperature/DataPreview.test.tsx src/api/temperature.test.ts"
        },
        {
          "status": "passed",
          "name": "production build",
          "command": "npm run build"
        },
        {
          "status": "passed",
          "name": "diff whitespace",
          "command": "git diff --cached --check"
        }
      ],
      "schema": "connlab.sol-task-report",
      "integration": {
        "method": "Scoped local clean master commit; no remote publication",
        "status": "passed"
      },
      "roles": {
        "qa": {
          "status": "passed",
          "method": "Same-agent targeted affected frontend matrix and sequential build",
          "limitations": "Text-only presentation mapping proven at rendered-page seam; no browser run, backend/source/threshold/numerical code unchanged."
        },
        "reviewer": {
          "status": "passed",
          "standards_outstanding": 0,
          "method": "Sequential same-agent Standards and Spec self-review",
          "independent": false,
          "spec_outstanding": 0
        },
        "developer": {
          "method": "Micro task same-agent TDD: page-level range regression failed before implementation, passed afterward; nine formatter boundary cases and rendered confirmation/selection regression.",
          "status": "passed"
        }
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_EFFECTIVE_COLUMN_GROUPING_20261009",
    "tier": "standard",
    "subject": "c4d33bb9814d3569454e31f51944949055707365",
    "summary": "Normalize temperature editor columns and preserve sample groups through balanced exclusions",
    "disposition": "completed",
    "decision_ref": "User final authorization: 关闭任务",
    "closed_at": "2026-10-11T01:53:26.982199Z"
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
