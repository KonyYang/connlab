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
    "task_id": "TASK_LEGACY_PROJECT_REGISTRATION_20261019",
    "summary": "Register selected legacy project folders for search and browse in place",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Implement approved minimum formal registration: preview selection and confirmation, conflict-aware idempotent batch registration, dedicated historical records and Projects Legacy view/search/detail/Open Folder/Change Location. Read-only originals; test writes only in isolated databases. No business data or original folder mutation, push, publication, formal lifecycle/LTR/Matrix authority recovery.",
    "scope_paths": [
      "backend/application/legacy_project_registration_service.py",
      "backend/infrastructure/storage/models_legacy_projects.py",
      "backend/infrastructure/storage/repositories/legacy_projects.py",
      "backend/api/routes_legacy_projects.py",
      "backend/api/routes_tools_legacy_projects.py",
      "backend/infrastructure/storage/database.py",
      "backend/api/main.py",
      "backend/application/legacy_project_preview_service.py",
      "backend/infrastructure/files/legacy_project_preview_gateway.py",
      "frontend/src/api/legacyProjects.ts",
      "frontend/src/features/legacy-projects/LegacyProjectPreview.tsx",
      "frontend/src/features/legacy-projects/LegacyProjectBrowser.tsx",
      "frontend/src/features/legacy-projects/LegacyProjectList.tsx",
      "frontend/src/features/legacy-projects/legacy-project-preview.css",
      "frontend/src/pages/ProjectListPage.tsx",
      "frontend/src/App.tsx",
      "tests/unit/test_legacy_project_registration_service.py",
      "tests/unit/test_legacy_project_registration_repository.py",
      "tests/unit/test_legacy_project_registration_schema.py",
      "tests/integration/test_legacy_project_registration_api.py",
      "tests/integration/test_tools_legacy_projects_api.py",
      "frontend/src/features/legacy-projects/LegacyProjectPreview.test.tsx",
      "frontend/src/features/legacy-projects/LegacyProjectBrowser.test.tsx",
      "frontend/src/features/legacy-projects/LegacyProjectList.test.tsx",
      "frontend/src/pages/ProjectListPage.test.tsx",
      "frontend/src/App.test.tsx",
      "docs/plans/LEGACY_PROJECT_REGISTRATION_20261019.md",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [
      "Additive database schema and durable registration",
      "Concurrency/idempotency and conflict ownership across existing project records"
    ],
    "activation_head": "54b7f21d41b638809a69309e1b9ce79511d1550c",
    "started_at": "2026-10-18T23:42:11.482255Z",
    "updated_at": "2026-10-18T23:42:11.482255Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_CURRENT_DECIMALS_20261017",
    "tier": "standard",
    "subject": "a75e77dc958c6074f382cb4f8a27a8eed3465615",
    "summary": "Unified current decimal precision for temperature zero detection calculations charts and Excel export",
    "disposition": "completed",
    "decision_ref": "User explicitly requested final task closure after accepted temperature workspace and sidebar navigation delivery.",
    "closed_at": "2026-10-18T23:36:18.543559Z"
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
