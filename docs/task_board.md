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
    "task_id": "TASK_PROJECT_FOLDER_LEGACY_RECOVERY_REVIEW",
    "summary": "Repair project folder generation review, stale legacy path recovery, template guidance, and safely blocked checkpoints without overwriting operator files.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Project Folder preview, review and guarded regeneration for legacy workspaces; safe path reconciliation and checkpoint handling; no direct mutation of real operator folders or databases during validation.",
    "scope_paths": [
      "backend/api/project_folder_generation_composition.py",
      "backend/api/project_folder_preflight.py",
      "backend/api/routes_project_folder_generation.py",
      "backend/api/routes_official_project_workspace.py",
      "backend/api/routes_public_folder_workflow.py",
      "backend/api/routes_folder.py",
      "backend/application/project_folder_generation_service.py",
      "backend/application/official_project_workspace_service.py",
      "backend/application/project_folder_required_forms_service.py",
      "backend/application/public_folder_workflow_service.py",
      "backend/application/project_folder_open_service.py",
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchExecutionConsole.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx",
      "frontend/src/features/project-workbench/projectFolderTaskSelectors.ts",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
      "tests/unit/test_official_project_workspace_service.py",
      "tests/unit/test_project_folder_required_forms_service.py",
      "tests/unit/test_project_folder_open_service.py",
      "tests/unit/test_project_folder_generation_service.py",
      "tests/unit/test_generation_workspace_recovery.py",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_official_project_workspace_api.py",
      "tests/integration/test_project_folder_open_api.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "frontend/src/features/project-workbench/useProjectFolderGeneration.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts",
      "docs/project_folder_generation_recovery.md",
      "docs/PROJECT_CONTEXT.md",
      "docs/packaging_notes.md"
    ],
    "risk_reasons": [
      "authoritative external project folder and output mutation",
      "durable generation checkpoint recovery",
      "legacy workspace identity reconciliation"
    ],
    "activation_head": "9b4335e36178032eb03bf1bdcf29131ae033f542",
    "started_at": "2026-09-23T23:07:13.579991Z",
    "updated_at": "2026-09-23T23:07:13.579991Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_EQUIPMENT_CALIBRATION_MANUFACTURER_HEADER_MATCH",
    "tier": "micro",
    "subject": "ef79e24d56c87ed6ebcf72ec59375a245ab4ac32",
    "summary": "Accept the legacy equipment workbook Manufacturer header when the configured third header cell contains Manufacturer plus a vendor annotation, while retaining the fixed All Equip. layout and other required headers.",
    "disposition": "completed",
    "decision_ref": "user-close-2026-09-24",
    "closed_at": "2026-09-23T16:23:29.237335Z"
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
