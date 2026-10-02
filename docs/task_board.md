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
    "task_id": "TASK_CREATE_FOLDER_IR_DWV_RECORDS_20261002",
    "summary": "Generate IR/DWV blank records in the Create folder workflow and disclose generated files",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Extend existing confirmed-Matrix contact-record Create folder preflight and recoverable generation to IR/DWV; show generated-file readiness/skip/archive information in creation UI. Preserve existing LLCR/CR, names, authority and measured files; isolated validation only; no measurement-result import or report/photo automation.",
    "scope_paths": [
      "backend/api/project_folder_preflight.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/application/project_folder_generation_service.py",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "tests/unit/test_project_folder_generation_service.py",
      "docs/PROJECT_CONTEXT.md",
      "docs/project_folder_generation_recovery.md"
    ],
    "risk_reasons": [
      "authoritative external mutation"
    ],
    "activation_head": "d3aef5c9d2c01803f18d4dfdc0ea53e550377ad2",
    "started_at": "2026-10-02T08:47:00.592399Z",
    "updated_at": "2026-10-02T10:24:24.530324Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CREATE_FOLDER_IR_DWV_RECORDS_20261002",
      "stage": "revision",
      "status": "running",
      "requires_user": true,
      "summary": "Archive-access warning now asks users to close documents and File Explorer windows/tabs viewing the folder or subfolders before retrying Create folder, with a permissions fallback. Existing persisted legacy warning is mapped to the same guidance; complete diagnostic suffixes are collapsed. Independent Developer RED/GREEN and Reviewer passed; independent QA: Python service 20 passed, Layout 79 passed, sequential production build passed on frozen four-file state. Root read-only business browser check saw no current alert, so native warning display was not exercised. Original WinError 5 rename remains awaiting User closing matching Explorer window/tab, then original browser rebuild retry. Business files and unrelated design document unchanged."
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_REPORT_AUTOMATION_DOC_BASELINE_20261002",
    "tier": "micro",
    "subject": "2106e342e65b7c1d625aecfca6f8833247a0c355",
    "summary": "Reconcile three report automation documents with current ConnLab implementation",
    "disposition": "completed",
    "decision_ref": "User final Close 2026-10-02: three report automation documents reconciled, validated and committed.",
    "closed_at": "2026-10-02T08:35:36.218394Z"
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
