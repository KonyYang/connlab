# ConnLab Task Board

> Authority: the compact control block below. Workflow: `docs/project_management/SOL_NATIVE_WORKFLOW.md`.
> WIP=1. GPT-5.6 Sol routes work as micro, standard, or high risk and runs routine stages
> automatically until the User's final Close.

<!-- CONNLAB_EXECUTION_CONTROL_BEGIN -->
```json
{
  "schema": "connlab.sol-task-control",
  "version": 1,
  "mode": "sol_native",
  "wip_limit": 1,
  "state": "running",
  "active": {
    "task_id": "TASK_MATRIX_SCHEDULE_UNIFIED_CONFIRM",
    "summary": "Unify Project Schedule editing and authority confirmation with Confirm Matrix while retaining existing schedule revisions and safe folder/output gating.",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Matrix Editor schedule fields become part of the single Confirm Matrix action; schedule-only edits enable confirm; no standalone Confirm schedule; atomic authority transition; preserve existing schedule revisions, legacy clients, and required-date safety for generated outputs.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/matrix_editor_session_dtos.py",
      "backend/api/project_folder_generation_composition.py",
      "backend/api/project_folder_preflight.py",
      "backend/api/routes_matrix_editor_session.py",
      "backend/api/routes_project_schedule.py",
      "backend/application/confirmed_matrix_authority_service.py",
      "backend/application/customer_feedback_form_generation_service.py",
      "backend/application/matrix_editor_live_xlsx_publication_service.py",
      "backend/application/matrix_editor_session_signature.py",
      "backend/application/matrix_revision_flow_service.py",
      "backend/application/matrix_schedule_planning.py",
      "backend/application/project_application_form_write_back_service.py",
      "backend/application/project_schedule_output.py",
      "backend/application/project_schedule_service.py",
      "backend/application/project_section2_sync_service.py",
      "backend/application/test_report_draft_service.py",
      "backend/infrastructure/storage/repositories/project_schedule.py",
      "docs/PROJECT_CONTEXT.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.lifecycle.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.test.tsx",
      "frontend/src/features/matrix-editor/MatrixSchedulePlanningCard.tsx",
      "frontend/src/features/matrix-editor/matrixEditorDraftModel.ts",
      "tests/integration/test_confirmed_matrix_authority_api.py",
      "tests/integration/test_confirmed_matrix_authority_history_api.py",
      "tests/integration/test_confirmed_matrix_runtime_projection_api.py",
      "tests/integration/test_confirmed_matrix_test_record_generation_api.py",
      "tests/integration/test_confirmed_matrix_test_record_preview_api.py",
      "tests/integration/test_generation_workspace_process_recovery.py",
      "tests/integration/test_matrix_duration_authority_publication_api.py",
      "tests/integration/test_matrix_editor_session_api.py",
      "tests/integration/test_matrix_revision_flow_api.py",
      "tests/integration/test_matrix_to_test_record_smoke_flow_api.py",
      "tests/integration/test_matrix_typed_duration_authority_round_trip_api.py",
      "tests/integration/test_project_folder_generation_api.py",
      "tests/integration/test_project_folder_generation_complete_chain.py",
      "tests/integration/test_project_schedule_api.py",
      "tests/unit/test_confirmed_matrix_authority_service.py",
      "tests/unit/test_matrix_editor_session_service.py",
      "tests/unit/test_matrix_revision_flow_service.py",
      "tests/unit/test_matrix_schedule_planning.py",
      "tests/unit/test_project_schedule_service.py",
      "tests/unit/test_project_section2_sync_service.py"
    ],
    "risk_reasons": [
      "Changes authoritative Project Schedule and Matrix confirmation in one transaction and affects project folder/output eligibility."
    ],
    "activation_head": "9fc60223f98beead8649e60c5f520445badaeaa8",
    "started_at": "2026-09-26T08:41:04.702813Z",
    "updated_at": "2026-09-27T00:44:09.524786Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_MATRIX_SCHEDULE_UNIFIED_CONFIRM",
      "stage": "scope_manifest_correction",
      "status": "running",
      "summary": "User 2026-09-27 explicitly approved exact 9fc60223..86c2a372 diff excluding docs/task_board.md, 47 paths, superseding earlier 18/29-path questions.",
      "requires_user": false
    },
    "report": null
  },
  "last_closed": {
    "task_id": "TASK_INTAKE_LTR_ROW_COMPARISON_LAYOUT",
    "tier": "standard",
    "subject": "c23d302ccaf33c292546c140b582e8970a9972a1",
    "summary": "Show existing and proposed LTR workbook row values side by side in a single field-aligned English comparison table.",
    "disposition": "completed",
    "decision_ref": "User final close after verified intake LTR comparison layout revision.",
    "closed_at": "2026-09-26T08:11:58.184270Z"
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
