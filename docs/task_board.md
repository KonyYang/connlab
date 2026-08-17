# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/TASK_WORKFLOW.md`.
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
    "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST",
    "summary": "Complete the ordinary-browser Matrix Import source picker with direct target-directory Word/PDF candidates and stale-safe opaque selection while preserving desktop and read-only behavior.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Implement only missing behavior on current master: resolve Submitted Material before parsed intake attachments; list direct .doc/.docx/.pdf files without paths; preserve picker states, desktop native selection, read-only zero calls, and existing Matrix preview authority; bind opaque IDs to directory, filename, and current file content or instance; add proportional regressions and browser verification; no persistence, recursive scan, external mutation, or legacy workflow restoration.",
    "scope_paths": [],
    "risk_reasons": [],
    "activation_head": "f79a095c5db02ed8143d3cfd41099e54fece801a",
    "started_at": "2026-08-17T12:17:24.839564Z",
    "updated_at": "2026-08-17T12:53:32.445300Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST",
      "subject": "f6bbf843d25aa7d8b288cc467d2ef0219e686604",
      "summary": "Ordinary-browser Matrix Import now lists path-free direct Word and PDF files from the preferred resolved source folder with stale-safe opaque selection; desktop native and read-only behavior remain intact.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_project_test_plan_source_candidates.py",
        "backend/application/project_test_plan_source_candidate_service.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx",
        "frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx",
        "frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts",
        "tests/integration/test_project_test_plan_source_candidates_api.py",
        "tests/unit/test_matrix_source_candidate_service.py"
      ],
      "validation": [
        {
          "name": "backend_api_preview",
          "status": "passed",
          "summary": "26 passed, 1 environment-dependent symlink test skipped"
        },
        {
          "name": "frontend_focused",
          "status": "passed",
          "summary": "57 passed"
        },
        {
          "name": "frontend_build",
          "status": "passed",
          "summary": "TypeScript and Vite production build passed"
        },
        {
          "name": "python_compile",
          "status": "passed",
          "summary": "Changed backend modules compiled"
        },
        {
          "name": "browser_smoke",
          "status": "passed",
          "summary": "Real browser at 1280px and 514px passed interaction, overflow, path and console checks"
        },
        {
          "name": "diff_check",
          "status": "passed",
          "summary": "Git diff check and scope passed"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "TDD implementation, self-review and developer validation complete"
        },
        "reviewer": {
          "status": "passed",
          "summary": "Independent Standards and Spec review found zero findings"
        },
        "qa": {
          "status": "passed",
          "summary": "Independent automated QA matrix passed; browser evidence retained from developer smoke"
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Clean master integration commit created with exact in-scope product paths"
      }
    }
  },
  "last_closed": null,
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
