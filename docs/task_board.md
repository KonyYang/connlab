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
    "task_id": "TASK_362_IR_DWV_RECORD_WORKBOOK_20261001",
    "summary": "Implement IR/DWV Matrix record workbook end to end",
    "tier": "high_risk",
    "route": "full_chain",
    "scope": "Implement the approved IR/DWV workbook work order exactly: P1 template inventory, backup/purification, openpyxl layout and writer, artifact store, unit tests and golden cell diff gate; P2 projection, generation/publication chain, external resource, routes and integration tests; P3 Matrix Editor header action, API client, UI tests and end-to-end verification. Preserve LLCR/CR behavior and never use Excel COM.",
    "scope_paths": [
      "backend/api/dependencies.py",
      "backend/api/main.py",
      "backend/api/routes_matrix_editor_ir_dwv_record_generation.py",
      "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
      "backend/application/external_resource_service.py",
      "backend/application/matrix_editor_ir_dwv_record_generation_service.py",
      "backend/application/matrix_editor_ir_dwv_record_projection.py",
      "backend/domain/enums.py",
      "backend/infrastructure/files/ir_dwv_record_artifact_store.py",
      "backend/infrastructure/files/project_folder_required_forms_gateway.py",
      "backend/infrastructure/office/ir_dwv_record_workbook_gateway.py",
      "backend/infrastructure/office/ir_dwv_record_workbook_layout.py",
      "docs/plans/IR_DWV_RECORD_WORKBOOK_GOLDEN_DIFF.md",
      "docs/plans/IR_DWV_RECORD_WORKBOOK_PLAN.md",
      "frontend/src/api/client.ts",
      "frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx",
      "frontend/src/features/matrix-editor/IrDwvRecordDownloadAction.test.tsx",
      "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
      "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
      "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts",
      "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx",
      "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx",
      "frontend/src/features/settings/settingsResourceConfig.ts",
      "scripts/inventory_ir_dwv_template.py",
      "tests/fixtures/ir_dwv/IR_DWV_Template.xlsx",
      "tests/fixtures/ir_dwv/template_inventory.json",
      "tests/integration/test_external_resource_api.py",
      "tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py",
      "tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py",
      "tests/unit/test_external_resource_service.py",
      "tests/unit/test_ir_dwv_record_projection.py",
      "tests/unit/test_ir_dwv_record_workbook_gateway.py"
    ],
    "risk_reasons": [
      "Back up and purify an authoritative external Excel template under D:\\Source\\Template.",
      "Publish generated workbooks into project Test results with conflict archival under the existing folder write slot."
    ],
    "activation_head": "29c0b9de3335d5c1e8beb0f3f2f559889ac572fd",
    "started_at": "2026-10-01T03:23:28.767007Z",
    "updated_at": "2026-10-02T02:11:02.474319Z",
    "checkpoint": {
      "schema": "connlab.sol-task-checkpoint",
      "version": 1,
      "task_id": "TASK_362_IR_DWV_RECORD_WORKBOOK_20261001",
      "stage": "delivery",
      "status": "running",
      "summary": "Implementation, review, validation, and integration are complete.",
      "requires_user": false
    },
    "report": {
      "schema": "connlab.sol-task-report",
      "version": 1,
      "task_id": "TASK_362_IR_DWV_RECORD_WORKBOOK_20261001",
      "subject": "01c49338f883ba0fe07b62a4e8e4bedb0775f6b2",
      "summary": "Complete IR/DWV records and fix sample-expanded third-round continuation: fixed three rounds per sheet N6B/Q/AF and N7B/S/AJ, two-column gutters, fourth-round continuation and max17 retained. Isolated LOGO metric preserves original Remarks budget. Actual requested browser download GREEN and independent final writer/API QA99passed. Native Excel/packaged release not run.",
      "scope_ok": true,
      "changed_paths": [
        "backend/api/dependencies.py",
        "backend/api/main.py",
        "backend/api/routes_matrix_editor_ir_dwv_record_generation.py",
        "backend/application/confirmed_matrix_llcr_cr_record_generation_service.py",
        "backend/application/external_resource_service.py",
        "backend/application/matrix_editor_ir_dwv_record_generation_service.py",
        "backend/application/matrix_editor_ir_dwv_record_projection.py",
        "backend/domain/enums.py",
        "backend/infrastructure/files/ir_dwv_record_artifact_store.py",
        "backend/infrastructure/files/project_folder_required_forms_gateway.py",
        "backend/infrastructure/office/ir_dwv_record_workbook_gateway.py",
        "backend/infrastructure/office/ir_dwv_record_workbook_layout.py",
        "docs/plans/IR_DWV_RECORD_WORKBOOK_GOLDEN_DIFF.md",
        "docs/plans/IR_DWV_RECORD_WORKBOOK_PLAN.md",
        "frontend/src/api/client.ts",
        "frontend/src/features/contact-measurement-plan/MatrixTestPointsEditor.tsx",
        "frontend/src/features/matrix-editor/IrDwvRecordDownloadAction.test.tsx",
        "frontend/src/features/matrix-editor/LlcrCrRecordDownloadAction.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.editing.test.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.testSupport.tsx",
        "frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx",
        "frontend/src/features/matrix-editor/useLlcrCrSpecializedRecordWorkbookModel.ts",
        "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.test.tsx",
        "frontend/src/features/project-workbench/ProjectWorkbenchCloseConfirmation.tsx",
        "frontend/src/features/settings/settingsResourceConfig.ts",
        "scripts/inventory_ir_dwv_template.py",
        "tests/fixtures/ir_dwv/IR_DWV_Template.xlsx",
        "tests/fixtures/ir_dwv/template_inventory.json",
        "tests/integration/test_external_resource_api.py",
        "tests/integration/test_matrix_editor_ir_dwv_record_generation_api.py",
        "tests/unit/test_confirmed_matrix_llcr_cr_record_generation_service.py",
        "tests/unit/test_external_resource_service.py",
        "tests/unit/test_ir_dwv_record_projection.py",
        "tests/unit/test_ir_dwv_record_workbook_gateway.py"
      ],
      "validation": [
        {
          "status": "passed",
          "name": "final affected writer unit and IR/DWV API after sample-width and isolated-logo correction",
          "result": "99 passed,1 existing deprecation warning,53.84s,exit0; once on frozen layoutdd207eb0/gateway4c546011/testsd68c9589; precise argv and raw hashes in GOLDEN_DIFF."
        },
        {
          "status": "passed",
          "name": "independent actual current-template artifacts and physical/layout preservation",
          "result": "N3/5/6/7 three rounds per sheet with two blank column gutters; fourth continuation retained;17 supported18prewriteblocked. Reviewer12LOGOs/96formulas/1512blankmeasurements/652gutters/4530normalizedcellsstyles; QA own source and prior isolatedformal/archive unchanged. LOGO8metric only dedicated callers; original Remarks7budget restored."
        },
        {
          "status": "passed",
          "name": "requested live project real browser smoke and final download",
          "result": "Actual localhost5173 project1fb... Matrix Editor click IR&DWV Form→Downloadpreview before565token RED; final613token onlyGroup2,Group6b. Group2 B/Q/AF three rounds,1599cellvaluesstyles/formulasnormalizedsameold,Remarks136.6same;Group6b original2rounds2logos92.4same. FinalSHA b07a0268745d5c918ab065b77a0487a59539037e90cd9d3444123374605aed44. Main viewed readonly finalAC10:AR23render; businessMatrix/template/officialfiles notwritten, originalUsertabpreserved ownedtabclosed."
        },
        {
          "status": "passed",
          "name": "unchanged UI and safe-publication regressions retained",
          "result": "No current frontend/API/publication implementation delta; earlier151affected+52sharedPython,234frontend37files with opt-in profiling skipped, subsequent72close-labeltests andTS/Vite157modulebuild, isolated8014/5174 draft/formal/archive/blockers evidence remain valid. Counts overlap, not summed; no new fullrepo/nativeExcel/packagedrelease claim."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "context": "ir_dwv_final_integrator served independent current revision Planner only: sample width must not reduce three-round capacity; N6B/Q/AF N7B/S/AJ, two gutters, fourth oldcontinuation/max17 preserved; exact approvedscope."
        },
        "developer": {
          "status": "passed",
          "context": "ir_dwv_revision_developer; public capacityRED2failedN6/7, LOGON6RED and laterRemarksboundaryRED1fail1pass; sharedmetricfinding corrected and frozen. Final targeted45passed45deselected27.99s; actualsource3/5/6/7outputs. Claims on intermediatefreeze withdrawn and finalbytes verified."
        },
        "reviewer": {
          "status": "passed",
          "context": "ir_dwv_p1_reviewer; final19passed71deselected11.84s Standards0/Spec0; sharedLOGO/Remarksfindingclosed; current12logos96formulas1512blank652gutters4530cellsstyles and sourceimmutability verified on finalhashes."
        },
        "qa": {
          "status": "passed",
          "context": "ir_dwv_p1_qa; final complete99writer/APItests once53.84s + actual3/5/6/7 and finalbusinessdownload compared per-group; source/priorformal/archive immutable. Preliminary overbroadGroup6bdiagnostic corrected, not productfailure or codechange; finalstagepassed."
        },
        "integrator": {
          "status": "passed",
          "context": "ir_dwv_sample_width_integrator fresh independent context; exactcleanmaster01c49338/parentbdb8d20e/previous99aaa814 and34approvednonboardpaths match; current six-file delta, frozen3hashes/source/download4outputs/priorformalarchive/log/DoD checked Standards0/Spec0. Readonly, no duplicate test/write/push."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "01c49338f883ba0fe07b62a4e8e4bedb0775f6b2",
        "code_subject": "01c49338f883ba0fe07b62a4e8e4bedb0775f6b2",
        "facts": "Legacyv1 directmaster integration clean; fresh independent Integrator verified exact approved34 and6fileacceptance delta, current frozen hashes, final browser artifact and QA99facts/DoD. No current taskclose/publication; nativeExcel/release/fullrepo limitations explicit."
      }
    }
  },
  "last_closed": {
    "task_id": "TASK_MATRIX_IR_DWV_TEST_POINTS_20260930",
    "tier": "standard",
    "subject": "af1ef613190c4bf6ddd277c0992a4d30c34db1f2",
    "summary": "Add confirmed Matrix IR/DWV points and Fee quantities",
    "disposition": "completed",
    "decision_ref": "User explicit final close on 2026-10-01 before IR/DWV workbook work order.",
    "closed_at": "2026-10-01T03:22:02.240815Z"
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
