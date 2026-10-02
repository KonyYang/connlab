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
    "updated_at": "2026-10-02T06:29:58.793927Z",
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
      "subject": "16dc53e5fa1329e0ac4ebe2e1e81dcbf43251395",
      "summary": "IR/DWV file naming and output routing remain aligned with registered LTR and server-verified Matrix authority. Acceptance revision simplifies the IR/DWV card: suppress routine source-information bullets in card and dialog, preserve actionable errors/success/destination/archive confirmation; shrink input and align Form to its right, including narrow viewports. LLCR/CR information retained. No backend, workbook content, authority, archive or storage policy change in this revision.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/routes_matrix_editor_ir_dwv_record_generation.py",
        "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
        "backend/application/matrix_editor_ir_dwv_record_generation_service.py",
        "tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/contact-measurement-plan.css",
        "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.tsx",
        "frontend/src/features/matrix-editor/IrDwvRecordDownloadAction.test.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.test.tsx"
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
          "name": "revision TDD RED/GREEN concise feedback",
          "result": "IR/DWV action test RED:3failed,1passed because routine source bullets remained in destination dialog, success card and downloaded draft. GREEN4passed after IR-only suppression; API boundary mocks, no private hook mocks. Existing archive/publish failure test retains actionable error behavior."
        },
        {
          "status": "passed",
          "name": "final revision frontend QA",
          "result": "npm.cmd test -- src/features/matrix-editor/IrDwvRecordDownloadAction.test.tsx src/features/matrix-editor/LlcrCrRecordDownloadAction.test.tsx src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.test.tsx src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx:4files,74tests passed on final bytes,31.38s. Includes preserved CR source-information assertion and63 Matrix editing regressions."
        },
        {
          "status": "passed",
          "name": "final production build",
          "result": "npm.cmd run build exit0: tsc -b and Vite7.3.2,157modules,794ms Vite build. Sequential after Vitest. No packaged application rebuilt/run."
        },
        {
          "status": "passed",
          "name": "actual browser layout",
          "result": "Existing localhost business page inspected read-only after Vite HMR. At676x804 input210.47px wide and Form105.44px wide immediately right with8px gap, vertically aligned. At610x804 title moves above but input306.56px and button remain same row. Original viewport reset, points still P1&P2,S1&Housing. Did not click Confirm Matrix or any formal generation/publish action. Screenshot saved outside repository: C:/Users/White/.codex/visualizations/2026/08/23/01a02cd2-b111-7c53-a4b3-d1e1802d7ed3/ir-dwv-compact-card-1790922450158.png. Download/success/failure feedback behavior proven by action tests rather than business file writes."
        },
        {
          "status": "passed",
          "name": "Standards and Spec focused review",
          "result": "Primary sequential Standards/Spec review of acceptance revision against108854ab,0actionable findings per axis. CSS restricted to shared IR/DWV card; generic wrappers use display:contents so status/errors span row without widening action column. IR-only routine-information suppression; modal authority, destination/archive warnings, blockers, busy state and LLCR/CR preserved. git diff --check exit0. Not independent agents."
        }
      ],
      "roles": {
        "developer": {
          "status": "passed",
          "context": "Primary agent preserved original server output work, automatically Revise on acceptance adjustment; meaningful UI TDD RED3fails to GREEN4passes."
        },
        "reviewer": {
          "status": "passed",
          "context": "Focused primary sequential Standards then Spec review of exact final revision, zero findings each; LLCR regression assertion added. No independent-agent review claimed."
        },
        "qa": {
          "status": "passed",
          "context": "Final frontend74tests, production build and actual read-only browser layout at676/610 passed. Prior36backend tests remain applicable because backend/test subtree unchanged. No release-package or business-folder publication rerun."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "16dc53e5fa1329e0ac4ebe2e1e81dcbf43251395",
        "code_subject": "16dc53e5fa1329e0ac4ebe2e1e81dcbf43251395",
        "facts": "Direct master16dc53e5; exact9 nonboard paths since activation58a847ba. Clean before finish. User-approved two-path current design drafts preserved temporarily in exact stash ec46499117d35dbed695c3bbc3d395a7719c85e7, before hashes VBA B83490D542627A02D1568BF5FA8D5B2F37C7B8DF6E258980EAC9EA51F333D5C0 and photo D336D7FCCDFBE8651853A5278C36D2A11D1B8F5DF2F68151F1C380BDE3FE79EC; restore immediately after board recording and retain backup. No final close or publication authorized."
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
