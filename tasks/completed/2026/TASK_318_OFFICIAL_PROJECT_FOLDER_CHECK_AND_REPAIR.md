# TASK_318_OFFICIAL_PROJECT_FOLDER_CHECK_AND_REPAIR

Status: Complete. Implemented on 2026-06-13.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Completion status: TASK_318 is implemented and verified. `TASK_317C_TEMPORARY_PROJECT_PLANNING_IDENTITY` remains a separate proposed interleaved task for review; TASK_318 does not consume or rename it.

Allowed reason: the user explicitly approved TASK_318 implementation after review corrections. `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION` is complete with review corrections. This task replaces TASK_312's user-facing readiness/check role inside the new `Project Folder` model instead of extending the old package-preview surface.

Executable plan:

- `docs/task_318_official_project_folder_check_and_repair_plan.md`

## Goal

Add a read-only first, repair-capable check for the local Official project folder so the Workbench can answer:

```text
Is the local project folder structurally complete, are required request/output files in the expected locations, and what is the one next repair action?
```

This task turns the `Submitted Material` and required folder rows from TASK_317's future placeholder into a controlled Project Folder readiness check.

## Product Language

Use user-facing language:

- Project Folder
- Local project folder
- Official project folder
- Source Book
- Request material
- Submitted Material
- Required folders
- Required files
- Check project folder
- Repair folder structure

Do not use user-facing language:

- Package readiness
- Package preview
- Package details
- Workspace details
- `.connlab`
- manifest
- SQLite
- task ids
- API route names

## Business Folder Contract

The local DL folder is:

```text
{Project default save location}\{DL_NUMBER}
```

It contains:

```text
Source Book\
{DL_NUMBER} {Sample Description} {Test Item}\
```

The Official project folder must contain at least:

```text
E-mail\
Submitted Material\
Photos\
Test results\
Test results\Final Examination\
```

Required file checks for this task:

- request email under Official project folder `E-mail`
- selected Application Form / request attachments collected by TASK_317 under `Submitted Material`
- Test Record presence only through `ProjectOutputRecordService.get_status_summary()` mapping for `TEST_RECORD_FORM`
- Fee Form presence only through `ProjectOutputRecordService.get_status_summary()` mapping for `FEE_EVALUATION`
- Section 2 status only through `ProjectOutputRecordService.get_status_summary()` mapping for `SECTION2_WRITE_BACK` or the existing Section 2 preview read model
- Customer Feedback is deferred in TASK_318 unless a current approved service provides a concrete project-local target file path or explicit output record
- Section 2 sync state as a status row only, using existing preview state; no write-back in TASK_318

## Scope

TASK_318 must implement:

1. A backend read-only project folder check service.
2. A backend repair operation for missing folders only.
3. A project-scoped API:
   - `GET /api/projects/{project_id}/official-folder/check`
   - `POST /api/projects/{project_id}/official-folder/repair-folders`
4. Frontend API client types and functions.
5. Workbench Project Folder row integration.
6. One primary action only:
   - `Repair folder structure` when required folders are missing.
   - `Refresh folder check` only when the frontend check/repair request fails and the user needs a retry action.
   - No generated-file actions in this task.

## Out Of Scope

- No public-drive upload or sync.
- No automatic generation of Test Record.
- No automatic generation of Fee Form.
- No Customer Feedback Form generation.
- No Application Form Section 2 write-back.
- No repair of conflicting files by overwrite.
- No moving files out of Source Book.
- No deleting files.
- No AI classification.
- No execution evidence, sample photos, final examination photo import, StepInstance, TestResult, report generation, AI review, permissions, LAN, or multi-user work.
- No enhancement of `/api/projects/{project_id}/project-package/preview` as the main product path.
- No second `Package readiness` panel beside the Project Folder rows.

## Inputs

- project id
- completed TASK_316 official workspace record
- TASK_317 request-material preview/collection state
- real file system under the local DL folder
- active Confirmed Matrix state, where already exposed
- Confirmed Fee status, where already exposed
- Section 2 sync preview state, where already exposed
- `ProjectOutputRecordService.get_status_summary()` for existing mappable output kinds:
  - `TEST_RECORD_FORM`
  - `FEE_EVALUATION`
  - `SECTION2_WRITE_BACK`
- no `ProjectPackagePreviewService` or `/project-package/preview` output source as the TASK_318 read model

## Outputs

- project folder check response
- required folder statuses
- required file statuses
- blockers
- warnings
- next repair action
- repair result for missing required folders
- Workbench `Project Folder` row state

## Backend Contract

### Status Vocabulary

Project folder check status:

- `blocked`: no completed local project folder / official workspace record
- `missing`: required folders or files are missing
- `warning`: optional or future-scope items need attention
- `ready`: required folder structure and currently checkable files are present
- `conflict`: expected path exists but is not the expected file/folder type

Check item status:

- `ready`
- `missing`
- `conflict`
- `warning`
- `not_applicable`
- `deferred`

Repair action:

- `repair_folders`
- `none`

`Refresh folder check` is a frontend retry action for request/fetch failure only. It is not a backend check status and must not be mixed into the backend status vocabulary.

### Required Folders

The service must check:

- Official project folder root
- `E-mail`
- `Submitted Material`
- `Photos`
- `Test results`
- `Test results/Final Examination`

If a required path exists with the wrong type, report `conflict` and do not repair.

If a required folder is missing, report `missing` and allow `repair_folders`.

### Required Files

TASK_318 must not invent generated files. It may only check for files that are already known from current state:

- request email and request material targets from TASK_317 response/records
- existing Test Record output status from `ProjectOutputRecordService.get_status_summary()` and `TEST_RECORD_FORM`
- existing Fee Form output status from `ProjectOutputRecordService.get_status_summary()` and `FEE_EVALUATION`
- existing Section 2 status from `ProjectOutputRecordService.get_status_summary()` and `SECTION2_WRITE_BACK`, or the existing Section 2 preview read model
- Customer Feedback only when a current approved service exposes a concrete project-local target file path or explicit output record

If a generated file is not yet produced by an approved task path, report it as `deferred` or `not_applicable`, not `missing`.

Customer Feedback template availability is not readiness. A configured or discovered template only means a future task may generate the file. It must not make the Project Folder row ready in TASK_318.

Do not read `ProjectPackagePreviewService` or `/api/projects/{project_id}/project-package/preview` to decide these rows.

### Repair Rules

Repair is limited to missing folders:

- create missing required folders under the completed Official project folder
- do not overwrite files
- do not replace a path that exists as a file
- do not copy request material
- do not generate forms
- do not edit Word or Excel files
- return created paths and unresolved conflicts

Partial repair failure must be explainable:

- if some folders are created and a later folder fails due to permission, lock, path length, or wrong type, the service must rerun preview
- the repair response must include the already created paths, unresolved conflicts or errors, and the refreshed preview
- the user must not be left with a generic exception that hides partial completion
- add a unit test for "some folders created, later folder creation fails"

## Frontend Contract

Project Folder should show rows similar to:

```text
Local project folder        Created / Needs repair / Missing
Request material            Missing / Partial / Review required / Collected / Conflict
Folder structure            Ready / Missing folders / Conflict
Submitted Material          Ready / Missing files / Needs review / Deferred
Confirmed Fee authority     Missing / Confirmed / Stale
Required forms              Deferred / Ready when generated / Missing existing file
Application Form Section 2  Not updated / Preview later / Synced
Public drive upload         Hidden or read-only future state
```

User-facing top action rules:

- If no local project folder exists, keep TASK_316 action.
- If request material is the next blocker, keep TASK_317 action.
- If folder structure is missing, show `Repair folder structure`.
- If the frontend folder-check request fails, show `Refresh folder check`.
- Backend warning or conflict statuses must use their normal blocker/action rules; they are not refresh states.
- If only future generated files are deferred, do not show a repair/generate button in TASK_318.
- If conflicts exist, show a blocker message and no destructive action.

Request material and Submitted Material are separate signals:

- `review_required` means `Needs review`; it is not a missing-file state and must not keep prompting `Collect request material`
- `partial` may only mean there are still copyable request-material targets; if only manual review remains, use `review_required`
- Submitted Material is ready only when the confirmed collected targets are present under the Official project folder's `Submitted Material`
- Source Book-only or review-only candidates do not make Submitted Material ready and must not be counted as missing submitted files

## Acceptance Criteria

- Check blocks when no completed local official workspace record exists.
- Check reports missing required folders.
- Check reports wrong-type path conflicts.
- Check reports required folder structure ready when all required folders exist.
- Repair creates only missing required folders.
- Repair does not overwrite files or delete anything.
- Repair refuses conflict paths.
- Check integrates TASK_317 request material state without re-copying request material.
- Check keeps Request material and Submitted Material as separate rows/signals.
- Check does not mark future generated files as missing unless an existing output record/file is already expected.
- Check uses `ProjectOutputRecordService.get_status_summary()` for current mappable output rows and does not use old package preview as its read model.
- Customer Feedback stays deferred unless a current approved service provides a concrete project-local target or output record.
- Repair returns partial completion details if folder creation partially succeeds before failing.
- Workbench uses `Project Folder` language, not `Package`.
- Workbench exposes one current action only.
- Public-drive upload remains hidden or read-only.
- No Office write-back or generated document creation occurs in TASK_318.
- No old package preview route is used as the main UI/API contract.

## Validation Required During Implementation

Backend:

```powershell
py -m pytest tests\unit\test_official_project_folder_check_service.py -q
py -m pytest tests\integration\test_official_project_folder_check_api.py -q
```

Frontend:

```powershell
cd frontend; npm test -- --run ProjectWorkbench officialFolder --watch=false
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or official_folder or task318"
cd frontend; npm run build
```

General:

```powershell
git diff --check
```

Browser smoke after implementation approval:

1. Open an active-Matrix project with a completed local project folder.
2. Confirm the Project Folder surface shows `Folder structure`.
3. Remove or simulate a missing required folder in a test fixture.
4. Confirm the next action is `Repair folder structure`.
5. Execute repair.
6. Confirm missing folders are created.
7. Confirm conflicts do not show destructive repair.
8. Confirm no public-drive upload action is enabled.

## Completion Notes

Implemented:

- backend Official project folder check service
- missing-folder-only repair gateway and partial failure result
- `GET /api/projects/{project_id}/official-folder/check`
- `POST /api/projects/{project_id}/official-folder/repair-folders`
- frontend typed API client functions
- Workbench Project Folder lifecycle action integration
- `Folder structure` and `Submitted Material` rows backed by TASK_318 check state
- static guard preventing TASK_318 service from using old package preview

Validation completed:

```powershell
py -m pytest tests\unit\test_official_project_folder_check_service.py tests\integration\test_official_project_folder_check_api.py -q
py -m pytest tests\unit\test_project_request_material_collection_service.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or official_folder or task318"
cd frontend; npm test -- --run ProjectWorkbench officialFolder --watch=false
cd frontend; npm run build
git diff --check
```

Browser smoke note: in-app Browser attach timed out during this implementation turn, so visual smoke remains a manual follow-up item.
