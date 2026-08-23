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
    "task_id": "TASK_MATRIX_EDITOR_LLCR_CR_DRAFT_DOWNLOAD",
    "summary": "Generate LLCR and CR preview workbooks from the current Matrix Editor draft, matching Test Record behavior and resolving explicit split sample allocations safely.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Add a one-click Matrix Editor draft generation path for LLCR and CR, preserve confirmed-Matrix generation for authoritative downstream use, and add regression coverage for current-draft precedence and explicit 5+5(d) LLCR allocation.",
    "scope_paths": [
      "frontend/src/features/matrix-editor",
      "frontend/src/api/client.ts",
      "backend/api",
      "backend/application",
      "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
      "tests/unit",
      "tests/integration"
    ],
    "risk_reasons": [],
    "activation_head": "cda1548f1e51b78a1e5a586de1bc17b7f6e8d019",
    "started_at": "2026-08-23T07:37:10.394579Z",
    "updated_at": "2026-08-23T08:09:27.523187Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_EDITOR_LLCR_CR_DRAFT_DOWNLOAD",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_EDITOR_LLCR_CR_DRAFT_DOWNLOAD",
      "subject": "9c9632bd1b471be96678ba4d82c53e31063b0739",
      "summary": "LLCR and CR now download separate preview workbooks from the current Matrix Editor draft; explicit 5+5(d) LLCR allocations resolve safely.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/main.py",
        "backend/api/routes_matrix_editor_llcr_cr_record_generation.py",
        "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
        "backend/application/matrix_editor_llcr_cr_record_generation_service.py",
        "backend/application/matrix_editor_llcr_cr_record_projection.py",
        "backend/application/matrix_record_sample_quantity.py",
        "backend/infrastructure/files/llcr_cr_specialized_record_artifact_store.py",
        "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/LlcrCrRecordWorkbookPanel.test.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordWorkbookPanel.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.test.tsx",
        "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts",
        "tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py",
        "tests/unit/test_matrix_editor_llcr_cr_record_projection.py"
      ],
      "validation": [
        {
          "name": "backend related pytest",
          "status": "passed",
          "result": "19 passed"
        },
        {
          "name": "frontend Matrix Editor Vitest",
          "status": "passed",
          "result": "47 passed"
        },
        {
          "name": "frontend production build",
          "status": "passed"
        },
        {
          "name": "browser verification",
          "status": "passed",
          "result": "Group 6 current draft 5; LLCR and CR one-click downloads succeeded; generated LLCR workbook sample count 5"
        }
      ],
      "roles": {
        "developer": {
          "status": "passed"
        },
        "reviewer": {
          "status": "passed",
          "standards_findings": 0,
          "spec_findings": 0
        },
        "qa": {
          "status": "passed"
        }
      },
      "integration": {
        "status": "passed",
        "head": "9c9632bd1b471be96678ba4d82c53e31063b0739",
        "clean": true
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_SOL_WORKFLOW_REVISE",
    "tier": "standard",
    "subject": "233149fcb5eb51f2e3fde4cb6afd40a774b4a71c",
    "summary": "Allow in-scope feedback to return a completed task from ready_for_close to running without closing or creating a new task.",
    "disposition": "completed",
    "decision_ref": "user:关闭",
    "closed_at": "2026-08-23T07:16:11.423390Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
