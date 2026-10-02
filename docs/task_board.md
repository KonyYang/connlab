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
    "updated_at": "2026-10-02T00:32:11.252381Z",
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
      "subject": "43b1721163cfc852f5352523d88f4c8bf708b940",
      "summary": "Complete template-driven paired IR/DWV records, clean execution fields, preserved logo/device/template units, Matrix conditions and requirements, and safe draft/publication chain. Independent final affected QA81passed; unchanged frontend build and isolated browser flow verified. Native Excel/release not run; sample capacity17 and explicit Remarks overflow guard remain.",
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
          "name": "final affected writer unit and IR/DWV API",
          "result": "81 passed; existing deprecation warning;43.28s; final frozen gateway434ec584/test2936bd91"
        },
        {
          "status": "passed",
          "name": "independent actual current-template files",
          "result": "3/5/7 samples,9blocks,18requirements,90conditions,1224blankmeasurementcells,72statsformulas,9logos; source07cf and prior syntheticformal/archive unchanged"
        },
        {
          "status": "passed",
          "name": "unaffected frontend and shared regressions retained",
          "result": "Earlier151affected+52sharedPython;234frontend37files (opt-in profiling skipped); subsequent72affectedclose-labeltests+TypeScript/Vite157modulebuild exit0. Overlapping counts not summed."
        },
        {
          "status": "passed",
          "name": "isolated real browser flow and actual artifacts",
          "result": "Owned8014/5174 draft download, formal publication, cancel, archive, missingpoints/lockedtemplate blockers. Later backend-only deltas covered by affectedtests and actualfiles; final Remarks not rerun browser. Userbusinessfiles/tab preserved; ownedservices stopped."
        }
      ],
      "roles": {
        "planner": {
          "status": "passed",
          "context": "Independent Planner (earlier task context) assessed golden-source authority, paired rounds/sequence boundaries, min5 template slots/defaults/logo and units choice; User latest settled units."
        },
        "developer": {
          "status": "passed",
          "context": "ir_dwv_revision_developer; substantive RED/GREEN evidence; final Remarks7RED failures then7GREEN and31focused checks; freeze recorded."
        },
        "reviewer": {
          "status": "passed",
          "context": "ir_dwv_p1_reviewer; fullchain findings resolved then final10riskfocused passed; Standards0Spec0; independently inspected9actualblocks and staged-publication fail safety."
        },
        "qa": {
          "status": "passed",
          "context": "ir_dwv_p1_qa; final81affected tests+read-onlyactualfiles, immutable hashes; retained valid unchanged browser/frontend/build evidence."
        },
        "integrator": {
          "status": "passed",
          "context": "ir_dwv_final_integrator independently verified cleanmaster43b17211 parentcode51c12a33; board-onlylastdiff/producttree unchanged, activationancestor,34exactapprovedpaths/0drift,frozenhashes/source07cf, actualartifactSHA/size+QAevidence and API/UI wiring. No fullmatrixrepeat, no writes."
        }
      },
      "integration": {
        "status": "passed",
        "subject": "43b1721163cfc852f5352523d88f4c8bf708b940",
        "code_subject": "51c12a332ffbdc1b76f24157a2d052394fe4f075",
        "facts": "Legacy v1 direct master integration clean. Independent Integrator confirmed exact34nonboardpaths, approvedscope amendment, all task commits in ancestry, exactfrozenbytes and zero actionable integration findings; no taskclose/push."
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
