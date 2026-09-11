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
    "task_id": "TASK_RELEASE_FEE_PUBLICATION_AND_WORKSPACE_RECOVERY",
    "summary": "Repair Fee Form publication staging, pricing autosave races, and recoverable project folder failures reported on another workstation.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Reproduce the reported errors; fix operation staging and draft save serialization; allow safe recovery of unchanged/unpublished workspace operations without bypassing conflict checks; verify and produce a corrected portable browser release.",
    "scope_paths": [
      "backend/application/fee_form_publication_service.py",
      "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
      "backend/infrastructure/files/recoverable_workspace_publisher.py",
      "backend/application/project_folder_generation_service.py",
      "backend/api/project_folder_generation_composition.py",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
      "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx",
      "tests/unit/test_fee_form_publication_service.py",
      "tests/unit/test_generation_workspace_recovery.py",
      "tests/unit/test_project_folder_generation_service.py",
      "tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py",
      "tests/integration/test_project_folder_generation_recovery.py",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "docs/project_folder_generation_recovery.md",
      "docs/packaging_notes.md"
    ],
    "risk_reasons": [
      "Changes recovery for publishing into existing operator project folders; preserve explicit conflict authority and file ownership."
    ],
    "activation_head": "67aa363e9f4cd53495dc214fda5e4e455c40e476",
    "started_at": "2026-09-11T04:39:52.435610Z",
    "updated_at": "2026-09-11T05:11:27.041759Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_RELEASE_FEE_PUBLICATION_AND_WORKSPACE_RECOVERY",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_RELEASE_FEE_PUBLICATION_AND_WORKSPACE_RECOVERY",
      "subject": "0fcc9780c2b1938d8a97d05663a69339e9f7b032",
      "summary": "Fixed Fee Form staging and typed errors, serialized Fee Evaluation autosave/CAS, and safely released provably unpublished workspace recovery checkpoints. Built and isolated-smoke-tested ConnLab_Web_202609111305_v0.1.0.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_confirmed_matrix_fee_evaluation_export.py",
        "backend/application/fee_form_publication_service.py",
        "backend/infrastructure/files/recoverable_workspace_publisher.py",
        "docs/packaging_notes.md",
        "docs/project_folder_generation_recovery.md",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.pricingDraftHydration.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.test.tsx",
        "frontend/src/features/fee-evaluation/FeeEvaluationReviewExportPage.tsx",
        "tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py",
        "tests/integration/test_generation_workspace_process_recovery.py",
        "tests/unit/test_fee_form_publication_service.py",
        "tests/unit/test_generation_workspace_recovery.py"
      ],
      "validation": [
        {
          "command": "py -m pytest tests/unit/test_fee_form_publication_service.py tests/unit/test_confirmed_matrix_fee_evaluation_export_timeout_service.py tests/unit/test_generation_workspace_recovery.py tests/unit/test_project_folder_generation_service.py tests/unit/test_generation_recovery.py tests/integration/test_confirmed_matrix_fee_evaluation_export_api.py tests/integration/test_fee_evaluation_export_child_transaction.py tests/integration/test_generation_workspace_process_recovery.py tests/integration/test_project_folder_generation_recovery.py tests/integration/test_project_folder_generation_write_guard.py tests/integration/test_project_registry_generation_lock.py",
          "status": "passed",
          "summary": "Independent QA: 98 passed, 62.45s. Initial restricted attempt failed pytest temp setup; rerun with required permission passed."
        },
        {
          "command": "npm test -- --run src/features/fee-evaluation",
          "status": "passed",
          "summary": "Independent QA: 8 files, 86 passed, 9.75s."
        },
        {
          "command": "scripts/build_windows_browser_release.ps1 -ReleaseDate 202609111305",
          "status": "passed",
          "summary": "74 release tests passed 7.33s; frontend tsc/Vite 5.7s; PyInstaller 33.1s; manifest pins reviewed commit."
        },
        {
          "command": "tmp/smoke_fee_recovery_release.ps1 -ReleaseFolder dist_release/ConnLab_Web_202609111305_v0.1.0",
          "status": "passed",
          "summary": "2.71s: frozen health, frontend shell/current fee asset, diagnostic download, isolated empty database and EXE manifest SHA256; owned test server stopped."
        },
        {
          "command": "git diff --check",
          "status": "passed",
          "summary": "Independent review and QA passed."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "summary": "Independent recovery_planner established pre-publication cleanup safety gates and recovery acceptance."
        },
        "developer": {
          "status": "passed",
          "summary": "Independent recovery_developer implemented and RED/GREEN-tested recovery. Root implemented fee staging/API/autosave with RED/GREEN regression evidence."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Independent release_reviewer: Standards 0, Spec 0 unresolved. Explicit-save input-lock finding fixed and tested."
        },
        "qa": {
          "status": "passed",
          "summary": "Independent release_qa verified final affected 98 Python and 86 frontend tests. Root performed fresh release build and isolated smoke."
        },
        "integrator": {
          "status": "passed",
          "summary": "Independent release_integrator verifies immutable subject, scope, clean tree, release manifest and validation evidence before this report is submitted."
        }
      },
      "integration": {
        "status": "passed",
        "summary": "Reviewed fix commit and fresh browser package; no operator database/config/project files modified. Target-workstation Office execution remains a manual verification boundary."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_REGISTRY_ACTION_ICON_BUTTONS",
    "tier": "micro",
    "subject": "4e81a97759ea6f5d83ed55bee9a512a24c1dce99",
    "summary": "Project registry actions are compact icon buttons placed directly beside Open Workbench.",
    "disposition": "completed",
    "decision_ref": "User explicitly requested 关闭.",
    "closed_at": "2026-09-11T04:34:26.592539Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
