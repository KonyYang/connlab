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
    "task_id": "TASK_DRAFT_DOWNLOAD_AVAILABLE_INFO_20261012",
    "summary": "Populate available project information in draft downloads without authority writeback",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Download-only Fee Form, Test Record and LLCR/CR available metadata; draft-first read policy, no fabricated actual facts, preserve formal confirmation and publication gates",
    "scope_paths": [
      "backend/application",
      "backend/api/dependencies.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/infrastructure/office/llcr_cr_record_workbook_layout.py",
      "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
      "tests/unit",
      "tests/integration",
      "docs/draft_download_information.md"
    ],
    "risk_reasons": [],
    "activation_head": "4d576f921c1e96c2ee425f3da5c37edbfe451b01",
    "started_at": "2026-10-12T15:11:07.002360Z",
    "updated_at": "2026-10-12T15:47:41.024860Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_DRAFT_DOWNLOAD_AVAILABLE_INFO_20261012",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "roles": {
        "reviewer": {
          "summary": "Separate sequential same-agent Standards and Spec passes: 0 outstanding findings; no independent-agent claim; formal default remains strict and metadata is fingerprinted",
          "status": "passed"
        },
        "qa": {
          "summary": "Full affected matrix and native Excel QA passed; official publication/folder recovery gates and no download authority writes covered",
          "status": "passed"
        },
        "developer": {
          "summary": "RED/GREEN at public reader, Fee download validation and actual DOCX/XLSX HTTP seams; current Matrix text and registered-description/specification compatibility retained",
          "status": "passed"
        }
      },
      "summary": "Draft-first available information fills Fee Form, both Word Test Record routes, LLCR/CR and IR/DWV downloads; formal contact forms fill registered/confirmed metadata while preserving authority gates",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/routes_confirmed_matrix_test_record_generation.py",
        "backend/application/confirmed_matrix_llcr_cr_record_preview_service.py",
        "backend/application/confirmed_matrix_llcr_cr_record_projection.py",
        "backend/application/confirmed_matrix_test_record_document_generation_service.py",
        "backend/application/fee_form_publication_service.py",
        "backend/application/matrix_editor_ir_dwv_record_generation_service.py",
        "backend/application/matrix_editor_llcr_cr_record_generation_service.py",
        "backend/application/matrix_editor_test_record_document_generation_service.py",
        "backend/application/project_basic_information_output.py",
        "backend/application/project_basic_information_output_identity.py",
        "backend/application/project_identity.py",
        "backend/infrastructure/office/llcr_cr_record_workbook_layout.py",
        "backend/infrastructure/office/llcr_cr_specialized_record_workbook_gateway.py",
        "docs/draft_download_information.md",
        "tests/integration/test_confirmed_matrix_test_record_generation_api.py",
        "tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py",
        "tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py",
        "tests/integration/test_matrix_editor_test_record_generation_api.py",
        "tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py",
        "tests/unit/test_draft_download_basic_information.py",
        "tests/unit/test_fee_form_publication_service.py",
        "tests/unit/test_ir_dwv_record_projection.py"
      ],
      "subject": "94286484b58dbd880af04fcf4b6fcc76ebf7be99",
      "version": 1,
      "integration": {
        "summary": "Clean local master at exact subject; no remote publication or task closure",
        "status": "passed"
      },
      "validation": [
        {
          "status": "passed",
          "name": "affected backend matrix",
          "summary": "357 tests passed across 22 unit/integration modules on final code/test bytes; existing Starlette/httpx warning only"
        },
        {
          "status": "passed",
          "name": "native Excel read-only QA",
          "summary": "Isolated LLCR draft opened with LTR, tester Min and current condition; unknown checker/equipment blank, literal tester and no recalculation errors"
        },
        {
          "status": "passed",
          "name": "exact diff",
          "summary": "git diff --check clean; same-agent standards/spec review; no UI changes or frontend-build claim"
        }
      ],
      "schema": "connlab.sol-task-report",
      "task_id": "TASK_DRAFT_DOWNLOAD_AVAILABLE_INFO_20261012"
    }
  },
  "last_closed": {
    "task_id": "TASK_TEMPERATURE_TEST_INFO_20261011",
    "tier": "standard",
    "subject": "fa8d387c0b3e79ec03279f8f483a9d629517b331",
    "summary": "Add editable temperature report metadata and optional project association",
    "disposition": "completed",
    "decision_ref": "User accepted completed temperature export changes and requested close on 2026-10-12",
    "closed_at": "2026-10-12T00:15:25.069817Z"
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
