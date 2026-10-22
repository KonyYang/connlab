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
    "task_id": "TASK_LLCR_RESULT_SEMANTICS_20261023",
    "summary": "Correct LLCR absolute resistance versus delta semantics without changing real reports",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Distinguish initial/final resistance and delta values through existing import and report seams; preserve source meanings and local-update fidelity. Use isolated copies only, no authoritative file writes or database migration.",
    "scope_paths": [
      "backend/domain/result_dataset_models.py",
      "backend/infrastructure/office/llcr_result_workbook_gateway.py",
      "backend/infrastructure/office/test_report_document_gateway.py",
      "tests/unit/test_llcr_result_workbook_gateway.py",
      "tests/unit/test_test_report_document_gateway.py",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [],
    "activation_head": "07e4c15bd784b404182475d22c6765c6378e5966",
    "started_at": "2026-10-22T16:06:06.821761Z",
    "updated_at": "2026-10-22T23:21:00.160079Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_LLCR_RESULT_SEMANTICS_20261023",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_LLCR_RESULT_SEMANTICS_20261023",
      "subject": "1c5c8a07701860d827ac0b0032e1040bf6b76a16",
      "summary": "LLCR quantity/stage semantics corrected; 261 affected tests passed in user-run ordinary PowerShell. Previous host-only hardlink failures resolved without weakening protection. Real reports/templates/project data unchanged.",
      "scope_ok": true,
      "changed_paths": [
        "backend/domain/result_dataset_models.py",
        "backend/infrastructure/office/llcr_result_workbook_gateway.py",
        "backend/infrastructure/office/test_report_document_gateway.py",
        "docs/report_generation_architecture.md",
        "tests/unit/test_llcr_result_workbook_gateway.py",
        "tests/unit/test_test_report_document_gateway.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Affected final matrix",
          "tests": 261,
          "failures": 0,
          "errors": 0,
          "skipped": 0,
          "seconds": 83.058,
          "timestamp": "2026-10-23T07:15:03.069156+08:00",
          "executor": "User ran supplied isolated PowerShell runner; assistant inspected JUnit results and exact case set",
          "evidence_path": "tmp/llcr_semantics_20261023/qa-external.xml",
          "raw_sha256": "c348f31d43362b0e3e8a0324e958f2e6e35922847d2eadcfd074e158adc9317c",
          "result": "All 15 prior failed cases now pass. Product/test bytes unchanged since implementation commit; only board changed."
        },
        {
          "status": "passed",
          "name": "Developer RED/GREEN",
          "result": "56 targeted checks passed, including absolute versus delta, final-only stage, cache mismatch, v1 shorthand ambiguity and duplicate appendix identity."
        },
        {
          "status": "passed",
          "name": "Two isolated reference copies",
          "result": "Single/two-row appendix headers and No. result tables; protected round-trip, unrelated XML/package parts, repeat-byte identity passed; original 204 file hashes and mtimes unchanged."
        },
        {
          "status": "passed",
          "name": "Focused review",
          "result": "Previous sequential same-agent standards/spec review retained; no product/test changes since review, no remaining code findings."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "context": "same agent",
          "summary": "Scoped implementation and 56 targeted checks; no authoritative file mutations."
        },
        "reviewer": {
          "status": "passed",
          "context": "sequential focused same-agent review, not independent",
          "standards_findings": 0,
          "spec_findings": 0,
          "limitations": [
            "Word visual rendering remains unverified; OOXML fidelity is not a pixel or fixed-page-count guarantee.",
            "Ambiguous v1 Summary datasets require reimport/confirmation; no historical data is silently rewritten.",
            "Reference-copy tests use synthetic numeric edits, not reapproval of actual business measurements."
          ]
        },
        "qa": {
          "status": "passed",
          "context": "User executed final affected matrix outside restricted host; assistant verified results",
          "automated": "261 passed; 0 failures/errors/skips",
          "limitations": [
            "Word visual rendering remains unverified; OOXML fidelity is not a pixel or fixed-page-count guarantee.",
            "Ambiguous v1 Summary datasets require reimport/confirmation; no historical data is silently rewritten.",
            "Reference-copy tests use synthetic numeric edits, not reapproval of actual business measurements."
          ]
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "subject": "1c5c8a07701860d827ac0b0032e1040bf6b76a16",
        "tree": "d8ce8f4ba65e515f6892d667fcdbad579f5172d3",
        "clean": true,
        "pushed": false
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_REPORT_LOCAL_UPDATE_FIDELITY_20261022",
    "tier": "standard",
    "subject": "b5dcb41b6d75fdd65036088549e582c6f3faa043",
    "summary": "Preserve approved report formatting during local LLCR and equipment updates",
    "disposition": "completed",
    "decision_ref": "User 2026-10-23 explicitly closes fidelity task and authorizes next LLCR semantic fix with isolated validation only",
    "closed_at": "2026-10-22T16:06:06.821761Z"
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
