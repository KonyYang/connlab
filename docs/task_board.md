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
    "updated_at": "2026-09-22T16:00:23.041415Z",
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
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_EQUIPMENT_CALIBRATION_MANUFACTURER_HEADER_MATCH",
      "subject": "da7a2302df2d505ea3069d943dbe226eaea4709c",
      "summary": "The legacy All Equip. layout now accepts a third-column header that contains Manufacturer, while retaining exact matching for every other required column.",
      "scope_ok": true,
      "changed_paths": [
        "backend/application/external_resource_service.py",
        "backend/infrastructure/office/excel_tabular_layout.py",
        "tests/unit/test_legacy_equipment_excel_layout.py"
      ],
      "validation": [
        {
          "status": "passed",
          "details": "TDD red case failed with the prior exact Manufacturer header match; the final focused suite passed 15 tests."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "details": "Implemented and self-reviewed the exact diff; standards and specification passes found no actionable issue."
        }
      },
      "integration": {
        "status": "passed",
        "mode": "direct_primary",
        "details": "Committed as da7a2302df2d505ea3069d943dbe226eaea4709c on the active task branch."
      }
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
