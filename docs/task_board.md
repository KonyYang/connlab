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
    "task_id": "TASK_LIGHTWEIGHT_PARALLEL_TASKS",
    "summary": "Support one main task and one isolated micro task with serial integration.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Task workflow scripts, rules and isolated governance tests only.",
    "scope_paths": [
      "scripts/connlab_sol_task.py",
      "scripts/connlab_parallel_task.py",
      "scripts/run_task.ps1",
      "scripts/connlab_publish_closed_task.py",
      "tests/unit/test_connlab_parallel_tasks.py",
      "tests/unit/test_connlab_sol_native_workflow.py",
      "tests/unit/test_connlab_publish_closed_task.py",
      "AGENTS.md",
      "docs/project_management/SOL_NATIVE_WORKFLOW.md",
      "docs/project_management/GPT6_ASTRA_USAGE_GUIDE.md",
      "docs/task_board.md"
    ],
    "risk_reasons": [],
    "activation_head": "7d6dc4309ffae05230792295c0c813ff12b5dd7d",
    "started_at": "2026-09-28T00:22:03.154248Z",
    "updated_at": "2026-09-28T00:44:15.591607Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_LIGHTWEIGHT_PARALLEL_TASKS",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_LIGHTWEIGHT_PARALLEL_TASKS",
      "subject": "4813c4a45217fd8c195df9427a90434a270597f8",
      "summary": "Implemented opt-in main plus micro task slots, shared board identity/lock, serial integration, isolated lifecycle and safe close publication. Legacy tasks remain compatible; no business changes or push.",
      "scope_ok": true,
      "changed_paths": [
        "AGENTS.md",
        "docs/project_management/GPT6_ASTRA_USAGE_GUIDE.md",
        "docs/project_management/SOL_NATIVE_WORKFLOW.md",
        "scripts/connlab_parallel_task.py",
        "scripts/connlab_publish_closed_task.py",
        "scripts/connlab_sol_task.py",
        "scripts/connlab_task_close.py",
        "scripts/run_task.ps1",
        "tests/unit/test_connlab_parallel_tasks.py",
        "tests/unit/test_connlab_sol_native_workflow.py"
      ],
      "validation": [
        {
          "name": "59 workflow, parallel lifecycle and publication tests on isolated repositories/local bare remotes",
          "status": "passed",
          "duration_seconds": 94.93
        },
        {
          "name": "git diff --check",
          "status": "passed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "TDD slices and implementation; exact final affected checks passed."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Same-agent separate Standards and Spec passes: no unresolved findings; not an independent agent review."
        },
        "qa": {
          "status": "passed",
          "summary": "Same-agent final clean-subject QA: 59 passed in 94.93s; no product/Office/frontend tests needed."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "direct_primary",
        "summary": "Only workflow scripts/rules/tests changed; local commits only; parallel upgrade deferred to next idle isolated Submit."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_TEST_POINTS_SINGLE_AUTHORITY",
    "tier": "high_risk",
    "subject": "7b782f92e0025b5b2fd8073bde7be98e89b91aeb",
    "summary": "Unify Test points draft/confirmation with Matrix authority and safely publish LLCR/CR forms to project Test results.",
    "disposition": "completed",
    "decision_ref": "User requested 关闭 after accepting the Test points simplification.",
    "closed_at": "2026-09-28T00:17:23.833487Z"
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
