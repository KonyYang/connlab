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
    "updated_at": "2026-09-30T15:42:28.762243Z",
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
      "roles": {
        "qa": {
          "status": "passed",
          "summary": "One final affected matrix after last implementation/test edits: 490 Python, 357 Vitest, production build, read-only real-browser layout. No whole-repository or packaged-release validation claimed."
        },
        "developer": {
          "status": "passed",
          "summary": "TDD RED: IR-only profile rejected and inputs absent; known units lost for missing/unsupported duration. GREEN: new 11 API/compatibility tests and 2 UI regressions. Real isolated DB/API verifies confirm-only publication and Fee price preservation with updated quantities."
        },
        "reviewer": {
          "status": "passed",
          "summary": "Sequential focused Standards and Spec review in primary context, not an independent agent. Exact diff checked against request, old JSON compatibility, optional settings, contact fingerprints, quantity ownership/clearing, selected steps, and Fee authority boundary. No remaining blocking findings."
        }
      },
      "scope_ok": true,
      "schema": "connlab.sol-task-report",
      "changed_paths": [
        "backend/api/matrix_editor_session_dtos.py",
        "backend/api/matrix_editor_session_response_mappers.py",
        "backend/application/matrix_step_quantity_authority_builder.py",
        "backend/application/matrix_test_points_authority.py",
        "backend/domain/matrix_contact_measurement_models.py",
        "backend/modules/fee_evaluation/fee_reviewed_extension_defaults.py",
        "docs/PROJECT_CONTEXT.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
        "frontend/src/features/matrix-editor/matrixStepWorkspaceModel.ts",
        "tests/integration/test_matrix_ir_dwv_points_api.py"
      ],
      "integration": {
        "status": "passed",
        "summary": "Clean exact local master commit a830c6305d4fbe2d3838381559def5886193bfff; no unrelated work changed."
      },
      "validation": [
        {
          "status": "passed",
          "name": "Backend affected calculation and Matrix/Fee API suite",
          "result": "490 passed, one existing Starlette deprecation warning"
        },
        {
          "status": "passed",
          "name": "Frontend Matrix/Test points/Fee suite",
          "result": "357 passed; one pre-existing skipped profiling test"
        },
        {
          "status": "passed",
          "name": "Production build",
          "result": "tsc -b and vite build passed"
        },
        {
          "status": "passed",
          "name": "In-app browser read-only smoke",
          "result": "Actual project Matrix page renders separate IR/DWV controls, selected-step coverage, missing-count warning, and unchanged LLCR/CR controls. Business Confirm not clicked."
        }
      ],
      "task_id": "TASK_MATRIX_IR_DWV_TEST_POINTS_20260930",
      "summary": "Implemented optional Matrix IR/DWV per-sample point settings, confirm-only quantity publication, Fee Units refresh, compatibility, validation, and UI coverage. No business project or supplied attachment edits; no result-workbook generator or release rebuild.",
      "subject": "a830c6305d4fbe2d3838381559def5886193bfff",
      "version": 1
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
