# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> WIP=1. GPT-5.6 Sol routes work as micro, standard, or high risk and runs routine stages
> automatically until the User's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_CLOSE_AUTO_PUBLISH_GATE",
    "summary": "Publish completed tasks to origin/master through a fail-closed post-Close Git gate after the board close commit.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Add a small closed-task publication module and connect only completed terminal Close to exact board commit plus ordinary fast-forward GitHub push; exclude cancellation and CloseAndSubmit; never force, rebase, reset, stash, or clean.",
    "scope_paths": [
      "AGENTS.md",
      "docs/project_management/SOL_NATIVE_WORKFLOW.md",
      "scripts/connlab_publish_closed_task.py",
      "scripts/run_task.ps1",
      "tests/unit/test_connlab_publish_closed_task.py",
      "tests/unit/test_connlab_sol_native_workflow.py",
      "docs/task_board.md"
    ],
    "risk_reasons": [
      "remote GitHub mutation",
      "workflow authority change",
      "automatic Git commit and push after explicit user Close"
    ],
    "activation_head": "b48b50ca5f58fa75e68bfd61a7471f65cdb78236",
    "started_at": "2026-09-22T00:05:34.866806Z",
    "updated_at": "2026-09-22T00:05:34.866806Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_DATA_PROTECTION_ADOPTION",
    "tier": "high_risk",
    "subject": "c5bbe88c82d247773a2aaba9783b0c4ea7aab0dd",
    "summary": "Protect existing project folders by separating identity-only adoption and healthy-folder opening from explicit backup rebuild operations, including portable cross-PC rebinding without modifying business files.",
    "disposition": "completed",
    "decision_ref": "user-close-2026-09-22",
    "closed_at": "2026-09-21T23:58:33.839550Z"
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
