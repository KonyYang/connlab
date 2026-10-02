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
    "task_id": "TASK_IR_DWV_DOWNLOAD_NAME_AUTHORITY_20261002",
    "summary": "Align IR/DWV download names with confirmed LTR and Matrix authority",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Retain existing LLCR-shared official Test results publication and archive safety without mutation-policy changes. Correct browser download names to authoritative registered LTR plus IR&DWV Record, with draft suffix only for unconfirmed Matrix; retain isolated internal UUID artifact paths and compatibility when LTR unavailable. Verify confirmed official, confirmed no-folder, unconfirmed and stale-token cases through public API, plus existing LLCR/IR-DWV UI regressions. Update PROJECT_CONTEXT; preserve and restore unrelated design draft.",
    "scope_paths": [
      "backend/api/routes_matrix_editor_ir_dwv_record_generation.py",
      "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
      "backend/application/matrix_editor_ir_dwv_record_generation_service.py",
      "tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "58a847ba6abaeed3bfd0a5e4487045682d860b60",
    "started_at": "2026-10-02T04:29:01.724211Z",
    "updated_at": "2026-10-02T06:06:56.369435Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_IR_DWV_DOWNLOAD_NAME_AUTHORITY_20261002",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_IR_DWV_DOWNLOAD_NAME_AUTHORITY_20261002",
      "subject": "557d5bdeb4f084c046b7b629027b36a024c5568c",
      "summary": "Align public IR/DWV download filenames with registered LTR and server-verified Matrix authority. Preserve existing shared LLCR/CR official Test results publication, archive approval and UUID artifact isolation. Confirmed no-folder downloads omit draft; unconfirmed downloads use draft suffix. No workbook content, frontend implementation or official mutation policy changed.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_matrix_editor_ir_dwv_record_generation.py",
        "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
        "backend/application/matrix_editor_ir_dwv_record_generation_service.py",
        "tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py",
        "docs/PROJECT_CONTEXT.md"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "TDD RED/GREEN download contract",
          "result": "Four isolated public API scenarios initially failed on Content-Disposition only (4 failed, 9 deselected); after implementation all four passed. Covers confirmed no folder, draft no folder, draft with folder, altered quantities falsely marked not pending. Repeated downloads retain distinct internal artifacts."
        },
        {
          "status": "passed",
          "name": "final affected backend QA",
          "result": "pytest -p no:cacheprovider tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py -q: 36 passed in55.22s, one existing StarletteDeprecationWarning. Isolated real DI SQLite/file tests exercise official create/archive, conflict and stale-token behavior; no business files written."
        },
        {
          "status": "passed",
          "name": "final affected frontend QA",
          "result": "npm.cmd test -- src/features/matrix-editor/IrDwvRecordDownloadAction.test.tsx src/features/matrix-editor/LlcrCrRecordDownloadAction.test.tsx src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.test.tsx: 3files,10tests passed. Frontend implementation unchanged; production build, live browser and release package not rerun."
        },
        {
          "status": "passed",
          "name": "two-axis focused review and diff hygiene",
          "result": "Primary agent sequential Standards and Spec review of exact working diff against58a847ba; zero actionable findings per axis. Existing layering, source selection, safe formal archive/publication and cleanup retained. git diff --check exit0. No independent agents claimed."
        },
        {
          "status": "passed",
          "name": "unchanged validated code and bounded document preservation",
          "result": "Only board changed since verified code69fde0bc; git diff69fde0bc HEAD excluding docs/task_board.md empty, status clean after exact user-approved two-path stash. Design documents not committed or deleted; stash backup retained. Byte-identical restoration will be verified immediately after board recording."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "context": "Primary agent implemented coherent TDD slice, observed meaningful RED/GREEN; only bounded server download label and validated authority return changed."
        },
        "reviewer": {
          "status": "passed",
          "context": "Focused sequential primary-agent Standards then Spec review, zero findings on each. This is not independent-agent review."
        },
        "qa": {
          "status": "passed",
          "context": "Primary-agent final QA after final byte changes:36 backend +10 frontend tests; isolated formal-write tests only. No Office, business-folder, browser or release-package verification claimed."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "557d5bdeb4f084c046b7b629027b36a024c5568c",
        "code_subject": "69fde0bce5cc464b7e7d65fc19f66b225133b3f0",
        "facts": "Task code commit69fde0bce5cc464b7e7d65fc19f66b225133b3f0; exact current HEAD557d5bdeb4f084c046b7b629027b36a024c5568c adds only sole-writer board recovery checkpoint. Nonboard tree compared unchanged, so existing final46 tests remain applicable. User explicitly authorized reversible preservation of two stopped design drafts: exact two-path stash e9c8d1279f925089e4bd20ed3b8bd41b972b4271. Before hashes VBA B83490D542627A02D1568BF5FA8D5B2F37C7B8DF6E258980EAC9EA51F333D5C0, photo D336D7FCCDFBE8651853A5278C36D2A11D1B8F5DF2F68151F1C380BDE3FE79EC. Immediately restore both current versions after recording; preserve older backups without applying them over newer versions."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_DOC_IR_DWV_CONTEXT_SYNC_20261002",
    "tier": "micro",
    "subject": "93434491301e159877e5d26653386ab82f793d5d",
    "summary": "Correct obsolete IR/DWV workbook implementation status in project context",
    "disposition": "completed",
    "decision_ref": "User final close 2026-10-02 after clarification: specification point extraction is not required; manually entered Matrix points are authoritative.",
    "closed_at": "2026-10-02T04:20:05.226986Z"
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
