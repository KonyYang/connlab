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
    "task_id": "TASK_MATRIX_REIMPORT_ROW_IDENTITY",
    "summary": "Prevent duplicate Matrix row identities when re-importing the same source and rebuild the portable browser release.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fix Matrix re-import reconciliation so each existing draft row can be consumed at most once, reject duplicate row lineage before persistence, add regression coverage, and build/smoke a new ConnLab_Web release.",
    "scope_paths": [
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.test.ts",
      "backend/application/project_matrix_duration_authority_payload.py",
      "tests/unit/test_project_matrix_draft_persistence_service.py",
      "scripts/build_windows_browser_release.ps1",
      "scripts/smoke_windows_browser_release.ps1"
    ],
    "risk_reasons": [],
    "activation_head": "479bc533b0a920b642bdceb0374a77f5beded5c7",
    "started_at": "2026-08-24T23:40:27.998640Z",
    "updated_at": "2026-08-24T23:53:01.562699Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_REIMPORT_ROW_IDENTITY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_REIMPORT_ROW_IDENTITY",
      "subject": "ff7e08161646d855cfdf381c9c1920a4faf6a730",
      "summary": "Matrix re-import now consumes each existing row identity at most once, invalid duplicate row identities are rejected before SQLite persistence, and ConnLab_Web_202608250749_v0.1.0 was built and smoke-tested.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/project_matrix_duration_authority_payload.py",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.test.ts",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "tests/integration/test_matrix_editor_session_api.py",
        "tests/unit/test_project_matrix_draft_persistence_service.py"
      ],
      "validation": [
        {
          "name": "Developer affected checks",
          "status": "passed",
          "detail": "26 backend and 22 frontend tests passed on the reviewed state."
        },
        {
          "name": "Complete Matrix QA",
          "status": "passed",
          "detail": "63 backend and 95 Matrix Editor frontend tests passed."
        },
        {
          "name": "Browser release build",
          "status": "passed",
          "detail": "39 release tests, production frontend build, and PyInstaller completed."
        },
        {
          "name": "Packaged browser smoke",
          "status": "passed",
          "detail": "New release health endpoint and homepage passed on isolated port 8766."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "detail": "TDD red/green reproduction and affected checks passed."
        },
        "reviewer": {
          "status": "passed",
          "detail": "Standards and requirement review found no remaining issues."
        },
        "qa": {
          "status": "passed",
          "detail": "Complete affected matrix and release validation passed."
        }
      },
      "integration": {
        "status": "passed",
        "detail": "Commit ff7e0816 is clean on master and the new portable browser release is available."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_MANUAL_SAMPLE_QTY_HYDRATION",
    "tier": "micro",
    "subject": "768c599ca1ed461edeb006a88ac4b095385ce782",
    "summary": "Restore saved manual sample quantities when the current Matrix requires quantity confirmation, so Update Fee is not blocked after a valid reload.",
    "disposition": "completed",
    "decision_ref": "user-message-2026-08-25-close-and-start-matrix-reimport-fix",
    "closed_at": "2026-08-24T23:40:27.998640Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
