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
    "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS",
    "summary": "Fix project folder finalization access failure and actionable recovery diagnostics",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Diagnose diagnostic d01ccfa9c2f54ba5b0e82b8600b2d4a3 and safely fix existing operation-owned overwrite cleanup without weakening identity or content protections. No real database migration or unconfirmed external deletion.",
    "scope_paths": [
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "backend/application/project_folder_generation_service.py",
      "backend/shared/operation_diagnostics.py",
      "tests/unit/test_generation_workspace_recovery.py",
      "tests/unit/test_project_folder_generation_service.py",
      "tests/unit/test_operation_diagnostics.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "docs/project_folder_generation_recovery.md"
    ],
    "risk_reasons": [
      "Cleanup of a previously approved overwrite recovery copy is destructive; retain exact identity and content checks."
    ],
    "activation_head": "b78b686328fa4761d5800033d6fe61dc4aac55f1",
    "started_at": "2026-09-17T00:15:34.338492Z",
    "updated_at": "2026-09-17T00:35:43.208738Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS",
      "stage": "review_scope_confirmation",
      "status": "blocked",
      "summary": "Root cause proven: readonly old directories fail final cleanup after all8steps. Developer RED/GREEN22passed; P1 external hardlink attr mutation fixed. Independent review P2: production Runner.finalize omits verify_context callback. Await user approval to include backend/api/project_folder_generation_composition.py (additional high-risk path); do not modify it before approval. Pending independent re-review, final QA and integration. No real data writes/resume. Board rollover closed prior Fee task.",
      "requires_user": true
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_CONFIRM_SPEND_TIME_ROUNDTRIP",
    "tier": "standard",
    "subject": "b644c6c6b90868c4a499cbc590021a9485b78836",
    "summary": "Fix Fee confirmation after editing Visual Inspection man-hours",
    "disposition": "completed",
    "decision_ref": "User explicitly closed Fee task and requested folder failure diagnosis and fix",
    "closed_at": "2026-09-17T00:15:34.338492Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
