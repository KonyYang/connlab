# TASK_321_PROJECT_FOLDER_REQUIRED_FORMS_GENERATION

Status: Complete after explicit user approval.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: TASK_321 was implemented after explicit user approval, following TASK_316-TASK_320 Project Folder model completion.

Executable plan:

- `docs/task_321_project_folder_required_forms_generation_plan.md`

## Decision On TASK_313

Old `TASK_313_PROJECT_PACKAGE_ORCHESTRATOR_EXECUTE` is retained as historical reference but must not be implemented in its current form.

Reasons:

- It exposes `Package` / `Execute package` as the operator concept, which conflicts with the completed Project Folder direction.
- It assumes all generated artifacts are placed under `Submitted Material`.
- It depends on old `project-package/preview` semantics instead of the official Project Folder checks introduced by TASK_316-TASK_320.
- It would reintroduce a broad Package panel instead of using the TASK_320 `Required forms` task detail.

TASK_321 replaces the executable intent of old TASK_313 with an operator-facing Project Folder task:

```text
Generate required forms
```

## Goal

Add a preview-first Project Folder action that generates and places required form files into the local Official project folder, then records their output status so the TASK_320 `Required forms` row can become current.

V1 required forms:

- Test Record
- Fee Form
- Customer Feedback Form

## User-Facing Model

The operator sees this as Project Folder preparation, not package execution.

Visible wording:

- `Required forms`
- `Generate required forms`
- `Test Record`
- `Fee Form`
- `Customer Feedback Form`
- `Official project folder`
- `Submitted Material`

Forbidden user-facing wording in the new flow:

- `Package`
- `Execute package`
- `Project package`
- `.connlab`
- `manifest`
- `SQLite`
- backend route names

Internal code may still use existing historical names where required for compatibility, but the new API/UI contract must use Project Folder / Required forms wording.

## Business Placement Rules

The formal local folder structure is:

```text
{DL_NUMBER}/
  Source Book/
  {DL_NUMBER} {Sample Description} {Test Item}/
    E-mail/
    Submitted Material/
    Photos/
    Test results/
      Final Examination/
    Customer Feedback Form.xlsx
    Fee Form.xls or Fee Form.xlsx
    Test Report *.docx
```

TASK_321 V1 placement:

- `Test Record` goes under `Official project folder/Submitted Material/`.
- `Fee Form` goes under `Official project folder/`.
- `Customer Feedback Form` goes under `Official project folder/`.

Do not place all files into `Submitted Material`.

## Inputs

Backend inputs:

- Project id.
- Completed TASK_316 official workspace record / manifest / file-system path check.
- TASK_318 Official project folder check.
- Active Confirmed Matrix authority.
- Latest current Confirmed Fee authority.
- Customer Feedback template discovery from the existing Customer Feedback generation service.
- Existing generated-output status records.

Frontend inputs:

- Existing Workbench model state.
- TASK_320 `ProjectFolderTaskList`.
- Required forms task row state.

## Outputs

Preview API returns:

- project id
- status: `blocked` | `ready` | `current` | `conflict`
- Official project folder path
- one item for each required form:
  - key
  - label
  - target path
  - status
  - action: `generate` | `update` | `skip` | `conflict` | `blocked`
  - message
- blockers
- warnings

Generate API returns:

- project id
- Official project folder path
- generated items with final paths
- skipped current items
- warnings

Persisted output status:

- `test_record_form`
- `fee_evaluation`
- new `customer_feedback_form`

TASK_321 must also persist enough managed-output metadata to decide whether an existing target file is safe to update:

- final output path,
- source context signature,
- final file fingerprint, at minimum SHA-256 and size,
- generated output kind,
- generated timestamp.

This may be stored by extending `ProjectOutputRecord` or by adding a task-owned required-forms managed-output table/read model. The selected design must expose a single service-level contract to preview/generate; the frontend must not know the storage detail.

## Required Backend Contract

Add Project Folder Required Forms routes:

```text
GET  /api/projects/{project_id}/project-folder/required-forms/preview
POST /api/projects/{project_id}/project-folder/required-forms/generate
```

Do not add `/project-package/execute`.

The POST request must include the preview context the operator saw:

- `expected_official_project_folder_path`
- `expected_confirmed_matrix_id`
- `expected_confirmed_revision`
- `expected_confirmed_fee_id`
- `expected_confirmed_fee_revision`
- `expected_confirmed_fee_pricing_draft_edit_id`
- `expected_customer_feedback_template_path`
- expected target paths for the three required forms

The backend must re-read current state and reject stale context with `409` before generating or copying files.

## Generation And Placement Rules

- Re-run preview server-side before writing.
- Generate files into ConnLab-controlled staging first.
- Staging generation must not register project output records or mark any output current.
- If existing generation services currently register output records as a side effect, TASK_321 must introduce staging-only generator ports/adapters and use those ports instead.
- Resolve final target paths under the Official project folder only.
- Use deterministic business-readable final names.
- If a final target does not exist, create it with no-overwrite semantics.
- If a final target exists and matches the last ConnLab-managed output record for the same output kind, same path, same source context, and unchanged disk fingerprint, TASK_321 may safely update it using a same-directory temporary file plus final replace after rechecking the fingerprint.
- If a final target exists and matches the last ConnLab-managed output record for the same output kind and same path, but the current source context has changed, TASK_321 may perform a controlled refresh only when the disk fingerprint still matches the stored ConnLab-managed fingerprint. The refresh must recheck the fingerprint immediately before final replace, then write a new output record with the new source context and fingerprint.
- If a final target exists but is unmanaged, has no matching output record, or its disk fingerprint differs from the last ConnLab-managed fingerprint, return conflict and do not overwrite.
- Never silently overwrite files.
- Never delete user files.
- If final placement partially succeeds and then fails, return copied/skipped/conflict/error status and persist enough information for the next preview to explain the state.
- Register output records only after final target placement succeeds.
- Failed attempts may register `failed` output status only if it helps Workbench explain the failure; they must not mark Required forms ready.

## Suggested Final File Names

Use the project identity prefix from the registered DL/LTR number:

```text
{DL_NUMBER}_Test_Record.docx
{DL_NUMBER}_Fee_Form.xls
{DL_NUMBER}_Customer_Feedback_Form.xlsx
```

If extension compatibility requires `.xlsx` for Fee Form, the plan must explicitly document why and keep the target label `Fee Form`.

No numeric suffixing in the Official project folder. Existing conflicting targets block.

## Required Frontend Contract

TASK_321 updates the TASK_320 `Required forms` task detail.

Allowed UI changes:

- Add Required forms preview loading/error state to Workbench model.
- Add `Generate required forms` row/detail action only when preview is ready.
- Show the three target paths and per-file status inside the selected Required forms detail.
- After generation, refresh:
  - Required forms preview
  - output status summary
  - Official folder check
  - Public drive upload preview if already loaded

Forbidden UI changes:

- Do not restore `ProjectPackagePreviewPanel` as a visible Workbench surface.
- Do not show `Execute package`.
- Do not add a generic tools panel.
- Do not add public-drive upload actions beyond existing TASK_319 controls.
- Do not expose Office/template internals.

## In Scope

- Backend Project Folder Required Forms preview service.
- Backend Project Folder Required Forms generation service.
- Thin FastAPI routes and dependency wiring.
- Safe filesystem placement gateway.
- New or extended output status support for Customer Feedback Form.
- Managed-output fingerprint support for safe regeneration/update of ConnLab-generated Required forms.
- TASK_318 Official project folder check update so Customer Feedback Form is no longer permanently deferred after TASK_321 creates a current project-local output.
- Frontend typed API client functions.
- Workbench Required forms task detail integration.
- Unit/integration/frontend/static tests.
- Task board update after implementation.

## Out Of Scope

- No old TASK_313 `/project-package/execute`.
- No public-drive upload/update behavior changes.
- No Application Form Section 2 write-back.
- No Test Report generation.
- No execution evidence/photos automation.
- No StepInstance, TestResult, report execution, AI review, permissions, LAN, or multi-user scope.
- No automatic generation from Confirm Matrix, Confirm Fee, folder creation, request material collection, or public-drive upload.
- No overwrite/merge/conflict-resolution UI.

## Acceptance Criteria

- Old TASK_313 remains deferred/historical and no `/project-package/execute` endpoint exists.
- Workbench Required forms detail shows preview-first status for Test Record, Fee Form, and Customer Feedback Form.
- `Generate required forms` is available only when:
  - local Official project folder is completed and matches real file-system state,
  - active Confirmed Matrix exists,
  - latest Confirmed Fee authority is current,
  - target paths are inside the Official project folder,
  - no final target conflict exists.
- Test Record final path is under `Submitted Material`.
- Fee Form final path is under Official project folder root.
- Customer Feedback Form final path is under Official project folder root.
- POST rejects stale preview context with `409` and does not write final files.
- Existing unmanaged, manually edited, or fingerprint-changed target files block before overwrite.
- Existing ConnLab-managed target files may be safely updated or refreshed only when the stored fingerprint still matches the current disk file; changed Matrix/Fee/template source context is allowed only through this controlled refresh path.
- Successful generation records current output status for all three required forms.
- Required forms row becomes ready/current after successful generation and refresh.
- Customer Feedback Form has its own output kind/status, not `approval_package`.
- TASK_318 Official project folder check reads `customer_feedback_form` output status and target file existence so Customer Feedback Form becomes ready after successful TASK_321 generation.
- Staging-only generation does not register output records; TASK_321 is the only service that marks Required forms outputs current after final placement succeeds.
- User-facing UI does not contain `Package`, `Execute package`, `TASK_313`, `.connlab`, `manifest`, or `SQLite` in the Required forms flow.

## Validation Plan

After implementation approval, run:

```powershell
py -m pytest tests/unit/test_project_folder_required_forms_service.py -q
py -m pytest tests/integration/test_project_folder_required_forms_api.py -q
py -m pytest tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_request_material_collection_service.py -q
```

```powershell
cd frontend
npm test -- --run ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --watch=false
npm run build
```

```powershell
py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task321 or project_workbench or required_forms"
git diff --check
```

Browser smoke after implementation approval:

- Open a DL project with active Confirmed Matrix and completed local Official project folder.
- Select `Project Folder`.
- Select `Required forms`.
- Confirm preview shows Test Record, Fee Form, and Customer Feedback Form target paths.
- Confirm no horizontal overflow at 740px width.
- Confirm `Generate required forms` is hidden or disabled when blockers exist.
- Confirm successful generation refreshes Required forms state.
- Confirm no `Package` / `Execute package` wording appears.

## Stop Point

## Completion Notes

TASK_321 is implemented. Old TASK_313 remains historical/deferred and must not be implemented as its old Package / Execute package shape.

Implemented:

- Project Folder Required forms preview and generate API.
- Safe managed-file refresh/update checks using final output fingerprint and source context metadata.
- Staging-only generator adapters so final output records are written only after successful final placement.
- Customer Feedback Form output kind and Official folder check integration.
- Workbench Project Folder `Required forms` task preview/detail/action wiring.
- Review follow-up corrections for mixed skip/generate requests, real-file existence checks across all Required forms, and first-placement failure status.

Validation:

- `py -m pytest tests/unit/test_project_folder_required_forms_service.py tests/unit/test_official_project_folder_check_service.py tests/unit/test_project_request_material_collection_service.py -q`
- `py -m pytest tests/integration/test_project_folder_required_forms_api.py -q`
- `cd frontend; npm test -- --run projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout projectWorkbenchLifecycleSelectors --watch=false`
- `py -m pytest tests/unit/test_frontend_shell_files.py -q -k "task321 or task320 or task318"`
- `cd frontend; npm run build`
