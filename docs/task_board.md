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
    "task_id": "TASK_REPORT_LOCAL_UPDATE_FIDELITY_20261022",
    "summary": "Preserve approved report formatting during local LLCR and equipment updates",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Restrict existing section updates to owned content and preserve unrelated typography, pagination, drawings, headers and manual content. Validate isolated copies only; no real report/template/project writes and no LLCR semantic changes.",
    "scope_paths": [
      "backend/infrastructure/office/test_report_document_gateway.py",
      "tests/unit/test_test_report_document_gateway.py",
      "tests/unit/test_report_update_fidelity.py",
      "docs/report_generation_architecture.md"
    ],
    "risk_reasons": [],
    "activation_head": "04158c78bf89de26d166ff77ed1df65fa1ed5fef",
    "started_at": "2026-10-22T15:38:25.782158Z",
    "updated_at": "2026-10-22T15:57:51.960351Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_REPORT_LOCAL_UPDATE_FIDELITY_20261022",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_REPORT_LOCAL_UPDATE_FIDELITY_20261022",
      "subject": "b5dcb41b6d75fdd65036088549e582c6f3faa043",
      "summary": "Local LLCR/equipment updates preserve approved report formatting and untouched OOXML parts. Reference equipment/protection copies passed; Word visual acceptance remains unverified.",
      "scope_ok": true,
      "changed_paths": [
        "backend/infrastructure/office/test_report_document_gateway.py",
        "docs/report_generation_architecture.md",
        "tests/unit/test_test_report_document_gateway.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "Affected report gateway/application/API and protection tests",
          "result": "214 passed, one existing dependency deprecation warning",
          "seconds": 129.33
        },
        {
          "status": "passed",
          "name": "Regression RED/GREEN",
          "result": "Reproduced global formatting, table rebuilding, unrelated ZIP reserialization and incompatible merged-statistics failures; corrected on final tested implementation."
        },
        {
          "status": "passed",
          "name": "Two authoritative reference copies",
          "result": "17/22 equipment rows; unrelated body XML and all other ZIP parts preserved; repeat unencrypted output byte-identical; protected roundtrip identical decrypted package; all 204 original files SHA256 and mtime unchanged."
        },
        {
          "status": "passed",
          "name": "Exact diff review and whitespace",
          "result": "Standards and spec passes by the same agent; no remaining blocking code findings. Visual limitation explicitly retained."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "context": "same agent",
          "summary": "Implemented and regression-tested scoped adapter change; no real report/template/project writes; LLCR semantics unchanged."
        },
        "reviewer": {
          "status": "passed",
          "context": "sequential focused pass by same agent, not independent",
          "standards_findings": 0,
          "spec_findings": 0,
          "limitations": [
            "Word visual export stalled opening both updated and untouched isolated copies; no pixel/page-count acceptance claimed. Only owned test Word processes were terminated.",
            "Real reference Final LLCR stages and different appendix headers remain next-batch semantic/mapping work.",
            "Changed cell values inherit paragraph/run properties; mixed formatting inside replaced text and unchanged page counts after content growth are not guaranteed."
          ]
        },
        "qa": {
          "status": "passed",
          "context": "same agent final affected-matrix pass",
          "automated": "214 passed",
          "limitations": [
            "Word visual export stalled opening both updated and untouched isolated copies; no pixel/page-count acceptance claimed. Only owned test Word processes were terminated.",
            "Real reference Final LLCR stages and different appendix headers remain next-batch semantic/mapping work.",
            "Changed cell values inherit paragraph/run properties; mixed formatting inside replaced text and unchanged page counts after content growth are not guaranteed."
          ]
        }
      },
      "integration": {
        "status": "passed",
        "branch": "master",
        "subject": "b5dcb41b6d75fdd65036088549e582c6f3faa043",
        "tree": "e9db412371f54322507d01f7d97787efbc53b0c9",
        "clean": true,
        "pushed": false
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_CUSTOMER_SAMPLE_MATERIAL_REDACTION_20261022",
    "tier": "high_risk",
    "subject": "0ef4bbfb032350d68894fa9b4157e0e128c5e02a",
    "summary": "Generate a customer report with fixed sample material redaction rules",
    "disposition": "completed",
    "decision_ref": "User 2026-10-22 explicitly confirmed close and next scoped fidelity implementation",
    "closed_at": "2026-10-22T15:38:25.782158Z"
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
