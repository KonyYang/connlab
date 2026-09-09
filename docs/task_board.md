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
    "updated_at": "2026-09-08T23:48:19.113804Z",
    "checkpoint": null,
    "report": null
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
