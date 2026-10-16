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
    "task_id": "TASK_WITHDRAW_EXISTING_PROJECT_INTAKE_20261017",
    "summary": "Withdraw rejected existing-project intake increment and preserve original registry operations",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Restore exactly the 38 non-board paths of 67be4caf to baseline 0d9b62a4, including removal of later in-scope refinements. Preserve three pure test-readiness fixes, original Delete/Trash/history, Git history and all real data. No new import implementation, push or publication.",
    "scope_paths": [
      "backend/api/main.py",
      "backend/api/routes_existing_projects.py",
      "backend/api/routes_project_registry_management.py",
      "backend/api/routes_workspace.py",
      "backend/application/existing_project_service.py",
      "backend/application/project_registry_management_service.py",
      "backend/application/workspace_info_service.py",
      "backend/infrastructure/files/existing_project_gateway.py",
      "backend/infrastructure/storage/database.py",
      "backend/infrastructure/storage/models_existing_project.py",
      "backend/infrastructure/storage/repositories/existing_project.py",
      "backend/infrastructure/storage/repositories/project_registry.py",
      "backend/infrastructure/workspace_info.py",
      "docs/plans/EXISTING_PROJECT_INTAKE_20261015.md",
      "frontend/src/api/existingProjects.ts",
      "frontend/src/api/projectRegistryManagement.ts",
      "frontend/src/features/projects-registry/ExistingProjectFilesPanel.test.tsx",
      "frontend/src/features/projects-registry/ExistingProjectFilesPanel.tsx",
      "frontend/src/features/projects-registry/ExistingProjectsPanel.test.tsx",
      "frontend/src/features/projects-registry/ExistingProjectsPanel.tsx",
      "frontend/src/features/projects-registry/ProjectRegistryBatchPanel.test.tsx",
      "frontend/src/features/projects-registry/ProjectRegistryBatchPanel.tsx",
      "frontend/src/features/projects-registry/ProjectRegistryManagementPanel.tsx",
      "frontend/src/features/settings/WorkspaceInfoPanel.test.tsx",
      "frontend/src/features/settings/WorkspaceInfoPanel.tsx",
      "frontend/src/pages/ProjectListPage.tsx",
      "frontend/src/pages/ProjectWorkbenchPage.tsx",
      "frontend/src/pages/SettingsPage.tsx",
      "frontend/src/project-dashboard.css",
      "frontend/src/settings.css",
      "tests/integration/test_existing_projects_api.py",
      "tests/integration/test_project_registry_management_api.py",
      "tests/integration/test_workspace_info_api.py",
      "tests/unit/test_database.py",
      "tests/unit/test_existing_project_gateway.py",
      "tests/unit/test_existing_project_service.py",
      "tests/unit/test_project_registry_management_service.py",
      "tests/unit/test_workspace_info_service.py"
    ],
    "risk_reasons": [
      "Cross-layer feature withdrawal removes additive storage-model registration; verify no schema downgrade, real database mutation or loss of original registry behavior."
    ],
    "activation_head": "f7faf5cc00e6812b1531ab04283a19564f214eda",
    "started_at": "2026-10-16T23:30:39.233997Z",
    "updated_at": "2026-10-16T23:42:35.634942Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_WITHDRAW_EXISTING_PROJECT_INTAKE_20261017",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_WITHDRAW_EXISTING_PROJECT_INTAKE_20261017",
      "subject": "154a0f394a53d500ea512bd21b56dd09387411e0",
      "summary": "Withdraw all rejected existing-project intake product changes across 38 paths; retain original Delete/Trash/History and three independent test stability fixes. Product tree equals 0d9b62a4. No new import implementation, real business-data mutation, push or publication.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/main.py",
        "backend/api/routes_existing_projects.py",
        "backend/api/routes_project_registry_management.py",
        "backend/api/routes_workspace.py",
        "backend/application/existing_project_service.py",
        "backend/application/project_registry_management_service.py",
        "backend/application/workspace_info_service.py",
        "backend/infrastructure/files/existing_project_gateway.py",
        "backend/infrastructure/storage/database.py",
        "backend/infrastructure/storage/models_existing_project.py",
        "backend/infrastructure/storage/repositories/existing_project.py",
        "backend/infrastructure/storage/repositories/project_registry.py",
        "backend/infrastructure/workspace_info.py",
        "docs/plans/EXISTING_PROJECT_INTAKE_20261015.md",
        "frontend/src/api/existingProjects.ts",
        "frontend/src/api/projectRegistryManagement.ts",
        "frontend/src/features/projects-registry/ExistingProjectFilesPanel.test.tsx",
        "frontend/src/features/projects-registry/ExistingProjectFilesPanel.tsx",
        "frontend/src/features/projects-registry/ExistingProjectsPanel.test.tsx",
        "frontend/src/features/projects-registry/ExistingProjectsPanel.tsx",
        "frontend/src/features/projects-registry/ProjectRegistryBatchPanel.test.tsx",
        "frontend/src/features/projects-registry/ProjectRegistryBatchPanel.tsx",
        "frontend/src/features/projects-registry/ProjectRegistryManagementPanel.tsx",
        "frontend/src/features/settings/WorkspaceInfoPanel.test.tsx",
        "frontend/src/features/settings/WorkspaceInfoPanel.tsx",
        "frontend/src/pages/ProjectListPage.tsx",
        "frontend/src/pages/ProjectWorkbenchPage.tsx",
        "frontend/src/pages/SettingsPage.tsx",
        "frontend/src/project-dashboard.css",
        "frontend/src/settings.css",
        "tests/integration/test_existing_projects_api.py",
        "tests/integration/test_project_registry_management_api.py",
        "tests/integration/test_workspace_info_api.py",
        "tests/unit/test_database.py",
        "tests/unit/test_existing_project_gateway.py",
        "tests/unit/test_existing_project_service.py",
        "tests/unit/test_project_registry_management_service.py",
        "tests/unit/test_workspace_info_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Exact rollback",
          "result": "15 modified paths byte-identical to baseline; 23 added paths removed; only three independent tests, prior flake evidence and task board differ from baseline."
        },
        {
          "status": "passed",
          "name": "Affected Python matrix",
          "result": "58 passed across 9 database/registry/repository/lifecycle files in isolated exported source; one existing deprecation warning. Full unrelated Python and Office not rerun."
        },
        {
          "status": "passed",
          "name": "Complete default-worker frontend",
          "result": "956 passed / 1 existing opt-in profiling skipped; 102 files passed / 1 skipped; 45.88s."
        },
        {
          "status": "passed",
          "name": "Sequential typecheck and production build",
          "result": "tsc -b passed; Vite 184 modules / 1.57s."
        },
        {
          "status": "passed",
          "name": "Temporary database preservation",
          "result": "Two init_db runs retain original project and extra existing_project_locations table and sentinel row."
        },
        {
          "status": "passed",
          "name": "Isolated UI",
          "result": "Delete -> Trash -> Restore; History; removed new panels; original Settings and four Tools entries preserved. Console zero errors/warnings. Owned browser/backend stopped, port 18765 closed."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "agent": "/root/rollback_planner"
        },
        "developer": {
          "status": "passed",
          "agent": "/root/rollback_developer"
        },
        "reviewer": {
          "status": "passed",
          "agent": "/root/rollback_reviewer",
          "standards_findings": 0,
          "spec_findings": 0
        },
        "qa": {
          "status": "passed",
          "agent": "/root/rollback_qa",
          "evidence": "C:\\Users\\White\\AppData\\Local\\Temp\\connlab-intake-rollback-20261017\\qa-final-result.json"
        },
        "integrator": {
          "status": "passed",
          "agent": "/root/rollback_integrator",
          "qa_report_sha256": "46903b8f22895e93055cff52215b0707d746eccab63e60a2d8028c59ea1c5805",
          "evidence": "Independent exact subject, scope, baseline, retained hash, QA artifacts and normalized exported backend/tests provenance verified."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "154a0f394a53d500ea512bd21b56dd09387411e0",
        "mode": "local linear history; no remote operations",
        "evidence": "Independent Integrator verified clean HEAD, parent f5e8aa98, exact 38-path allowlist, retained three test repairs, QA artifact hashes and source provenance. CRLF-only export normalization has no semantic difference."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FRONTEND_DEFAULT_CONCURRENCY_FLAKES_20261017",
    "tier": "standard",
    "subject": "fe2706b606633bb524e71426acfd8a72de1208bb",
    "summary": "Diagnose and minimally fix default-concurrency frontend test instability in point setup and Fee preview cancellation",
    "disposition": "completed",
    "decision_ref": "User explicitly closes this completed task on 2026-10-17, preserves all local commits, and forbids push or publication. Local-only close; publish-close is deliberately absent.",
    "closed_at": "2026-10-16T23:05:16.529887Z"
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
