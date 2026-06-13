# TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION

Status: Implemented. TASK_317 scope is complete.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: `TASK_317_SOURCE_BOOK_AND_REQUEST_MATERIAL_COLLECTION`, implementation complete.

Allowed reason: `TASK_317A_PROJECT_FOLDER_PREPARATION_UI_BLUEPRINT` is accepted as the UI/information-architecture prerequisite. TASK_317 is the next controlled task after TASK_316 local project workspace creation, and the user explicitly approved implementation.

Executable plan:

- `docs/task_317_source_book_and_request_material_collection_plan.md`

## Goal

Add the first Project Folder preparation slice after local project folder creation:

1. preview request material already registered on the project,
2. collect the original request email and attachments into `Source Book`,
3. place controlled copies of the request email and attachments into the Official project folder,
4. show the `Request material` row inside the minimum `Project Folder` Workbench frame.

The user-facing primary action is:

```text
Collect request material
```

## User Story

As a lab operator, I want ConnLab to copy the imported request email and its attachments into the local project folder structure, so the project has a preserved original source archive in `Source Book` and controlled working copies in the Official project folder without me manually searching the intake cache.

## Business Folder Contract

TASK_317 follows the folder hierarchy defined by TASK_317A:

```text
Project Folder (Workbench tab and preparation flow)
  Local DL folder = {Project default save location}\{DL_NUMBER}
    Source Book
      Request Material
        E-mail
        Application Form
        Attachments
    Official project folder = {DL_NUMBER} {Sample Description} {Test Item}
      E-mail
      Submitted Material
      Photos
      Test results
        Final Examination
```

Rules:

- `Source Book` stores original request material and raw reference material for local traceability.
- The Official project folder stores controlled copies for the formal project file set.
- The request email copy belongs under the Official project folder `E-mail`.
- The selected Application Form and confirmed request attachments belong under the Official project folder `Submitted Material`.
- Attachment candidates whose source role is unknown or ambiguous may be preserved in `Source Book`, but must not be silently placed in `Submitted Material`.
- TASK_317 copies files only. It must not move or delete original files from intake storage, user-selected locations, or any existing project folder.
- If the source email is not available from current project `FileAsset` records, TASK_317 may allow partial collection of the selected Application Form and confirmed attachments, but the UI and response must explicitly show `Request email missing`.
- If multiple different request email candidates exist, TASK_317 must block collection and ask for review. It must not copy multiple `.msg` files as request email.

## Input Sources

TASK_317 uses existing persisted project records:

- `Project`
- latest registered LTR / DL identity, through the same authority used by TASK_316
- completed `ProjectOfficialWorkspaceRecord`
- project `FileAsset` records created by Intake confirmation
- real file-system state for source files and target folders

Expected current `FileAsset` behavior:

- `FileAssetType.APPLICATION_FORM` points to the selected application form source.
- `FileAssetType.ATTACHMENT` may include the imported `.msg` request package and all other extracted request attachments.
- Current historical `FileAsset` rows do not reliably preserve the original intake `asset_role`.

TASK_317 must therefore define a source-role contract:

- New project confirmations should preserve project file provenance when creating `FileAsset` records or request-material source candidates. Minimum useful fields are source package id, source intake asset id where available, source role, and source hash where available.
- Preview must deduplicate source candidates by canonical path before classifying them; file hash is used for same-content checks and conflict diagnostics, not as a second state authority.
- When duplicate rows point to the same file, the preview must show one source candidate and merge/choose the highest-confidence source role.
- When multiple different `.msg` candidates remain after dedupe, preview status is `blocked` with a business-readable `Multiple request email candidates need review` blocker.
- When exactly one request email candidate remains, it is the request email.
- When no request email candidate exists, preview status may be `partial`; collect may still copy the selected Application Form and confirmed request attachments while marking the request email item as skipped/missing.
- Attachments with known request-attachment roles may be copied to `Submitted Material`.
- Attachments with unknown, ignored, inline-image, or ambiguous roles must be marked `needs_review` and must not be copied to `Submitted Material` in TASK_317.

## Output Targets

For each eligible source asset, TASK_317 should create a preview item and, when collection is executed, copy to one or more targets:

| Source asset | Source Book target | Official project folder target |
| --- | --- | --- |
| Imported request email / `.msg` | `Source Book/Request Material/E-mail/{safe original name}` | `Official project folder/E-mail/{safe original name}` |
| Selected Application Form | `Source Book/Request Material/Application Form/{safe original name}` | `Official project folder/Submitted Material/{safe original name}` |
| Confirmed request attachments | `Source Book/Request Material/Attachments/{safe original name}` | `Official project folder/Submitted Material/{safe original name}` |
| Needs-review attachment candidates | `Source Book/Request Material/Attachments/{safe original name}` | skipped until a later review/repair task approves placement |

Filename rules:

- Preserve the business-readable original file name when safe.
- Replace Windows-invalid filename characters.
- Normalize whitespace.
- If two source assets would produce the same target name, append a stable short source identifier before the extension.
- If a target file exists with the same size and hash as the planned source copy, mark it as already collected.
- If a target file exists with different content, block execution with a conflict.

## API Contract

Add request-material endpoints under a project-scoped route:

```text
GET  /api/projects/{project_id}/request-material/preview
POST /api/projects/{project_id}/request-material/collect
```

Preview response must include:

- project id
- local DL folder path
- Source Book path
- official project folder path
- status: `blocked`, `ready`, `collected`, `review_required`, `partial`, or `conflict`
- item list with source asset id, source name, source path, target area, target path, action, and status
- blockers
- warnings

Collect response must include:

- project id
- collection id or operation id
- status after execution
- copied paths
- already-collected paths
- skipped paths
- missing source paths
- conflict paths or conflict items
- blockers
- warnings

The collect endpoint must rerun preview before copying. It may copy only when preview has no blocking conflict. It must never overwrite a different existing target file.

## Persistence Contract

TASK_317 should add a lightweight SQLite index for request-material collection state so later tasks can inspect what was collected without treating the file system as the only UI source.

Recommended records:

```text
ProjectRequestMaterialCollectionRecord
  collection_id
  project_id
  official_workspace_id
  status
  item_count
  copied_count
  already_present_count
  conflict_count
  skipped_count
  missing_source_count
  created_at
  updated_at
  warnings_json

ProjectRequestMaterialCollectionItemRecord
  item_id
  collection_id
  project_id
  source_asset_id
  source_asset_type
  source_role
  dedupe_key
  source_path
  original_name
  target_area
  target_path
  status
  action
  review_required
  size_bytes
  sha256
```

Rules:

- SQLite is the ConnLab application index.
- The real file system remains the final existence check.
- If SQLite says an item is collected but the target file is missing, preview must report stale or partial state.
- Source-role/provenance stored for TASK_317 is for safe request-material collection only. It must not become a new email import authority.
- `.connlab/manifest.json` should not become the primary state source in TASK_317. Updating it is deferred unless implementation finds a small, compatible append-only manifest section is necessary and reviewed.

## File Operation Safety

TASK_317 must use preview-first file operations.

Rules:

- Copy only from existing source paths.
- Do not delete, move, or rename source files.
- Do not overwrite target files.
- Stage copies in a ConnLab-owned temporary directory under `{Local DL folder}/.connlab/tmp/`.
- Move staged files to final target paths only after preflight detects no conflicts.
- If staging fails, clean only the temporary directory created by this operation.
- If final placement partially succeeds and then fails, return explicit copied/conflict state. Do not hide partial results.
- Use real file-system checks in preview and collect.

## Workbench UI Contract

TASK_317 must start from the TASK_317A minimum `Project Folder` frame before showing request-material controls.

For projects with a DL number, an active Confirmed Matrix, and a completed local project folder, Workbench should show:

```text
Tabs:
  Project Folder | Execution

Project Folder:
  Current task: Request material
  Reason: Request email and attachments have not been collected into the local project folder.
  Primary action: Collect request material
  Task rows:
    Local project folder
    Request material
    Confirmed Fee authority
    Required forms
    Application Form Section 2
    Submitted Material
```

UI rules:

- User-facing active tab label is `Project Folder`, not `Package`.
- Do not show an `Overview` tab for the active-Matrix Project Folder flow in TASK_317.
- Do not show a row of unrelated secondary buttons.
- Request-material actions must appear only in the `Request material` row or the single top action.
- Public-drive upload is hidden or read-only. No enabled upload/update button is allowed in TASK_317.
- Execution remains the only place for Matrix execution map and Step workspace.
- Copy must use business language: `Request material`, `Source Book`, `Official project folder`, `Submitted Material`, and `E-mail`.
- Do not expose `.connlab`, manifest, SQLite, API routes, or task ids in operator copy.

## In Scope

- Backend preview and collect application service for project request material.
- Deterministic source asset classification from project `FileAsset` records.
- Source candidate dedupe and provenance/source-role preservation needed for safe classification.
- Safe target planning for Source Book and Official project folder copies.
- SQLite collection/index records if needed for traceability.
- Thin FastAPI routes and typed Pydantic responses.
- Frontend API client types and functions.
- Minimal Project Folder Workbench frame required by TASK_317A.
- `Request material` row and one primary action.
- Pytest, integration API tests, Vitest/static frontend tests.
- Task board and plan index updates after implementation is approved and completed.

## Out Of Scope

- No new Outlook live connection.
- No new email import workflow.
- No direct drag/drop upload into an existing project.
- No public-drive upload or sync.
- No Test Record generation.
- No Fee form generation.
- No Customer Feedback form generation.
- No Application Form Section 2 write-back.
- No Submitted Material full repair/check workflow beyond request-material copy targets.
- No execution evidence, sample photos, final examination photos, StepInstance, TestResult, report generation, AI review, permissions, LAN, or multi-user scope.
- No destructive move/delete behavior.
- No automatic collection from Confirm Matrix, Confirm Fee, Matrix Editor, or folder creation.

## Acceptance Criteria

- Preview blocks when no completed local project folder / official workspace record exists.
- Preview deduplicates duplicate project FileAsset rows by canonical path before classification and uses hash only for same-content/conflict checks.
- Preview blocks when multiple different request email candidates remain after dedupe.
- Preview lists available request email, selected Application Form, confirmed request attachments, and needs-review attachment candidates from existing project `FileAsset` records.
- Preview marks unknown or ambiguous attachment candidates as `needs_review` and does not plan `Submitted Material` placement for them.
- Preview reports `review_required` when all copyable request material has been collected and only manual attachment review remains.
- Preview reports missing source files as blockers or partial warnings with business-readable messages.
- Preview may report missing request email as partial rather than fully blocked, but the response and UI must explicitly show `Request email missing`.
- Preview reports existing same-content target files as already collected.
- Preview reports existing different-content target files as conflicts.
- Collect copies request email to `Source Book/Request Material/E-mail` and Official project folder `E-mail`.
- Collect copies selected Application Form and confirmed request attachments to `Source Book/Request Material/...` and Official project folder `Submitted Material`.
- Collect may preserve needs-review attachment candidates in `Source Book` only, but must mark their `Submitted Material` placement as skipped.
- Collect never deletes source files and never overwrites different target files.
- Collect response includes blockers, warnings, skipped paths, missing source paths, and conflict paths/items consistently.
- Collect records enough state for later preview to show `collected`, `review_required`, `partial`, or `conflict` accurately.
- Workbench active Matrix flow uses `Project Folder | Execution`, not `Overview | Package | Execution`.
- Workbench exposes one primary `Collect request material` action only when copyable request material remains.
- Workbench shows review-only request material as manual review and does not loop back to `Collect request material`.
- Workbench does not expose public-drive upload as an enabled action.
- UI and API responses contain no user-facing task ids, `.connlab`, manifest, SQLite, or raw route names.

## Validation

Completed implementation validation:

```powershell
py -m pytest tests\unit\test_intake_confirmation_service.py tests\unit\test_project_request_material_collection_service.py tests\unit\test_project_request_material_collection_repository.py tests\integration\test_project_request_material_collection_api.py -q
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or request_material or task317 or task313a or task316"
cd frontend; npm test -- --run ProjectWorkbench --watch=false
cd frontend; npm run build
```

Browser smoke after implementation approval:

1. Open an active-Matrix project with a completed local project folder.
2. Confirm the Workbench tabs read `Project Folder | Execution`.
3. Confirm the top action is `Collect request material` when request material is missing.
4. Execute collection on a fixture-backed project.
5. Confirm files appear under Source Book and Official project folder targets.
6. Refresh and confirm the request-material row shows collected or partial state.
7. Confirm no public-drive upload button is enabled.

## Model Fit Assessment

`GPT-5.3-codex` is suitable for this task because it requires disciplined cross-layer planning, safe file-operation boundaries, and frontend information-architecture control. The main risk is scope creep into public-drive upload, generated forms, Section 2 write-back, or execution evidence. This task explicitly forbids those areas. The required executable plan was reviewed before implementation and is now retained as the completion record for the implemented TASK_317 scope.
