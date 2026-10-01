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
    "task_id": "TASK_MATRIX_IR_DWV_TEST_POINTS_20260930",
    "summary": "Add confirmed Matrix IR/DWV points and Fee quantities",
    "tier": "standard",
    "route": "sol_build_review_qa",
    "scope": "Add IR/DWV per-sample test point counts in existing Matrix-owned JSON plan; confirm-only quantity projection and Fee refresh; preserve LLCR/CR and old snapshots. No source document writes or new record workbook feature.",
    "scope_paths": [
      "backend/domain/matrix_contact_measurement_models.py",
      "backend/api/matrix_editor_session_dtos.py",
      "backend/api/matrix_editor_session_response_mappers.py",
      "backend/application/matrix_test_points_authority.py",
      "backend/application/matrix_step_quantity_authority_builder.py",
      "frontend/src/api/client.ts",
      "frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx",
      "frontend/src/features/matrix-editor",
      "tests/integration",
      "docs/PROJECT_CONTEXT.md"
    ],
    "risk_reasons": [],
    "activation_head": "536f5082336d0feab82ba3e60d9fa47bc9da1f8f",
    "started_at": "2026-09-30T14:45:40.768073Z",
    "updated_at": "2026-10-01T01:03:19.040002Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_IR_DWV_TEST_POINTS_20260930",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "summary": "Shared IR/DWV measurement-pair text box sits directly beside the heading, without redundant count label, category or Group controls. Original pair labels persist in Matrix-owned JSON; backend counts nonempty comma/semicolon/ideographic-comma/newline separated entries, preserving internal &, and and hyphens. Confirm Matrix alone publishes samples times pairs to Fee. Legacy numeric values remain readable, unequal legacy values require explicit user correction, clears cannot resurrect old quantities, LLCR/CR fingerprints unchanged. No source document or business output writes.",
      "changed_paths": [
        "backend/api/matrix_editor_session_dtos.py",
        "backend/api/matrix_editor_session_response_mappers.py",
        "backend/application/matrix_step_quantity_authority_builder.py",
        "backend/application/matrix_test_points_authority.py",
        "backend/domain/matrix_contact_measurement_models.py",
        "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/api/client.ts",
        "frontend/src/contact-measurement-plan.css",
        "frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "tests/integration/test_matrix_ir_dwv_points_api.py"
      ],
      "subject": "af1ef613190c4bf6ddd277c0992a4d30c34db1f2",
      "version": 1,
      "integration": {
        "status": "passed",
        "summary": "Clean local master implementation commit af1ef613190c4bf6ddd277c0992a4d30c34db1f2; exact activation-to-subject paths reported; no unrelated edits or external publication."
      },
      "validation": [
        {
          "name": "Final affected Python matrix",
          "status": "passed",
          "result": "449 passed, one existing Starlette deprecation warning. Covers Matrix sessions, JSON persistence, quantity authority, Fee and LLCR/CR consumers; installed-Office marked tests excluded."
        },
        {
          "name": "Final affected frontend",
          "status": "passed",
          "result": "361 passed, one pre-existing skip across Matrix editor, contact-measurement and Fee Evaluation."
        },
        {
          "name": "Frontend production build",
          "status": "passed",
          "result": "npm run build passed TypeScript and Vite after final code and test changes."
        },
        {
          "name": "Actual browser visual smoke",
          "status": "passed",
          "result": "Read-only localhost Matrix page inspected in separate browser tab. One adjacent shared text area, no Points per sample label or IR/DWV categories; LLCR/CR intact; Confirm disabled with no edit. No typing or business data modification."
        }
      ],
      "scope_ok": true,
      "task_id": "TASK_MATRIX_IR_DWV_TEST_POINTS_20260930",
      "roles": {
        "reviewer": {
          "status": "passed",
          "summary": "Primary-agent sequential Standards and Spec review on exact final diff; no outstanding findings. JSON optional field preserves old contact hashes, backend calculates quantities once per profile, no new categories/Group controls, no new dependency or file output features. Not independent agent review."
        },
        "developer": {
          "status": "passed",
          "summary": "RED/GREEN API: absent pair field failed persisted reopening then passed saved text and confirmed Fee Units. RED/GREEN UI: missing text box failed then draft save/confirm passed. Tests cover four-pair sample, separator syntax, limits, numeric legacy, changes from 5 samples/4 pairs to 7 samples/3 pairs, clear precedence and confirmation-only updates."
        },
        "qa": {
          "status": "passed",
          "summary": "449 Python and 361 frontend passed on final reviewed state, one prior frontend skip; production build and actual browser visual check passed. Browser was read-only; save/confirm behavior exercised via isolated API and UI tests, not live business project writes. No packaged release run claimed."
        }
      },
      "schema": "connlab.sol-task-report"
    }
  },
  "last_closed": {
    "task_id": "TASK_FEE_MATRIX_SELECTIVE_REUSE_20260930",
    "tier": "standard",
    "subject": "c426f24799a74609aeddb0a76ca716b3ff262f3c",
    "summary": "Selectively reuse confirmed Fee edits across Matrix revisions",
    "disposition": "completed",
    "decision_ref": "User explicit final close request on 2026-09-30.",
    "closed_at": "2026-09-30T11:32:03.830481Z"
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
