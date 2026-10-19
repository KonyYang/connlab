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
    "updated_at": "2026-10-19T00:10:41.769542Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_LEGACY_PROJECT_REGISTRATION_20261019",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_LEGACY_PROJECT_REGISTRATION_20261019",
      "subject": "683ce90fe6b7dfa0e14f638f7b2ba3522d2b214a",
      "summary": "Formal legacy registration implemented; scoped functional acceptance passed with documented exceptions. Full frontend not green: existing temperature timeout reproduced on activation. Real DB hash/schema changed while existing reload service ran; legacy table empty, real business-row preservation unproven. No source change, real import, push or publication.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/main.py",
        "backend/api/routes_legacy_projects.py",
        "backend/api/routes_tools_legacy_projects.py",
        "backend/application/legacy_project_preview_service.py",
        "backend/application/legacy_project_registration_service.py",
        "backend/infrastructure/files/legacy_project_preview_gateway.py",
        "backend/infrastructure/storage/database.py",
        "backend/infrastructure/storage/models_legacy_projects.py",
        "backend/infrastructure/storage/repositories/legacy_projects.py",
        "docs/PROJECT_CONTEXT.md",
        "docs/plans/LEGACY_PROJECT_REGISTRATION_20261019.md",
        "frontend/src/App.test.tsx",
        "frontend/src/App.tsx",
        "frontend/src/api/legacyProjects.ts",
        "frontend/src/features/legacy-projects/LegacyProjectBrowser.test.tsx",
        "frontend/src/features/legacy-projects/LegacyProjectBrowser.tsx",
        "frontend/src/features/legacy-projects/LegacyProjectList.test.tsx",
        "frontend/src/features/legacy-projects/LegacyProjectList.tsx",
        "frontend/src/features/legacy-projects/LegacyProjectPreview.test.tsx",
        "frontend/src/features/legacy-projects/LegacyProjectPreview.tsx",
        "frontend/src/features/legacy-projects/legacy-project-preview.css",
        "frontend/src/pages/ProjectListPage.test.tsx",
        "frontend/src/pages/ProjectListPage.tsx",
        "tests/integration/test_legacy_project_registration_api.py",
        "tests/integration/test_tools_legacy_projects_api.py",
        "tests/unit/test_legacy_project_registration_repository.py",
        "tests/unit/test_legacy_project_registration_schema.py",
        "tests/unit/test_legacy_project_registration_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Scoped Python behaviors",
          "result": "87 selected behaviors: original isolated matrix86 passed and1 QA-env default-path failure; same default-path test then passed alone without conflicting QA path env. Developer final38 passed after public-path fix."
        },
        {
          "status": "passed",
          "name": "Scoped frontend and build",
          "result": "All43 task-related cases passed in both full executions; corrected TypeScript project check passed; Vite195 modules passed. Full gate explicitly NOT PASSED:1006pass1fail1skip then1005pass2fail1skip; unchanged temperature test alone8pass and same first timeout reproduced on activation. Baseline export also omitted unrelated fee fixture; restored only in Temp and10 related tests passed."
        },
        {
          "status": "passed",
          "name": "Isolated real samples and browser acceptance",
          "result": "36 real candidates:29ready registered,29retry AlreadyAdded,7review wrote0 until explicit KeepSeparate then7added. All36details/search/fakeopen, offline/relocation/revision/ownership checks passed;67 isolated nonlegacy business tables unchanged. RootUI3 disposable records,2KeepSeparate,confirmcancel/confirm,duplicate禁选,list/search/detail/fakeopen/change location and retained query;1440/514 no document overflow; independent QA inspected captures/records. Owned18769 and root tab stopped."
        },
        {
          "status": "passed",
          "name": "Source inventory preservation",
          "result": "3442 source inventory entries and28 metadata hashes unchanged;5 other protected files unchanged. This excludes real connlab.sqlite3, whose hash/schema changed with zero legacy rows; no claim of real DB preservation."
        },
        {
          "status": "passed",
          "name": "Independent review and integration",
          "result": "Planner/Developer/Reviewer/QA/Integrator separate contexts. OneP2 public workflow path-ownership omission fixed and independently rechecked;0unresolved code review findings.28exact paths;clean linear local history;product bytes unchanged after tested3aa51f62;no push/publication."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "agent": "/root/legacy_import_planner",
          "independent": true,
          "scope": "Assigned independent role"
        },
        "developer": {
          "status": "passed",
          "agent": "/root/legacy_import_developer",
          "independent": true,
          "scope": "Assigned independent role"
        },
        "reviewer": {
          "status": "passed",
          "agent": "/root/legacy_import_reviewer",
          "independent": true,
          "scope": "Assigned independent role"
        },
        "qa": {
          "status": "passed",
          "agent": "/root/legacy_import_qa",
          "independent": true,
          "scope": "Task functional acceptance with disclosed full-suite/environment exceptions"
        },
        "integrator": {
          "status": "passed",
          "agent": "/root/legacy_import_integrator",
          "independent": true,
          "scope": "Assigned independent role"
        }
      },
      "integration": {
        "status": "passed",
        "subject": "683ce90fe6b7dfa0e14f638f7b2ba3522d2b214a",
        "tested_subject": "3aa51f62a439647851a182c217a02388a5256164",
        "overall_full_frontend": "not_passed",
        "real_database_preservation": "not_verified; real hash/schema changed; zero legacy rows",
        "result": "Integrator verified Git/scope/evidence consistency only; complete acceptance is not all-green. No real schema rollback, push, or publication."
      }
    }
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
