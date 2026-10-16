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
    "task_id": "TASK_EXISTING_PROJECT_INTAKE_20261015",
    "summary": "Existing project in-place intake, workspace visibility and recoverable bulk registry management",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Implement first usable increment: isolated workspace visibility; bounded multiple-root discovery and reviewed identity/conflict-aware in-place directory registration; safe project-linked browsing/opening and relocation; recoverable bulk registry moves. No source file mutation, real business database migration, external LTR write, full database merge, push or deployment.",
    "scope_paths": [
      "docs/plans/EXISTING_PROJECT_INTAKE_20261015.md",
      "backend/application/existing_project_service.py",
      "backend/application/workspace_info_service.py",
      "backend/application/project_registry_management_service.py",
      "backend/infrastructure/files/existing_project_gateway.py",
      "backend/infrastructure/storage/models_existing_project.py",
      "backend/infrastructure/storage/repositories/existing_project.py",
      "backend/infrastructure/storage/repositories/project_registry.py",
      "backend/infrastructure/storage/database.py",
      "backend/infrastructure/workspace_info.py",
      "backend/api/routes_existing_projects.py",
      "backend/api/routes_workspace.py",
      "backend/api/routes_project_registry_management.py",
      "backend/api/main.py",
      "frontend/src/api/existingProjects.ts",
      "frontend/src/api/projectRegistryManagement.ts",
      "frontend/src/features/projects-registry/ExistingProjectsPanel.tsx",
      "frontend/src/features/projects-registry/ExistingProjectsPanel.test.tsx",
      "frontend/src/features/projects-registry/ExistingProjectFilesPanel.tsx",
      "frontend/src/features/projects-registry/ExistingProjectFilesPanel.test.tsx",
      "frontend/src/features/projects-registry/ProjectRegistryBatchPanel.tsx",
      "frontend/src/features/projects-registry/ProjectRegistryBatchPanel.test.tsx",
      "frontend/src/features/projects-registry/ProjectRegistryManagementPanel.tsx",
      "frontend/src/features/settings/WorkspaceInfoPanel.tsx",
      "frontend/src/features/settings/WorkspaceInfoPanel.test.tsx",
      "frontend/src/pages/ProjectListPage.tsx",
      "frontend/src/pages/SettingsPage.tsx",
      "frontend/src/pages/ProjectWorkbenchPage.tsx",
      "frontend/src/project-dashboard.css",
      "frontend/src/settings.css",
      "tests/unit/test_existing_project_service.py",
      "tests/unit/test_existing_project_gateway.py",
      "tests/unit/test_workspace_info_service.py",
      "tests/unit/test_project_registry_management_service.py",
      "tests/integration/test_existing_projects_api.py",
      "tests/integration/test_project_registry_management_api.py",
      "tests/integration/test_workspace_info_api.py",
      "tests/unit/test_database.py"
    ],
    "risk_reasons": [
      "Additive local metadata schema and project identity/conflict handling",
      "Recoverable registry transitions and filesystem path safety"
    ],
    "activation_head": "0d9b62a4a98fa999332d3ca19d49f8f8e8a8e8c9",
    "started_at": "2026-10-15T23:37:52.148882Z",
    "updated_at": "2026-10-16T04:58:14.944629Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_EXISTING_PROJECT_INTAKE_20261015",
      "stage": "qa",
      "status": "blocked",
      "summary": "Reviewed UI correction committed at 0f92c00c; 29 targeted tests and tsc passed, independent Reviewer Standards 0/Spec 0. Original full Python: 3601 passed/3 environment-conflict failures/9 skipped/19 deselected, exact 3 clean-environment rechecks passed; original frontend 968 passed/1 skipped plus build precedes correction. Final Temp-source Python gate and final original-repo Frontend gate were each denied before any process; both stopped with zero retries. Full successful Python and final frontend/build/UI acceptance remain incomplete. Real first-build UI evidence and 8 unchanged source files retained, owned browser/service stopped. Exact commands/reasons/isolation are in plan. No finish/Close/push/release or business-data writes.",
      "requires_user": true
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_LOCAL_REGISTRATION_TEMPERATURE_SAMPLES_20261014",
    "tier": "high_risk",
    "subject": "407d303cb93793f31904119181eef5e7dc3921e5",
    "summary": "Local offline account registration remembered login and adjustable temperature sample grouping",
    "disposition": "completed",
    "decision_ref": "User explicitly closes successfully completed login-free leader profile, real proxy save refinement and sample grouping task on 2026-10-15.",
    "closed_at": "2026-10-14T16:33:01.486252Z"
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
