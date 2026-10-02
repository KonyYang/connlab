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
    "task_id": "TASK_CREATE_FOLDER_ARCHIVE_ONLY_20261002",
    "summary": "Unify Create folder as reviewed whole-folder archive and fresh authority generation",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Create a missing official folder; existing verified sole owned folder requires whole-folder archive confirmation and fresh generation from templates and latest confirmed authorities. Remove content-based update/rename/rebind choices from the Create folder entry. Preserve legacy persisted-operation recovery, ownership/path/concurrency/lock safeguards and unrelated User work.",
    "scope_paths": [
      "docs/PROJECT_CONTEXT.md",
      "docs/plans/REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md",
      "docs/plans/REPORT_AUTOMATION_VBA_REFERENCE_MAP.md",
      "docs/plans/REPORT_RESULT_PHOTO_AUTOMATION_DESIGN.md",
      "docs/project_folder_generation_recovery.md",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts"
    ],
    "risk_reasons": [
      "Changes initiation of authoritative external folder archival and replacement"
    ],
    "activation_head": "3f8aac97e5c12b528ad5b5cdc88ed533aa4b5d32",
    "started_at": "2026-10-02T12:05:08.026304Z",
    "updated_at": "2026-10-02T12:57:46.087847Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_CREATE_FOLDER_ARCHIVE_ONLY_20261002",
      "stage": "scope_manifest_correction",
      "status": "running",
      "summary": "User approved on 2026-10-02 only board-manifest correction to record three existing design-document deletions from separate commit ba5a7d77. Do not edit, restore, or recommit those documents; six-file product commit 818de002 unchanged.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_CREATE_FOLDER_IR_DWV_RECORDS_20261002",
    "tier": "high_risk",
    "subject": "0b1f58320e01be1cbaa32da1a8491e4d7bc152fa",
    "summary": "Generate IR/DWV blank records in the Create folder workflow and disclose generated files",
    "disposition": "completed",
    "decision_ref": "User final Close 2026-10-02 after generated-file list removal delivery; retain disclosed business-folder occupancy/retry limitation and preserve unrelated design document.",
    "closed_at": "2026-10-02T11:08:38.105836Z"
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
