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
    "task_id": "TASK_EQUIPMENT_CALIBRATION_MANUFACTURER_HEADER_MATCH",
    "summary": "Accept the legacy equipment workbook Manufacturer header when the configured third header cell contains Manufacturer plus a vendor annotation, while retaining the fixed All Equip. layout and other required headers.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Only the requested legacy equipment-calibration header matching behavior.",
    "scope_paths": [
      "backend/application/external_resource_service.py",
      "tests/unit/test_external_resource_service.py"
    ],
    "risk_reasons": [],
    "activation_head": "c9fefcc3e06560a604f246e2061bea4ff77bd119",
    "started_at": "2026-09-22T15:51:57.399200Z",
    "updated_at": "2026-09-23T16:18:51.252916Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_EQUIPMENT_CALIBRATION_MANUFACTURER_HEADER_MATCH",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "version": 1,
      "scope_ok": true,
      "task_id": "TASK_EQUIPMENT_CALIBRATION_MANUFACTURER_HEADER_MATCH",
      "roles": {
        "developer": {
          "detail": "Implemented and self-reviewed exact diff; targeted checks passed",
          "status": "passed"
        }
      },
      "validation": [
        {
          "status": "passed",
          "detail": "50 passed on final HEAD, 2026-09-24",
          "name": "affected unit tests"
        },
        {
          "status": "passed",
          "detail": "148 focused release tests, frontend build, packaged executable build, health and homepage smoke passed on unchanged source bytes",
          "name": "browser release build and smoke"
        },
        {
          "status": "passed",
          "detail": "Configured legacy XLS resource became valid without modifying workbook content",
          "name": "live equipment resource revalidation"
        }
      ],
      "summary": "Accepted annotated Manufacturer header in the fixed legacy All Equip. layout; verified XLS fallback and current release revalidation; completed user-authorized managed development runtime and browser-release startup repairs.",
      "subject": "ef79e24d56c87ed6ebcf72ec59375a245ab4ac32",
      "schema": "connlab.sol-task-report",
      "integration": {
        "detail": "Clean master HEAD with exact task diff and separately committed release repair",
        "status": "passed"
      },
      "changed_paths": [
        "backend/application/external_resource_service.py",
        "backend/desktop/managed_development_launcher.py",
        "backend/desktop/packaged_server.py",
        "backend/infrastructure/office/excel_com_readonly_tabular_gateway.py",
        "backend/infrastructure/office/excel_tabular_layout.py",
        "docs/packaging_notes.md",
        "packaging/README_FOR_BROWSER_OPERATOR.md",
        "packaging/RELEASE_NOTES_BROWSER.md",
        "packaging/Start_ConnLab.bat",
        "scripts/run_mvp_dev.ps1",
        "tests/unit/test_desktop_packaged_server.py",
        "tests/unit/test_desktop_release_scripts.py",
        "tests/unit/test_excel_com_readonly_tabular_gateway.py",
        "tests/unit/test_legacy_equipment_excel_layout.py",
        "tests/unit/test_managed_development_launcher.py"
      ]
    }
  },
  "last_closed": {
    "task_id": "TASK_PROJECT_FOLDER_AVAILABILITY_GUIDANCE",
    "tier": "high_risk",
    "subject": "64a26bf331d5c6eb9a32016c456a2bab66ec6076",
    "summary": "Make Project Folder actions reflect real folder and template availability, disable false Open/Create affordances, and guide missing-template recovery through Settings.",
    "disposition": "completed",
    "decision_ref": "user-close-2026-09-22-runtime-recovery",
    "closed_at": "2026-09-22T15:32:57.117418Z"
  },
  "retained_history": [
    {
      "task_id": "TASK_361A_FEE_SUMMARY_ACCEPTANCE_CONTRACT",
      "tier": "standard",
      "closed_at": "2026-09-18T03:01:50.000000Z"
    },
    {
      "task_id": "TASK_PROJECT_FOLDER_FINALIZATION_ACCESS_COMPLETE",
      "tier": "high_risk",
      "closed_at": "2026-09-17T11:59:24.022479Z"
    }
  ]
}
```
<!-- CONNLAB_EXECUTION_CONTROL_END -->

Historical boards, role evidence, and retired lane metadata are audit material only. They do not
authorize work, create WIP, or override this control block.

## Pending engineering-debt tasks ( backlog / not active )

These items are not in-flight; they are recorded here for prioritization. They do not
change the `active` field above.

### TASK_361B_TEST_RUNNER_INTERPRETER_ALIGNMENT

**Tier:** micro
**Revised from:** the stale broad test-environment proposal discovered during TASK_361A
**Goal:** Keep the supported test entry point on the same Python runtime as ConnLab development.

The original diagnosis was rechecked before implementation:

- `C:/PythonEnvs/connlab/.venv` is Python 3.11.9 and imports Tkinter 8.6 successfully; no
  dependency installation is needed.
- Office-dependent integration tests already use the `office_integration` marker. The normal gate
  excludes them and `-Suite Office` remains the explicit installed-Office check.
- WorkBuddy or Codex temporary-directory and safe-delete restrictions are host permissions, not
  ConnLab product behavior. They must be handled by the runner environment or an explicitly
  permitted pytest temp location, not by weakening repository cleanup or test semantics.

The remaining defect was limited to `scripts/run_tests.ps1`: it invoked the ambient `py` launcher,
which selected Python 3.13.3 instead of the Python 3.11.9 environment used by ConnLab. The revised
runner defaults to `C:/PythonEnvs/connlab/.venv/Scripts/python.exe`, supports an explicit
`-PythonExe` override, fails clearly when that interpreter is missing, and preserves the existing
normal/Office split.

**Validation:** the focused runner contract passes, and the complete non-Office Python gate passes
with 2954 tests, 7 skips, and 19 Office tests deselected on Python 3.11.9. No product code,
dependencies, Office implementation, or host safety policy changed.
