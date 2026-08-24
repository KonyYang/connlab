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
    "task_id": "TASK_PROJECT_PACKAGE_DRAFT_PREVIEW",
    "summary": "Allow Project Package preview to remain usable from a Matrix draft; only formal actions require confirmed Matrix authority.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Project Package preview must render a non-authoritative Matrix draft state without requiring Matrix confirmation; confirmed authority remains required for formal actions.",
    "scope_paths": [
      "backend/application/project_package_preview_service.py",
      "backend/application/confirmed_fee_version_service.py",
      "backend/api/routes_project_package_preview.py",
      "tests/unit/test_project_package_preview_service.py",
      "tests/integration/test_project_package_preview_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "62887b9ef6d6f2aca242314c04566b7e06f6c9c4",
    "started_at": "2026-08-23T23:54:46.584360Z",
    "updated_at": "2026-08-24T00:05:43.852909Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_PACKAGE_DRAFT_PREVIEW",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_PROJECT_PACKAGE_DRAFT_PREVIEW",
      "subject": "7a7a2f6654e782747dd5c5438c4bcd100d34eff1",
      "summary": "Project Package preview now treats the latest active Matrix draft as a usable non-authoritative preview source and preserves confirmation requirements for formal package outputs.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/routes_project_package_preview.py",
        "backend/application/project_package_preview_service.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/project-workbench/ProjectPackagePreviewPanel.test.tsx",
        "frontend/src/features/project-workbench/ProjectPackagePreviewPanel.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx",
        "frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx",
        "tests/integration/test_project_package_preview_api.py",
        "tests/unit/test_project_package_preview_service.py"
      ],
      "validation": [
        {
          "name": "project package preview backend",
          "status": "passed",
          "detail": "20 passed: active Matrix draft, no Matrix source, superseded drafts, and API response contract"
        },
        {
          "name": "project workbench frontend",
          "status": "passed",
          "detail": "55 passed across ProjectPackagePreviewPanel, ProjectWorkbenchLayout, and useProjectWorkbenchModel"
        },
        {
          "name": "frontend production build",
          "status": "passed",
          "detail": "tsc -b && vite build completed"
        },
        {
          "name": "diff check",
          "status": "passed",
          "detail": "git diff --check passed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Used red-green tests for a usable active Matrix draft and for ignoring superseded drafts."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Standards review and specification review found no unresolved findings; formal output authority remains confirmed-only."
        },
        "qa": {
          "status": "passed",
          "summary": "Completed selected backend, frontend, and production-build verification on the final implementation."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Integrated in commit 7a7a2f6654e782747dd5c5438c4bcd100d34eff1 with a clean working tree."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_BROWSER_RELEASE_LLCR_GATE_AND_RUNTIME_SMOKE",
    "tier": "standard",
    "subject": "1966e98bc782d824abb83197ad72cb61bbb65868",
    "summary": "Make the browser release gate current LLCR/CR workbook behavior and make the browser smoke check start and verify the packaged local server.",
    "disposition": "completed",
    "decision_ref": "user-message-2026-08-24-close",
    "closed_at": "2026-08-23T23:46:37.671259Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
