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
    "updated_at": "2026-09-22T23:30:58.902908Z",
    "checkpoint": {
      "task_id": "TASK_EQUIPMENT_CALIBRATION_MANUFACTURER_HEADER_MATCH",
      "status": "running",
      "stage": "runtime-verified",
      "schema": "connlab.sol-task-checkpoint",
      "summary": "Excel COM cannot open the configured legacy XLS because of Content.MSO, so the legacy tabular reader now falls back to the bundled xlrd parser. The configured workbook revalidated as valid through current source and returned DG-Q-0033 with its ISO calibration date; the persisted Settings resource is valid.",
      "version": 1,
      "requires_user": false
    },
    "report": null
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
