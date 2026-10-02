# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> Version 1 keeps one active task; an idle isolated Submit upgrades to version 2 with one main
> task and one independent micro task. GPT-6 Astra runs routine stages until each task's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "ready_for_close",
  "active": {
    "task_id": "TASK_DOC_IR_DWV_CONTEXT_SYNC_20261002",
    "summary": "Correct obsolete IR/DWV workbook implementation status in project context",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Update only docs/PROJECT_CONTEXT.md to reflect implemented IR/DWV template-based blank record generation and draft versus safe official publication; keep automated specification point extraction unimplemented. No code changes; preserve and restore the unrelated untracked photo automation design draft.",
    "scope_paths": [
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "1bb4d89c390a241cdb794a0bb3f6ac1d60aea290",
    "started_at": "2026-10-02T03:43:10.928184Z",
    "updated_at": "2026-10-02T03:45:13.614888Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_DOC_IR_DWV_CONTEXT_SYNC_20261002",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_DOC_IR_DWV_CONTEXT_SYNC_20261002",
      "subject": "b889ca0b1463e6d6120c6779bccbac24fdcde291",
      "summary": "Correct PROJECT_CONTEXT to mark IR/DWV blank-record workbook generation implemented, retain automated specification point extraction as unimplemented, and include IR/DWV in draft-versus-safe-official-publication guidance. Documentation only; unrelated untracked design draft preserved in a single-path recovery stash for restoration after board recording.",
      "scope_ok": true,
      "changed_paths": [
        "docs/PROJECT_CONTEXT.md"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "documentation cross-check against implemented entry and generator/publication boundaries",
          "result": "Read actual IR/DWV routes, generation service and openpyxl writer; UI action tests expose IR&DWV Form; writer clears measured cells; confirmed/draft publication wiring exists. Corrected only obsolete status and shared output guidance."
        },
        {
          "status": "passed",
          "name": "final exact diff and scope self-review",
          "result": "git diff --check exit0 after final edits; only PROJECT_CONTEXT content and sole-writer board changed; no product code or tests changed, so no redundant test/build run."
        },
        {
          "status": "passed",
          "name": "unrelated draft bounded preservation",
          "result": "Only docs/plans/REPORT_RESULT_PHOTO_AUTOMATION_DESIGN.md stashed at exact72845df92e9f370f259270695833e012320ee6bd; initial SHA2566d928420f27128e5e6395a703cf28e474e9ff62201084d505a569e92abf81647. Backup kept; restoration is immediate post-record housekeeping, not a claimed completed check yet."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "context": "Primary agent implemented documentation-only micro correction, self-reviewed exact diff, and cross-checked actual code. No independent role/test execution claimed."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "b889ca0b1463e6d6120c6779bccbac24fdcde291",
        "code_subject": "b889ca0b1463e6d6120c6779bccbac24fdcde291",
        "facts": "Micro direct-master documentation commit b889ca0b on clean primary, exact observed nonboard path docs/PROJECT_CONTEXT.md; no product or unrelated file changes."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_362_IR_DWV_RECORD_WORKBOOK_20261001",
    "tier": "high_risk",
    "subject": "01c49338f883ba0fe07b62a4e8e4bedb0775f6b2",
    "summary": "Implement IR/DWV Matrix record workbook end to end",
    "disposition": "completed",
    "decision_ref": "User explicit final close: 关闭任务, 2026-10-02 after successful IR/DWV sample-width acceptance.",
    "closed_at": "2026-10-02T02:13:51.795487Z"
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
