# TASK_319_PUBLIC_DRIVE_UPLOAD_UPDATE_PREVIEW

Status: Complete. Implemented and validated.

Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.

Current active task: none. TASK_318 is complete. TASK_319 implementation is complete. Do not enter TASK_320 without separate approval.

Allowed reason for creating this task: the user asked to continue by defining TASK_319 after TASK_318.

Executable plan:

- `docs/task_319_public_drive_upload_update_preview_plan.md`

## Goal

Add a preview-first public-drive upload/update workflow for the local Official project folder prepared by TASK_316-TASK_318.

The workflow must answer:

```text
Where will the Official project folder be uploaded, which files would be added or safely updated, which files are already current, and which files are blocked because the public-drive copy was changed outside ConnLab?
```

## User Story

As a lab operator, I want to upload or update the local Official project folder to the configured public-drive project location through one explicit action, so I can submit the controlled folder without manually comparing every file or risking a silent overwrite.

## Product Language

Use user-facing language:

- Project Folder
- Public drive upload
- Public Project locations
- Local official project folder
- Public project folder
- Preview upload
- Upload to public drive
- Update public drive
- Conflict
- Already current

Do not use user-facing language:

- Package publish
- Workspace sync
- Rsync
- Manifest
- SQLite
- hash
- upload-state
- API route names

Internal code may use terms such as manifest, SQLite, and upload state, but the UI must stay operator-facing.

## Preconditions

TASK_319 depends on:

- TASK_316 completed local project folder / official workspace record.
- TASK_317 request material collection state.
- TASK_318 Official project folder check.
- Settings resource `Public Project locations` configured as a real directory.

TASK_319 must not proceed when:

- no completed local project folder exists;
- no local Official project folder exists;
- `Public Project locations` is missing or not a directory;
- TASK_318 reports required folder/file conflict;
- the local official folder has blocking missing items that must be fixed before upload;
- the planned public target folder already exists but is not known to ConnLab and contains unmanaged files that would collide with local files.

TASK_319 preview must call the TASK_318 Official project folder check before building the public-drive upload item list. TASK_318 remains the gate for local folder completeness:

- TASK_318 `conflict` blocks public-drive upload.
- TASK_318 blocking missing required folders/files blocks public-drive upload.
- TASK_318 non-blocking warnings or deferred future files may appear as public-drive preview warnings, but must not be hidden.
- TASK_318 request-material missing or Submitted Material missing must block upload until TASK_317/TASK_318 state is repaired.

## Scope

TASK_319 must implement:

1. Backend upload preview service.
2. Backend safe upload/update operation.
3. Public-drive upload state persistence in SQLite and/or `.connlab` cache, with one canonical application read path.
4. Project-scoped API:
   - `GET /api/projects/{project_id}/public-drive/preview`
   - `POST /api/projects/{project_id}/public-drive/upload`
5. Frontend API client types and functions.
6. Workbench Project Folder row integration.
7. One current action only:
   - `Preview public-drive upload`
   - `Upload to public drive`
   - `Refresh public-drive preview`
8. Tests for preview, upload, conflict, idempotency, and Workbench wiring.

## Out Of Scope

- No public-drive delete.
- No silent overwrite.
- No conflict resolution UI that chooses a winner.
- No merge of human-edited public-drive files.
- No generated Test Record, Fee Form, Customer Feedback Form, or Section 2 write-back.
- No request material re-copy.
- No folder repair.
- No email sending or approval workflow.
- No background watcher or automatic sync.
- No LAN/server deployment behavior.
- No permissions or multi-user locking model.
- No StepInstance, TestResult, evidence, report, AI review, or execution data scope.
- No broad Workbench redesign beyond adding the TASK_319 row/action into the existing Project Folder frame.

## Folder Contract

The local Official project folder is:

```text
{Project default save location}\{DL_NUMBER}\{DL_NUMBER} {Sample Description} {Test Item}
```

The public-drive target root is configured by Settings:

```text
Public Project locations
```

The planned public project folder is:

```text
{Public Project locations}\{DL_NUMBER}\{DL_NUMBER} {Sample Description} {Test Item}
```

If the public-drive convention later needs a different parent path, it must be a separate settings/path contract task. TASK_319 must not hard-code a real public-drive path.

## Upload Safety Rules

Public-drive upload must be conservative:

1. Preview before write.
2. Never delete public-drive files.
3. Never silently overwrite files that ConnLab did not previously upload.
4. Auto-update is allowed only when:
   - ConnLab has a previous upload record for the target file;
   - the public-drive file still matches the recorded public copy fingerprint from the last ConnLab upload;
   - the local file differs and should replace that previous ConnLab-managed copy.
5. If the public-drive file exists but ConnLab has no previous matching upload record, mark conflict.
6. If the public-drive file changed after ConnLab's last upload, mark conflict.
7. If local and public files match, mark skip / already current.
8. If the public file is missing and the local file exists, mark add.
9. Wrong-type path conflicts block upload.
10. Directory creation is allowed only for required public target folders owned by this upload operation.
11. Preview and upload must include required empty folders, not only files. Empty folders such as `Photos`, `Test results`, and `Test results\Final Examination` are part of the formal project folder structure even when no files exist inside them yet.
12. Public-drive updates must recheck the current public file fingerprint immediately before writing each file.
13. File writes must use a same-directory temporary file followed by atomic replace where the platform supports it. Upload records may be written only after the final public target exists and matches the copied local file.

## Public Target Adoption Rules

Existing public-drive folders must be classified conservatively:

- If the DL parent folder exists and the planned public Official project folder is missing, preview may create the planned Official project folder.
- If the planned public Official project folder exists and is empty, preview may adopt it and add the required directories/files.
- If the planned public Official project folder exists with required empty directories only, preview should mark those directories `skip` and add missing files.
- If the planned public Official project folder contains extra public files that do not collide with planned local relative paths, preview must warn but must not delete them.
- If an extra public file or directory collides with a planned local relative path and ConnLab has no matching previous upload record, preview must return `conflict`.
- If a public path is a file where a directory is required, or a directory where a file is required, preview must return `conflict`.

## Preview Contract

Preview item actions:

- `add`: local file or required directory does not exist on public drive and can be copied or created.
- `update`: local file differs, public copy is still ConnLab-managed and unchanged since last upload.
- `skip`: public copy already matches local file, or required directory already exists.
- `conflict`: public copy exists but is unmanaged, changed externally, wrong type, or otherwise unsafe.
- `deferred`: local item is future-scope or not generated yet and should not block upload unless TASK_318 marks it required.

Preview overall status:

- `blocked`: missing settings, missing local folder, missing prerequisite, or TASK_318 blocker.
- `ready`: has add/update actions and no conflicts.
- `current`: all checkable files already match public drive.
- `conflict`: at least one unsafe target conflict.
- `warning`: non-blocking warnings exist, such as deferred future files.

The preview must include:

- project id
- local official folder path
- public target folder path
- overall status
- item list with kind (`file` or `directory`), relative path, source path, target path, action, status, message
- blockers
- warnings
- counts for add/update/skip/conflict/deferred
- next action

## Upload Contract

Upload operation:

- reruns preview immediately before writing;
- refuses `blocked` and `conflict`;
- creates required directory items with action `add`;
- copies only file items with action `add` or `update`;
- rechecks public target state immediately before each file write;
- writes files through a same-directory temporary file and atomic replace where available;
- records per-file upload state only after a successful final placement;
- returns copied, updated, skipped, conflict, and failed items;
- reruns preview after upload and returns the refreshed preview.

Partial upload failure must be explainable:

- if some files copy successfully and a later copy fails, return a partial result;
- preserve upload records for files that were successfully copied;
- return failed target and error message;
- do not roll back public-drive files by deleting or overwriting;
- rerun preview so the operator can see what remains.

## Upload State Contract

TASK_319 needs enough state to tell ConnLab-managed public-drive files from human-edited files.

Required per uploaded file:

- project id
- local official folder path at upload time
- public project folder path
- relative path
- public target path
- local fingerprint at upload time
- public fingerprint immediately after upload
- uploaded at
- operation id

Canonical rule:

- SQLite is ConnLab's query/index source.
- `.connlab/upload-state.json` may be used as a portable cache if implemented, but it must not create a second competing truth source.
- Real file system checks remain authoritative for existence and conflict state.
- If SQLite/upload cache and file system disagree, preview must return conflict or warning, not guess.

## Frontend Contract

Workbench `Project Folder` should add a `Public drive upload` row.

Allowed row states:

- Not configured
- Ready to upload
- Already current
- Conflict
- Blocked
- Warning

Top action priority after TASK_319:

1. Missing local project folder: keep TASK_316 action.
2. Missing request material: keep TASK_317 action.
3. Missing folder structure or folder conflict: keep TASK_318 action/blocker.
4. Public-drive preview blocked by missing settings: show `Public Project locations is not configured` with no special Settings shortcut requirement.
5. Public-drive preview ready: show `Upload to public drive`.
6. Public-drive conflict: show conflict blocker and no destructive action.
7. Public-drive current: show `Open public project folder` only if an existing safe open-folder action already exists; otherwise show read-only current state.

Do not show upload action before preview returns `ready`.

Do not expose raw hashes, SQLite, manifest, or backend route names.

## Acceptance Criteria

- Preview blocks when no completed local project folder exists.
- Preview blocks when `Public Project locations` is missing or invalid.
- Preview derives target path from Settings and current project identity.
- Preview reports add/update/skip/conflict counts.
- Preview includes required empty directory items and does not rely only on local files.
- Preview calls TASK_318 folder check and blocks on TASK_318 conflicts or blocking missing required items.
- Preview marks existing unmanaged public files as conflict.
- Preview marks public files changed after ConnLab's last upload as conflict.
- Preview marks matching files as skip / already current.
- Preview classifies existing public target folders as adoptable, warning, or conflict according to the public target adoption rules.
- Upload refuses blocked/conflict previews.
- Upload creates required directory add items and copies only file add/update items.
- Upload never deletes public-drive files.
- Upload never overwrites unmanaged or externally changed public-drive files.
- Upload rechecks each public file immediately before update and uses temporary-file plus atomic replace for final placement.
- Upload records per-file state after successful copies.
- Upload is idempotent: after successful upload, a new preview returns current/skip.
- Partial upload failure returns copied/failed state and refreshed preview.
- Workbench shows one public-drive action only when prerequisites are satisfied.
- Workbench does not reintroduce Package wording.
- Static guard prevents frontend from exposing public-drive upload before TASK_319 wiring.

## Validation Required During Implementation

Backend:

```powershell
py -m pytest tests\unit\test_public_drive_upload_service.py -q
py -m pytest tests\integration\test_public_drive_upload_api.py -q
```

Frontend:

```powershell
cd frontend; npm test -- --run ProjectWorkbench publicDrive --watch=false
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "project_workbench or public_drive or task319"
cd frontend; npm run build
```

General:

```powershell
git diff --check
```

Manual smoke after implementation approval:

1. Configure `Project default save location`, `Template folder`, and `Public Project locations` to local test directories.
2. Open a project with completed local Official project folder and passing TASK_318 check.
3. Run public-drive preview.
4. Confirm the preview shows add actions for a clean target.
5. Upload.
6. Run preview again and confirm current/skip.
7. Modify a public-drive file manually.
8. Run preview and confirm conflict with no overwrite action.

## Completion Rule

TASK_319 must stop after implementation and validation. Do not enter TASK_320 or resume TASK_313 without separate approval.
