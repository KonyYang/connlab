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
    "task_id": "TASK_TEST_RECORD_DIRECT_PUBLISH",
    "summary": "Publish the current Matrix Editor Test Record directly into an existing official project folder with authoritative headers and explicit archive, recycle-bin, or cancel conflict handling.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Test Record generation and publication only: preserve download behavior without an official workspace, publish to Test results when one exists, source headers from confirmed Basic Information, and safely resolve same-name files.",
    "scope_paths": [
      "backend/application/matrix_editor_test_record_document_generation_service.py",
      "backend/application/matrix_editor_test_record_publication_service.py",
      "backend/api/routes_matrix_editor_test_record_generation.py",
      "backend/api/dependencies.py",
      "backend/infrastructure/files/test_record_publication_gateway.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/workbench.css",
      "tests/unit/test_matrix_editor_test_record_publication_service.py",
      "tests/integration/test_matrix_editor_test_record_generation_api.py"
    ],
    "risk_reasons": [
      "Writes a generated Word document into the authoritative official project folder.",
      "May archive or move an existing user document to the Windows recycle bin after explicit confirmation."
    ],
    "activation_head": "a91e21a881f600eb73bb170c3768ff505c9ab9be",
    "started_at": "2026-08-27T23:05:04.742557Z",
    "updated_at": "2026-08-27T23:05:04.742557Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "REPORT-001",
    "tier": "standard",
    "subject": "2ac55ff76aec1db371fc3987ab5c9a543935bc6b",
    "summary": "Generate a downloadable non-overwriting E-3707_H initialization report draft from confirmed project authority in Project Workbench.",
    "disposition": "completed",
    "decision_ref": "用户明确回复：关闭",
    "closed_at": "2026-08-27T22:35:55.480470Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
