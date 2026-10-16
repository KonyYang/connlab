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
    "task_id": "TASK_EXISTING_PROJECT_INTAKE_20261015",
    "summary": "Existing project in-place intake, workspace visibility and recoverable bulk registry management",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Implement first usable increment: isolated workspace visibility; bounded multiple-root discovery and reviewed identity/conflict-aware in-place directory registration; safe project-linked browsing/opening and relocation; recoverable bulk registry moves. No source file mutation, real business database migration, external LTR write, full database merge, push or deployment.",
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
      "frontend/src/pages/IntakeInboxPage.test.tsx",
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
      "Additive local metadata schema and project identity/conflict handling",
      "Recoverable registry transitions and filesystem path safety"
    ],
    "activation_head": "0d9b62a4a98fa999332d3ca19d49f8f8e8a8e8c9",
    "started_at": "2026-10-15T23:37:52.148882Z",
    "updated_at": "2026-10-16T22:39:09.984124Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_EXISTING_PROJECT_INTAKE_20261015",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_EXISTING_PROJECT_INTAKE_20261015",
      "subject": "7c9c1b22fcc6f00eae4b741b8987f3317e838aab",
      "summary": "Existing-project intake final acceptance complete. Approved inbox test readiness corrected with all assertions retained. Full non-Office Python, complete frontend with maximum two workers, sequential typecheck/build, isolated UI and final independent integration passed. No business data changes, Close, push or publication.",
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
        "frontend/src/pages/IntakeInboxPage.test.tsx",
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
          "name": "complete_non_office_python",
          "status": "passed",
          "result": "3604 passed, 9 skipped, 19 Office deselected, 2 warnings; exit 0; 728.42s. Retained Temp export, all 1036 inputs unchanged; Python Git inputs unchanged through subject."
        },
        {
          "name": "approved_inbox_test",
          "status": "passed",
          "result": "16 passed in 5.53s; every original assertion retained; independent focused review Standards 0 / Spec 0."
        },
        {
          "name": "complete_frontend",
          "status": "passed",
          "result": "974 passed, 1 existing profiling skip; 106 files passed, 1 skipped; 127.60s; exact executable inputs at 986d6933 unchanged through subject. VITEST_MAX_FORKS/MAX_THREADS=2, MIN_FORKS/MIN_THREADS=1; definitions, timeouts and assertions unchanged. Default-worker failures and focused 52 passing tests retained in plan."
        },
        {
          "name": "typecheck_build",
          "status": "passed",
          "result": "Same complete frontend runner executed tsc -b then Vite build: 189 modules, 1.32s; exit 0."
        },
        {
          "name": "isolated_ui_and_source_protection",
          "status": "passed",
          "result": "Real final UI synchronization, failure/retry and stale response acceptance passed. Current 36 dist files identical to actual accepted build; all product inputs unchanged. Eight fixture inventory/hash checks unchanged; owned browser/backend stopped, 18765 no listener."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "evidence": "Retained independent Planner completion recorded in existing plan implementation checkpoint at 67be4caf; no repeated planning."
        },
        "developer": {
          "status": "passed",
          "evidence": "Retained implementation at 67be4caf and reviewed correction 0f92c00c; root applied only explicitly approved test readiness correction 9c30a6fb with existing RED and 16 passing targeted tests."
        },
        "reviewer": {
          "status": "passed",
          "evidence": "Retained original independent review Standards 0 / Spec 0; incremental independent /root/review_test_readiness reports Standards 0 / Spec 0 on the approved test."
        },
        "qa": {
          "status": "passed",
          "evidence": "Independent /root/qa_python full non-Office gate and /root/qa_frontend_ui full frontend with max two workers, sequential build, real isolated UI and postbuild integrity checks. Default-concurrency reliability is not claimed."
        },
        "integrator": {
          "status": "passed",
          "evidence": "Independent /root/integrator verified exact 7c9c1b22 subject, parent/tree/clean master, exact 39-path scope, logs and hashes, input-equivalent Python/UI acceptance and data protection. No integration blocker."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "7c9c1b22fcc6f00eae4b741b8987f3317e838aab",
        "method": "Existing legacy local-master linear integration; independently verified; no remote action.",
        "publication": "Forbidden by this task; no Close, push, release or deployment."
      }
    }
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
