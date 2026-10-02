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
    "updated_at": "2026-10-02T07:47:30.502547Z",
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
      "subject": "4457ae6e2af6d44427fbe1d812b0332330f91a52",
      "summary": "Retains delivered IR/DWV naming and concise card changes. Matrix Editor acceptance fix now checks latest session after draft conflict, preserves current inputs, recreates a missing draft only against unchanged confirmed Matrix with no available working draft, and retries once with newly returned tokens. Changed authority, another available draft, edits during recovery and network failure do not trigger unsafe confirmation. No backend schema/authority/filesystem publication change. Residual verification limitation: actual in-app browser smoke is blocked by browser-control timeouts and is NOT counted passed; selected metadata is accessible but DOM/console inspection cannot complete. User reports current normal clicking; agent did not click, clear business drafts or publish authority.7 public component recovery cases passed instead.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_matrix_editor_ir_dwv_record_generation.py",
        "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
        "backend/application/matrix_editor_ir_dwv_record_generation_service.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/contact-measurement-plan.css",
        "frontend/src/features/matrix-editor/IrDwvRecordDownloadAction.test.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.test.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.confirmRecovery.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/useMatrixDraftPersistence.ts",
        "tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py"
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
          "result": "pytest -p no:cacheprovider tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py tests/integration/test_matrix_editor_llcr_cr_record_generation_api.py tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py -q: 36 passed in55.22s, one existing StarletteDeprecationWarning. Isolated real DI SQLite/file tests exercise official create/archive, conflict and stale-token behavior; no business files written. Backend/test/PROJECT_CONTEXT diff108854ab..16dc53e5 empty; this prior backend result remains applicable without duplicate execution."
        },
        {
          "status": "passed",
          "name": "Matrix recovery TDD RED/GREEN",
          "result": "After fixing test import assembly (not counted as behavioral RED), two public component tests failed on missing-draft recovery and authority-change feedback. GREEN2 after implementation. Final7 recovery cases cover fresh tokens/current inputs, changed authority, another available draft, failed save then user retry, edit-during-save plus disabled duplicate confirm, failed session check, and one-attempt limit. API mocks only at network boundary; no hook replacement."
        },
        {
          "status": "passed",
          "name": "Final Matrix Editor QA",
          "result": "npm.cmd test -- src/features/matrix-editor:178 passed,1 pre-existing skipped,25 test files passed/1 skipped,20.14s. Final reviewed code bytes, all editing/import/cancellation/IR-DWV/LLCR-CR tests included. Developer targeted25 passed prior to full QA."
        },
        {
          "status": "passed",
          "name": "Final frontend production build",
          "result": "npm.cmd run build:TypeScript tsc-b and Vite7.3.2 passed,157modules,859ms Vite build. Sequential after complete Vitest. Release package not rebuilt/run."
        },
        {
          "status": "passed",
          "name": "Standards and Spec focused review",
          "result": "Primary agent sequential exact working diff review before QA,0 actionable findings per axis. Draft lifecycle orchestration remains in existing persistence hook; same-project/base-version checks, generation and content signature guards, returned request pairs captured payload with fresh response tokens. Available server draft never overwritten by recovery preflight; new authority never auto-rebased. Existing active-matrix automatic retry removed with adjusted boundary tests. No external file or backend authority policy change. git diff --check passed. No independent agents claimed."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "context": "Primary same task acceptance revision; preserve unrelated design drafts, meaningful RED/GREEN2 then7 protection cases."
        },
        "reviewer": {
          "status": "passed",
          "context": "Primary sequential Standards and Spec review,0 findings each; not independent agents."
        },
        "qa": {
          "status": "passed",
          "context": "Exact reviewed bytes178frontend tests+1existing skip and production build passed; browser control unavailable explicitly excluded from passed checks, no release-package claim."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "4457ae6e2af6d44427fbe1d812b0332330f91a52",
        "code_subject": "4457ae6e2af6d44427fbe1d812b0332330f91a52",
        "facts": "Direct master4457ae6e; exact13 nonboard paths since activation58a847ba. Current acceptance code5 nonboard paths. Unrelated2 design docs retained hash-identically; user-approved bounded temporary stash only for clean board finish and immediate restoration. No final Close/publication."
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
