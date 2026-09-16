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
    "task_id": "TASK_TEST_RECORD_SINGLE_BUTTON_HEADER",
    "summary": "Keep one Matrix Editor Test Record button, add one state-driven confirmation flow for draft preview versus official save, and make downloaded draft headers use the same reliable metadata mapping as official Test Records.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Inspect and update the existing Matrix Editor Test Record frontend/backend seams. Confirm against fresh backend authority, folder, and target-file state; preserve safe official conflict handling; make draft generation download-only and side-effect-free; share official header mapping and Word header writing across preview and official generation; add regression coverage for UI state paths, cancellation, header variants, side effects, and existing publication behavior. Do not expose authority history or add buttons.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/MatrixWorkspaceActionGroups.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/pages/ProjectMatrixEditorPage.tsx",
      "frontend/src/api/client.ts",
      "frontend/src/features/project-workbench/TestRecordDraftGenerationButton.tsx",
      "backend/api/routes_matrix_editor_test_record_generation.py",
      "backend/application/matrix_editor_test_record_publication_service.py",
      "backend/application/matrix_editor_test_record_document_generation_service.py",
      "backend/application/matrix_editor_test_record_authority.py",
      "backend/infrastructure/office/test_record_document_gateway.py",
      "backend/infrastructure/files/test_record_publication_gateway.py",
      "tests/unit/test_matrix_editor_test_record_publication_service.py",
      "tests/unit/test_matrix_editor_test_record_authority.py",
      "tests/unit/test_test_record_document_gateway.py",
      "tests/integration/test_matrix_editor_test_record_generation_api.py",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
      "frontend/src/features/project-workbench/TestRecordDraftGenerationButton.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "6f0853c39adf5465a908e38304eba144e7bb0d44",
    "started_at": "2026-09-16T00:03:02.436360Z",
    "updated_at": "2026-09-16T00:03:02.436360Z",
    "checkpoint": null,
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_GROUP_IDENTITY_C",
    "tier": "high_risk",
    "subject": "8453c954afef0098a538fb43f58ea56a9c17b1db",
    "summary": "Implement a previewable, fingerprinted, backup-backed, reversible Matrix data-integrity repair and compatible schema migration without changing confirmed authority content or revision counts.",
    "disposition": "cancelled",
    "decision_ref": "User rejected scope expansion, requested rollback to pre-task code state, and explicitly cancelled the Matrix database integrity hardening/migration task.",
    "closed_at": "2026-09-16T00:00:14.030734Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
