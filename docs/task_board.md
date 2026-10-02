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
    "task_id": "TASK_REPORT_AUTOMATION_DOC_BASELINE_20261002",
    "summary": "Reconcile three report automation documents with current ConnLab implementation",
    "tier": "micro",
    "route": "sol_direct",
    "scope": "Only correct three report design/evidence Markdown documents against current code; preserve historical evidence, distinguish proposals from implemented behavior, no business code or external document writes.",
    "scope_paths": [
      "docs/plans/REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md",
      "docs/plans/REPORT_AUTOMATION_VBA_REFERENCE_MAP.md",
      "docs/plans/REPORT_RESULT_PHOTO_AUTOMATION_DESIGN.md"
    ],
    "risk_reasons": [],
    "activation_head": "93442a6c72f60b3b11f8366b0faf089efb73aa79",
    "started_at": "2026-10-02T08:02:43.987501Z",
    "updated_at": "2026-10-02T08:32:24.764041Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_REPORT_AUTOMATION_DOC_BASELINE_20261002",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_REPORT_AUTOMATION_DOC_BASELINE_20261002",
      "subject": "2106e342e65b7c1d625aecfca6f8833247a0c355",
      "summary": "Reconciled three report automation Markdown documents against current ConnLab source. Preserved historical evidence and newer v5 proposal; corrected delivered IR/DWV, LLCR, customer-report, authority, recoverable publication and measurement-source facts. No business code or external artifacts changed; Office historical probes were not rerun.",
      "scope_ok": true,
      "changed_paths": [
        "docs/plans/REPORT_AUTOMATION_REAL_SAMPLE_EVIDENCE.md",
        "docs/plans/REPORT_AUTOMATION_VBA_REFERENCE_MAP.md",
        "docs/plans/REPORT_RESULT_PHOTO_AUTOMATION_DESIGN.md"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Documentation integrity",
          "result": "Final three documents passed UTF-8 replacement-character, balanced Markdown fence, 25 unique repository reference and 2 relative-link checks."
        },
        {
          "status": "passed",
          "name": "Exact diff and scope review",
          "result": "Primary micro self-review verified current code facts, preserved user v5 design updates, distinguished implemented behavior from future proposals, corrected actual RecoverableContactRecordPublisher path, no code/template/external file edits."
        },
        {
          "status": "passed",
          "name": "Git diff check",
          "result": "Final staged diff passed git diff --cached --check before commit; working tree clean after content commit."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "context": "Primary micro implementation, documentation/source reconciliation and self-review; no claim of independent-agent review."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "2106e342e65b7c1d625aecfca6f8833247a0c355",
        "facts": "Direct master commit includes only three authorized Markdown documents and writer-generated task registration; no unrelated code edits."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_IR_DWV_DOWNLOAD_NAME_AUTHORITY_20261002",
    "tier": "standard",
    "subject": "4457ae6e2af6d44427fbe1d812b0332330f91a52",
    "summary": "Align IR/DWV download names with confirmed LTR and Matrix authority",
    "disposition": "completed",
    "decision_ref": "User final Close 2026-10-02 and approved temporary preservation of three unrelated documents; Matrix confirmation recovery delivered with browser-smoke limitation reported.",
    "closed_at": "2026-10-02T07:57:59.504767Z"
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
