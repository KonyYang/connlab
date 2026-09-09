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
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_PROJECT_REGISTRY_RECOVERY",
    "summary": "Simplify project closure and implement recoverable project deletion, conflict-safe restore/history, and exclusion from active registries and work queues.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Local ConnLab only: compact conditional-note closure, trash/history/restore of independent project records, protected transitions and stale-request rejection, consistent list/lookup/count/task filtering, independent review and isolated tests. Preserve business data, LTR ownership, and external files. No purge, duplicate-create preflight, GitHub push, or live-project mutation tests.",
    "scope_paths": [
      "backend/domain/models.py",
      "backend/domain/enums.py",
      "backend/domain/__init__.py",
      "backend/infrastructure/storage/models.py",
      "backend/infrastructure/storage/database.py",
      "backend/infrastructure/storage/project_registry_schema_migration.py",
      "backend/infrastructure/storage/repositories/project.py",
      "backend/infrastructure/storage/repositories/project_registry.py",
      "backend/application/project_registry_management_service.py",
      "backend/application/project_registry_models.py",
      "backend/application/project_registry_summary_service.py",
      "backend/application/project_service.py",
      "backend/application/project_ltr_cleanup_audit_service.py",
      "backend/application/project_lifecycle_write_guard.py",
      "backend/application/project_lifecycle_state_service.py",
      "backend/application/project_folder_generation_service.py",
      "backend/api/project_registry_access_guard.py",
      "backend/api/routes_project_registry_management.py",
      "backend/api/routes_project.py",
      "backend/api/dependencies.py",
      "backend/api/main.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/api/routes_project_folder_generation.py",
      "backend/infrastructure/files/generation_journal.py",
      "frontend/src/api/client.ts",
      "frontend/src/api/projectRegistryManagement.ts",
      "frontend/src/pages/ProjectListPage.tsx",
      "frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts",
      "frontend/src/features/projects-registry/ProjectRegistryManagementDialog.tsx",
      "frontend/src/features/projects-registry/ProjectRegistryManagementPanel.tsx",
      "frontend/src/features/projects-registry/useProjectRegistryManagement.ts",
      "frontend/src/features/projects-registry/projectRegistryManagementModel.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx",
      "frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx",
      "frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts",
      "frontend/src/components/layout/AppShell.tsx",
      "frontend/src/App.tsx",
      "frontend/src/project-dashboard.css",
      "frontend/src/workbench.css",
      "frontend/src/runtime-projection-prototype.css",
      "docs/PROJECT_CONTEXT.md",
      "docs/project_registry_management.md",
      "tests/unit/test_project_registry_management_service.py",
      "tests/unit/test_project_registry_schema_migration.py",
      "tests/unit/test_project_registry_repository.py",
      "tests/unit/test_project_registry_summary_service.py",
      "tests/unit/test_project_ltr_cleanup_audit_service.py",
      "tests/unit/test_project_folder_generation_service.py",
      "tests/unit/test_project_lifecycle_state_service.py",
      "tests/unit/test_project_lifecycle_write_guard.py",
      "tests/unit/test_project_service.py",
      "tests/unit/test_database.py",
      "tests/integration/test_project_registry_management_api.py",
      "tests/integration/test_project_registry_summary_api.py",
      "tests/integration/test_project_lifecycle_gating_api.py",
      "tests/integration/test_project_lifecycle_api.py",
      "tests/integration/test_project_api.py",
      "tests/integration/test_project_registry_generation_lock.py",
      "frontend/src/pages/ProjectListPage.test.tsx",
      "frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts",
      "frontend/src/features/projects-registry/ProjectRegistryManagementDialog.test.tsx",
      "frontend/src/features/projects-registry/useProjectRegistryManagement.test.tsx",
      "frontend/src/features/projects-registry/projectRegistryManagementModel.test.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx",
      "frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts",
      "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
      "frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts"
    ],
    "risk_reasons": [
      "Additive database migration and project visibility transitions",
      "Restore conflict resolution across multiple independent project records",
      "Prevent hidden-project writes and concurrent background file generation"
    ],
    "activation_head": "f838a1a2787790edcb2c16f1146cda202147e59a",
    "started_at": "2026-09-08T23:48:19.113804Z",
    "updated_at": "2026-09-09T00:47:09.126312Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_REGISTRY_RECOVERY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_PROJECT_REGISTRY_RECOVERY",
      "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
      "summary": "Simplified conditional-note closure; added recoverable trash/history and conflict-safe restore, consistent registry/queue exclusion, guarded hidden-project writes and generation serialization. Independent review and final isolated QA passed; project records, LTR ownership and external bytes are preserved. No purge, duplicate-create feature, live-project mutation or GitHub push.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/main.py",
        "backend/api/project_registry_access_guard.py",
        "backend/api/routes_project.py",
        "backend/api/routes_project_registry_management.py",
        "backend/application/project_lifecycle_state_service.py",
        "backend/application/project_lifecycle_write_guard.py",
        "backend/application/project_ltr_cleanup_audit_service.py",
        "backend/application/project_registry_management_service.py",
        "backend/application/project_registry_models.py",
        "backend/application/project_registry_summary_service.py",
        "backend/domain/models.py",
        "backend/infrastructure/storage/database.py",
        "backend/infrastructure/storage/models.py",
        "backend/infrastructure/storage/project_registry_schema_migration.py",
        "backend/infrastructure/storage/repositories/project.py",
        "backend/infrastructure/storage/repositories/project_registry.py",
        "docs/PROJECT_CONTEXT.md",
        "docs/project_registry_management.md",
        "frontend/src/api/client.ts",
        "frontend/src/api/projectRegistryManagement.ts",
        "frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.test.ts",
        "frontend/src/features/project-lifecycle/projectLifecycleReadonlyModel.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx",
        "frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts",
        "frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts",
        "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx",
        "frontend/src/features/project-workbench/useProjectWorkbenchModel.ts",
        "frontend/src/features/projects-registry/ProjectRegistryManagementDialog.test.tsx",
        "frontend/src/features/projects-registry/ProjectRegistryManagementDialog.tsx",
        "frontend/src/features/projects-registry/ProjectRegistryManagementPanel.tsx",
        "frontend/src/features/projects-registry/projectRegistryLifecycleViews.test.ts",
        "frontend/src/features/projects-registry/projectRegistryLifecycleViews.ts",
        "frontend/src/features/projects-registry/useProjectRegistryManagement.test.tsx",
        "frontend/src/features/projects-registry/useProjectRegistryManagement.ts",
        "frontend/src/pages/ProjectListPage.test.tsx",
        "frontend/src/pages/ProjectListPage.tsx",
        "frontend/src/project-dashboard.css",
        "tests/integration/test_project_lifecycle_api.py",
        "tests/integration/test_project_lifecycle_gating_api.py",
        "tests/integration/test_project_registry_generation_lock.py",
        "tests/integration/test_project_registry_management_api.py",
        "tests/integration/test_project_registry_summary_api.py",
        "tests/unit/test_project_lifecycle_state_service.py",
        "tests/unit/test_project_ltr_cleanup_audit_service.py",
        "tests/unit/test_project_registry_management_service.py",
        "tests/unit/test_project_registry_schema_migration.py",
        "tests/unit/test_project_registry_summary_service.py"
      ],
      "validation": [
        {
          "name": "Final Python non-Office suite",
          "status": "passed",
          "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
          "result": "2676 passed (2645 main plus 31 isolated configuration tests), 4 skipped, 19 Office tests deselected. Existing duplicate OpenAPI Operation ID warning remains.",
          "evidence": [
            "logs/qa-project-registry-31c60ba1/final-d310a9ea/python-main.log",
            "logs/qa-project-registry-31c60ba1/final-d310a9ea/python-config.log"
          ]
        },
        {
          "name": "Final frontend tests",
          "status": "passed",
          "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
          "command": "npm.cmd test (vitest run)",
          "result": "79 test files and 518 tests passed; 1 file and 1 test skipped.",
          "evidence": "logs/qa-project-registry-31c60ba1/final-d310a9ea/frontend-test.log"
        },
        {
          "name": "TypeScript and production build",
          "status": "passed",
          "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
          "command": "npm.cmd run build (tsc -b && vite build)",
          "evidence": "logs/qa-project-registry-31c60ba1/final-d310a9ea/frontend-build.log"
        },
        {
          "name": "Isolated browser acceptance",
          "status": "passed",
          "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
          "result": "Close reason/optional note, 375px layout, keyboard focus/Escape; trash/list counts/closed-state preservation; every same-number conflict displayed by independent ID; cancellation unchanged; stale preview 409; history restore and atomic active/history swap; hidden write 409. All 4 LTR rows including ownership, 3 external file hashes and source references unchanged. Agent-owned tab and server closed.",
          "evidence": "logs/qa-project-registry-31c60ba1/qa-result.md",
          "limitations": "Minimal synthetic project omitted confirmed Matrix/fee authority and used a non-business-formatted LTR sentinel; existing auxiliary workbench reads warned. Those business-generation flows and Office COM were not claimed as browser coverage. Related automated suites passed."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "context": "/root/planner",
          "summary": "Independent plan fixed closure semantics, orthogonal registry states, atomic all-conflict restore, hidden-write protection and preservation boundaries."
        },
        "developer": {
          "status": "passed",
          "contexts": [
            "/root/backend_developer",
            "/root/frontend_developer",
            "/root"
          ],
          "summary": "Meaningful RED/GREEN for conditional closure, registry transitions, hidden direct/indirect access and stale previews. Backend targeted 81 passed before final QA repairs; repaired repository targets 32 passed. Frontend final 9 files/121 tests and tsc passed. Root access-guard final affected 32 passed. These are implementation feedback, not the final full QA result."
        },
        "reviewer": {
          "status": "passed",
          "context": "/root/reviewer",
          "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
          "summary": "Independent full feature diff review followed by independent four-file incremental review through d310a9ea; identified P2 issues and QA regressions fixed; no unresolved P1/P2. git diff --check passed."
        },
        "qa": {
          "status": "passed",
          "context": "/root/qa",
          "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
          "summary": "Final complete matrix and isolated browser acceptance passed. Initial 31c60ba1 QA failure was diagnosed and fixed; only corrected d310a9ea results are final evidence.",
          "report": "logs/qa-project-registry-31c60ba1/qa-result.md",
          "report_sha256": "863efbd27c3c3b01eb7efc84fe9a3405f10d5e24875711eab194563996b84597"
        },
        "integrator": {
          "status": "passed",
          "context": "/root/integrator",
          "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
          "summary": "Independently verified candidate ancestry/tree, all 51 business paths against frozen scope, clean identical detached checkout, board identity, reviewed/tested subject and unchanged unrelated user document. No full tests repeated."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "d310a9ea7d1e2dab0d8d9177bd300de8d119ab6f",
        "base": "f838a1a2787790edcb2c16f1146cda202147e59a",
        "parent": "31c60ba1a5313fe49c23c91ef8d1beadc31f28f3",
        "tree": "a6f837e4600b894d506e9275e9b8b99920c519de",
        "method": "Feature commits already integrated in local primary at candidate HEAD. An identical clean detached worktree hosts the sole-writer completion record; root will fast-forward its board-only completion commit into primary.",
        "worktree": "logs/registry-integration-d310a9ea",
        "clean_worktree_verified": true,
        "board_blob": "7377eed6002a2aa0826364f2b987635544f2d971",
        "board_checkout_sha256": "652434746b3549df2e976c01ac2b578b6a87a6d33d5e721df14ccbe623b4c18f",
        "board_checkout_note": "core.autocrlf causes a checkout byte-hash difference; primary/worktree normalized bytes and committed Git blob are identical.",
        "preserved_unrelated_file": "docs/project_delivery_and_internal_followup_design.md",
        "preserved_unrelated_sha256": "bc7be8ecc45712a9ab4d9467e2fedb4e35aca263de66802658dd08254ce39a5c",
        "primary_tracked_changes": false,
        "primary_untracked_file_preserved": true,
        "github_push": false
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_ADDITIVE_SAMPLE_QUANTITY_DEFAULTS",
    "tier": "standard",
    "subject": "cc1da9f56f05e8dfaafb7186319d92faa0c0f881",
    "summary": "Fee Evaluation automatically sums additive Matrix sample quantity expressions such as 3+3 for Units and keeps Sample preparation fully discounted by default.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested: 关闭",
    "closed_at": "2026-09-08T23:41:01.885170Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
