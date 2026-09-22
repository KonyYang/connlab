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
    "task_id": "TASK_PROJECT_FOLDER_CREATE_REBUILD_ENTRY",
    "summary": "Separate project-folder opening from the Folder Actions header so the row icon remains the only Open action and the header handles Create folder or protected Backup and Rebuild.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Change the completed-workspace header action from Open folder to the reviewed Create folder backup-rebuild flow while preserving adoption, conflict review, recovery priority, read-only behavior, and existing backend data-protection contracts.",
    "scope_paths": [
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx"
    ],
    "risk_reasons": [
      "exposes authoritative external folder backup-and-rebuild entry",
      "must preserve recovery and read-only safety",
      "must not duplicate or bypass folder-open behavior"
    ],
    "activation_head": "9ad0edac21ad0d1b078de53f1521af1bb30e04e4",
    "started_at": "2026-09-22T09:42:38.241695Z",
    "updated_at": "2026-09-22T11:33:02.411865Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_CREATE_REBUILD_ENTRY",
      "stage": "scope_manifest_correction",
      "status": "running",
      "summary": "user-approved-workbench-model-test-2026-09-22",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_CLOSE_AUTO_PUBLISH_GATE",
    "tier": "high_risk",
    "subject": "83c7acf4c29e05a1d133490571c52769317235f3",
    "summary": "Publish completed tasks to origin/master through a fail-closed post-Close Git gate after the board close commit.",
    "disposition": "completed",
    "decision_ref": "user-close-2026-09-22",
    "closed_at": "2026-09-22T09:41:11.208201Z"
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
