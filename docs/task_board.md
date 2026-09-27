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
    "task_id": "TASK_MATRIX_SCHEDULE_COMPACT_HEADER",
    "summary": "Reduce Project Schedule card height by putting its title and four editable controls on one desktop row, and enlarge the title to match Test points.",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Keep the four existing schedule controls, labels, validation, and edit behavior unchanged. Place Project Schedule at the left and all four current fields in the same row on workstation widths; enlarge its heading to match the Test points heading. At narrower widths, allow a readable responsive wrap/stack rather than horizontal clipping. CSS and focused presentation test only.",
    "scope_paths": [
      "frontend/src/workbench.css",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx"
    ],
    "risk_reasons": [],
    "activation_head": "ce5e9d205df4a71c1dbf85002b478c08a9561f4e",
    "started_at": "2026-09-27T01:06:47.852875Z",
    "updated_at": "2026-09-27T01:54:31.521113Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_SCHEDULE_COMPACT_HEADER",
      "stage": "revision",
      "status": "running",
      "summary": "User feedback 2026-09-27: rename Project Schedule to Schedule.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_SCHEDULE_UNIFIED_CONFIRM",
    "tier": "high_risk",
    "subject": "24d2f1ad5a2a02a28fe2b1d64c797bced1ad3567",
    "summary": "Unify Project Schedule editing and authority confirmation with Confirm Matrix while retaining existing schedule revisions and safe folder/output gating.",
    "disposition": "completed",
    "decision_ref": "User 2026-09-27: 关闭",
    "closed_at": "2026-09-27T00:53:13.268897Z"
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
