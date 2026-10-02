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
  "state": "running",
  "active": {
    "task_id": "TASK_BASIC_INFORMATION_CONFIRM_CHANGES_20261002",
    "summary": "Load confirmed Basic Information on entry and confirm only material changes",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Normal entry uses latest confirmed Basic Information. Refresh recovers saved current-session editing without deleting old drafts. Disable Confirm for unchanged confirmed content; re-enable for material field or source/sample changes. First confirmation remains available after validation. Backend repeated identical confirmation is idempotent. Preserve lifecycle/validation/source review and external output behavior.",
    "scope_paths": [
      "frontend/src/App.tsx",
      "frontend/src/App.test.tsx",
      "frontend/src/features/project-basic-information",
      "backend/application/project_basic_information_service.py",
      "tests/unit/test_project_basic_information_service.py",
      "tests/integration/test_project_basic_information_api.py",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "10ae47c7c5b69a6d94c6c23a87c42ccf3c56e705",
    "started_at": "2026-10-02T13:33:29.361899Z",
    "updated_at": "2026-10-02T13:33:29.361899Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_CREATE_FOLDER_ARCHIVE_ONLY_20261002",
    "tier": "high_risk",
    "subject": "0ed750d81cfc37de9e836058457660b879bc02e6",
    "summary": "Unify Create folder as reviewed whole-folder archive and fresh authority generation",
    "disposition": "completed",
    "decision_ref": "User final Close on 2026-10-02 after approved scope-record correction and ready_for_close delivery. Retain disclosed installed Office COM and packaged-release validation limitations.",
    "closed_at": "2026-10-02T13:19:32.461244Z"
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
