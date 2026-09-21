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
    "task_id": "TASK_PROJECT_FOLDER_DATA_PROTECTION_ADOPTION",
    "summary": "Protect existing project folders by separating identity-only adoption and healthy-folder opening from explicit backup rebuild operations, including portable cross-PC rebinding without modifying business files.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Implement identity-only existing-folder adoption, portable same-project rebinding, non-hashing normal preview, safe UI actions, and backup-only advanced rebuild while preserving historical journal recovery compatibility.",
    "scope_paths": [
      "backend/api/project_folder_generation_composition.py",
      "backend/api/routes_official_project_workspace.py",
      "backend/api/routes_project_folder_generation.py",
      "backend/application/official_project_workspace_service.py",
      "backend/application/project_folder_generation_service.py",
      "backend/infrastructure/official_workspace_manifest.py",
      "docs/PROJECT_CONTEXT.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx",
      "frontend/src/features/report-workspace/useCustomerReportJob.ts",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "tests/integration/test_official_project_workspace_api.py",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/unit/test_generation_workspace_recovery.py",
      "tests/unit/test_official_project_workspace_service.py",
      "tests/unit/test_project_folder_generation_service.py"
    ],
    "risk_reasons": [
      "authoritative external filesystem mutation",
      "cross-PC project identity recovery",
      "destructive rebuild entry separation",
      "broad backend and frontend workflow change"
    ],
    "activation_head": "5426711281450466fc1ca25cea861f0d177e5dce",
    "started_at": "2026-09-21T14:27:11.502060Z",
    "updated_at": "2026-09-21T23:48:53.638766Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_DATA_PROTECTION_ADOPTION",
      "stage": "scope_manifest_correction",
      "status": "running",
      "summary": "user-approved-report-workspace-elapsed-fix-2026-09-22",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_CUSTOMER_REPORT_LONG_PATH_REPAIR",
    "tier": "standard",
    "subject": "25b68d6d363df5b98b7d31946ba4a311810f07ae",
    "summary": "Prevent customer-report generation from passing long official project-report paths directly to Microsoft Word by using a short controlled working copy while preserving source-authority checks and publication behavior.",
    "disposition": "completed",
    "decision_ref": "user-close-2026-09-21",
    "closed_at": "2026-09-21T11:22:49.206818Z"
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
