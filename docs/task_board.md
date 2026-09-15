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
    "task_id": "TASK_PROJECT_FOLDER_PREFLIGHT_PRIMARY_BLOCKER",
    "summary": "Show the real Project Folder configuration blocker instead of cascading required-form identity errors.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Project Folder generation preview, its regression tests, and any minimal Workbench presentation adjustment required to surface the actionable primary blocker.",
    "scope_paths": [
      "backend/api/project_folder_generation_composition.py",
      "tests/integration/test_project_folder_generation_api.py",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "65be54eeb54fcee990f5ac8bde074085fceb4f61",
    "started_at": "2026-09-15T14:04:36.355636Z",
    "updated_at": "2026-09-15T14:34:39.371998Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_PROJECT_FOLDER_PREFLIGHT_PRIMARY_BLOCKER",
      "stage": "external_identity_conflict",
      "status": "running",
      "summary": "The stale missing D:\\Test Project workspace record now replans under D:\\ConnLabProjects. The target DL-2026-09-001 directory contains a manifest and business content owned by project 4c2191f3419c4f29b14d734938091442, while the current project is 638bb45740f64a0085b2fa203c9d014c. User direction is required before any external folder migration or project identity correction.",
      "requires_user": true
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_FEE_FORM_XLSX_NATIVE_GENERATION",
    "tier": "standard",
    "subject": "7f7d989936778735140a404f11f66f1276ac17a3",
    "summary": "Migrate Fee Form generation to native XLSX without Excel COM",
    "disposition": "completed",
    "decision_ref": "User explicitly requested closure after accepting the completed Fee Form XLSX migration and missing-folder fallback fix.",
    "closed_at": "2026-09-15T13:54:35.472651Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
