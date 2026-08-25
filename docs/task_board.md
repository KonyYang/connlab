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
    "task_id": "TASK_SUPPORT_DIAGNOSTIC_BUNDLE",
    "summary": "Add persistent packaged-runtime diagnostics and a safe operator-exportable support bundle.",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Configure rotating packaged backend logs, capture sanitized frontend unhandled errors through a typed API, expose a Settings support panel that downloads a diagnostic ZIP, include release/build metadata, exclude databases, business files, and raw configuration, and verify packaged behavior.",
    "scope_paths": [
      "backend/shared/logging.py",
      "backend/desktop/packaged_server.py",
      "backend/desktop/runtime_paths.py",
      "backend/api/main.py",
      "backend/api/routes_diagnostics.py",
      "backend/application/support_diagnostic_bundle_service.py",
      "frontend/src/api/client.ts",
      "frontend/src/App.tsx",
      "frontend/src/pages/SettingsPage.tsx",
      "frontend/src/pages/SettingsPage.test.tsx",
      "frontend/src/features/settings/SupportDiagnosticsPanel.tsx",
      "frontend/src/features/settings/SupportDiagnosticsPanel.test.tsx",
      "packaging/connlab_browser_server.spec",
      "scripts/build_windows_browser_release.ps1",
      "tests/unit/test_logging.py",
      "tests/unit/test_support_diagnostic_bundle_service.py",
      "tests/integration/test_support_diagnostics_api.py"
    ],
    "risk_reasons": [],
    "activation_head": "3353208d24f1fc32b5095064d60b563c685da700",
    "started_at": "2026-08-25T00:08:22.338183Z",
    "updated_at": "2026-08-25T00:28:17.937523Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_SUPPORT_DIAGNOSTIC_BUNDLE",
      "stage": "review-and-qa",
      "status": "running",
      "summary": "Focused review completed with privacy and startup-fallback hardening; 23 backend tests, 5 frontend tests, production build, and isolated-port browser download verification pass.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_REIMPORT_ROW_IDENTITY",
    "tier": "standard",
    "subject": "ff7e08161646d855cfdf381c9c1920a4faf6a730",
    "summary": "Prevent duplicate Matrix row identities when re-importing the same source and rebuild the portable browser release.",
    "disposition": "completed",
    "decision_ref": "user-message-2026-08-25-close",
    "closed_at": "2026-08-24T23:54:33.132890Z"
  },
  "retained_history": []
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.
