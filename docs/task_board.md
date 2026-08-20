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
    "task_id": "TASK_MATRIX_IMPORT_SETUP_RETURN_DRAFT_RESTORE",
    "summary": "Preserve the newly imported Matrix draft when returning from a feature-card Setup workflow.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Fix Matrix Editor navigation-state restoration so Import Matrix results remain active after entering Setup and returning, without changing Matrix authority or unrelated workflows.",
    "scope_paths": [],
    "risk_reasons": [],
    "activation_head": "c9e5343188f04d7b17a9b2927b388d6db7c225ed",
    "started_at": "2026-08-20T22:38:08.460457Z",
    "updated_at": "2026-08-20T23:08:27.134088Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SETUP_RETURN_DRAFT_RESTORE",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_MATRIX_IMPORT_SETUP_RETURN_DRAFT_RESTORE",
      "subject": "15353785d68099f81e662291859ecd18892a48f5",
      "summary": "Restore the latest imported Matrix draft and its source lineage after returning from Setup, while ignoring historical source drafts after confirmation.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/matrix_editor_session_dtos.py",
        "backend/api/routes_matrix_editor_session.py",
        "backend/application/matrix_editor_session_contracts.py",
        "backend/application/matrix_editor_session_draft_state.py",
        "backend/application/matrix_editor_session_service.py",
        "frontend/src/api/client.ts",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "tests/integration/test_matrix_editor_session_api.py",
        "tests/unit/test_matrix_editor_session_service.py"
      ],
      "validation": [
        {
          "status": "passed",
          "summary": "Backend unit and API integration tests: 31 passed."
        },
        {
          "status": "passed",
          "summary": "Frontend MatrixEditorWorkspace tests: 52 passed."
        },
        {
          "status": "passed",
          "summary": "Frontend production build and Python compilation passed."
        },
        {
          "status": "passed",
          "summary": "Real browser Setup return retained the specified GS-12-2029 Matrix with 17 rows."
        },
        {
          "status": "passed",
          "summary": "git diff --check passed."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "summary": "Implemented, self-reviewed, and validated the final code."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Focused Standards and Spec review: 0 findings."
        },
        "qa": {
          "status": "passed",
          "summary": "Independent complete QA matrix passed."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Exact task commit is clean on master and changed paths match task scope."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_DOCS_ROOT_INFORMATION_ARCHITECTURE_CLEANUP",
    "tier": "standard",
    "subject": "9cc494a21d7e1061e77e7619377d45007e6bb6c0",
    "summary": "Consolidate historical documentation indexes, relocate and refresh the Intake/Precheck contract, and retire obsolete archive tooling without changing product behavior.",
    "disposition": "completed",
    "decision_ref": "User explicitly said 关闭 on 2026-08-21.",
    "closed_at": "2026-08-20T22:37:07.262264Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
