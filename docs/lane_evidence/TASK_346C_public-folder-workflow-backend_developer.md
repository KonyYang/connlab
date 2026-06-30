# TASK_346C Public Folder Workflow Backend Developer Evidence

Status: ready_for_review - fix pass complete pending Reviewer re-gate
Date: 2026-06-30
Role: Developer
Task: `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`
Lane: `public-folder-workflow-backend`

## Scope

This pass was planning-first only. No backend, frontend, API client, tests, real folders, LTR workbook files, packaging files, board files, or orchestration/governance files were modified by this Developer pass.

Allowed files for this pass:

- `docs/task_346c_public_folder_workflow_backend_plan.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`

Stop point:

- Reviewer implementation-readiness gate.
- Do not start Developer implementation until Reviewer readiness passes and the user explicitly approves implementation.

## Sources Read

Governance and lane sources:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND.md`
- `docs/task_346c_public_folder_workflow_backend_plan.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_planner.md`
- TASK_346A/TASK_346B/TASK_346F evidence and accepted scope summaries

Backend discovery sources:

- `backend/application/official_project_workspace_service.py`
- `backend/application/official_project_workspace_naming.py`
- `backend/application/official_project_folder_check_service.py`
- `backend/application/public_drive_upload_service.py`
- `backend/infrastructure/files/public_drive_upload_gateway.py`
- `backend/api/routes_public_drive_upload.py`
- `backend/infrastructure/storage/repositories/public_drive_upload.py`
- `backend/application/external_resource_service.py`
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_public_drive_upload_service.py`
- `tests/integration/test_public_drive_upload_api.py`

## Planning Findings

- Existing `PublicDriveUploadService` is useful evidence for preview-first and safe-copy behavior, but it is upload-only and targets the old public-drive path shape. It should not become the public folder workflow API by renaming.
- Existing `PublicDriveUploadGateway` has reusable primitives for fingerprinting, exclusive file creation, and guarded replacement. TASK_346C can extract or reuse those primitives only if implementation remains within backend file-operation scope.
- `OfficialProjectWorkspaceService` and `build_official_project_folder_name(...)` already own local official workspace and folder naming facts.
- `OfficialProjectFolderCheckService` can provide Submit readiness blockers before public-folder approval movement.
- `ExternalResourceService` already treats Public Project locations as a configured existing directory. TASK_346C must keep that behavior and must not silently create the configured public root.
- `ExcelComLTRWorkbookGateway.find_ltr_number(...)` can provide read-only DL-to-sheet lookup for workbook sheet year evidence, but TASK_346C must not write to the LTR workbook.
- Existing storage has public-drive upload file records, but no workflow state, operation audit, submit lock, auto-sync preference, or Open/Closed/year file records.
- A new router will require `backend/api/main.py` in the future implementation May Touch list.

## Developer Planning Decisions

### Lane Shape

Recommendation: keep TASK_346C as one implementation lane, with staged internal checkpoints:

1. Resolver/state/audit foundation.
2. Preview-only context/sync/submit/pull API.
3. Execute sync/submit/pull API and gateway operations.

Split fallback if Reviewer judges this too large:

- `TASK_346C1_PUBLIC_FOLDER_RESOLVER_STATE_AUDIT_PREVIEW`
- `TASK_346C2_PUBLIC_FOLDER_SYNC_SUBMIT_PULL_EXECUTION`

### Auto Sync Preference

Auto sync preference should be backend-owned workflow state, not frontend-only local state.

TASK_346C should store `auto_sync_enabled` on a per-project workflow state record. This lane must not add a background scheduler, watcher, or automatic sync process. TASK_346D can wire the frontend toggle after the backend context/preference contract exists.

### Submit Lock

Submit lock should be backend-owned workflow state.

After a successful Submit execute, backend state should set `sync_locked = true`, persist `submitted_at`, and link to the `submit_operation_id`. Sync preview and execute should return a blocked response when the lock is active. The frontend disabled state is only presentation.

### Preview Snapshot

Use recomputable `preview_hash` values instead of durable preview-token records.

Execute requests should include the preview hash. Execute recomputes the preview, rejects stale requests with `409 preview_stale`, and stores the executed hash plus snapshot JSON in the operation audit record.

### Storage Model

Future implementation should add separate TASK_346C workflow tables:

- `project_public_folder_workflow_states`
- `project_public_folder_workflow_operations`
- `project_public_folder_workflow_file_records`

This avoids overloading legacy public-drive upload records with Open/Closed/year workflow semantics.

### Temp-Dir Safety

All implementation tests must use `tmp_path` or injected temporary roots. No test or product command may mutate:

- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- real LTR workbook files

The implementation test plan should include path-containment checks, missing-root blockers, no-overwrite conflict checks, stale preview hash rejection, and migration/backward-compatibility checks for new workflow tables.

## Plan Updates

Updated `docs/task_346c_public_folder_workflow_backend_plan.md` to record:

- Developer planning-first status.
- One-lane recommendation with split fallback.
- Auto sync preference ownership.
- Submit-lock persistence ownership.
- Recomputable preview hash strategy.
- Operation/state/file-record schema refinement.
- Future implementation file list, including `backend/api/main.py` and focused tests.
- Temp-dir/no-real-folder safety validation.
- Stop point at Reviewer implementation-readiness gate.

## Existing Dirty Worktree Classification

Current workspace contains unrelated release/packaging residuals and board/planning residuals, including:

- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests
- `temp_agents_stash.md`
- `docs/task_board.md`

These were not touched by this Developer planning-first pass and must remain excluded from TASK_346C implementation packaging unless a separate lane authorizes them.

## Validation

- `git diff --check -- docs/task_346c_public_folder_workflow_backend_plan.md docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md` -> passed.
- Trailing whitespace scan on the two TASK_346C docs -> no matches.
- Targeted forbidden-scope status check -> no frontend, API client, Projects list, Matrix editor, or TASK_346C backend product implementation files changed by this planning-first pass.
- Targeted status did show pre-existing external residuals outside this lane: `docs/packaging_notes.md`, `docs/task_board.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, `temp_agents_stash.md`, and desktop release tests. These remain excluded from TASK_346C planning/implementation packaging.

## Stop Point

Developer implementation complete.

Recommended next role: Reviewer implementation gate.

Do not route QA or Integrator until Reviewer implementation gate passes.

## Implementation Summary

Changed TASK_346C package files:

- `backend/application/public_folder_year_resolver.py`
- `backend/application/public_folder_path_resolver.py`
- `backend/application/public_folder_workflow_service.py`
- `backend/infrastructure/files/public_folder_workflow_gateway.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/repositories/public_folder_workflow.py`
- `backend/infrastructure/storage/repositories/__init__.py`
- `backend/api/routes_public_folder_workflow.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `tests/unit/test_public_folder_year_resolver.py`
- `tests/unit/test_public_folder_workflow_service.py`
- `tests/unit/test_public_folder_workflow_gateway.py`
- `tests/integration/test_public_folder_workflow_api.py`
- `tests/integration/test_public_folder_workflow_migration.py`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`

No changes were made to frontend UI, `frontend/src/api/client.ts`, Projects list, Matrix Editor, real folder paths, LTR workbook files, release-engineering residuals, or `docs/project_management/**`.

### Checkpoint 1 - Resolver / State / Audit Foundation

Implemented:

- `PublicFolderYearResolver`
  - priority: local LTR `registered_on`, local LTR `requested_date`, read-only exact workbook sheet year, project `created_on`, human-confirmation blocker
  - no DL-number-year inference
- `PublicFolderPathResolver`
  - configured Public Project locations root must already exist
  - root is never created
  - resolves `Open/<year>/<project_folder_name>` and `Closed/<year>/<project_folder_name>`
  - path containment checks keep targets under public root
- New workflow persistence models:
  - `project_public_folder_workflow_states`
  - `project_public_folder_workflow_operations`
  - `project_public_folder_workflow_file_records`
- `PublicFolderWorkflowRepository`
  - workflow state persistence
  - backend-owned `auto_sync_enabled`
  - backend-owned `sync_locked`
  - operation audit persistence
  - workflow file-record persistence separate from legacy public-drive upload records

### Checkpoint 2 - Preview-Only Service / API

Implemented:

- `GET /api/projects/{project_id}/public-folder-workflow/context`
- `PUT /api/projects/{project_id}/public-folder-workflow/auto-sync`
- `POST /api/projects/{project_id}/public-folder-workflow/sync/preview`
- `POST /api/projects/{project_id}/public-folder-workflow/submit/preview`
- `POST /api/projects/{project_id}/public-folder-workflow/pull/preview`
- preview responses include resolved year/source/evidence, public root class, Open/Closed paths, planned items, blockers, conflicts, required confirmations, counts, `preview_hash`, `auto_sync_enabled`, and `sync_locked`
- preview does not create directories, files, operation records, or workbook writes

### Checkpoint 3 - Execute Service / API

Implemented:

- `POST /api/projects/{project_id}/public-folder-workflow/sync/execute`
- `POST /api/projects/{project_id}/public-folder-workflow/submit/execute`
- `POST /api/projects/{project_id}/public-folder-workflow/pull/execute`
- execute requires explicit confirmation and matching recomputed `preview_hash`
- stale preview returns conflict semantics through route mapping
- Sync copies new files and updates only managed files with fingerprint checks
- Submit v1 safely moves public Open working copy to Closed, with no encryption/compression/Windows permission automation
- Submit persists backend sync lock and submit operation id
- Pull copies public Closed folder to a unique local history folder and does not overwrite the current local folder
- operation audit records store preview hash and snapshot JSON

## Implementation Validation

Commands run:

- `py -m py_compile backend\application\public_folder_workflow_service.py backend\application\public_folder_year_resolver.py backend\application\public_folder_path_resolver.py backend\infrastructure\files\public_folder_workflow_gateway.py backend\infrastructure\storage\repositories\public_folder_workflow.py backend\api\routes_public_folder_workflow.py backend\api\dependencies.py backend\api\main.py` -> passed.
- `py -m pytest tests\unit\test_public_folder_year_resolver.py tests\unit\test_public_folder_workflow_service.py tests\unit\test_public_folder_workflow_gateway.py tests\integration\test_public_folder_workflow_api.py tests\integration\test_public_folder_workflow_migration.py -q` -> `17 passed in 1.91s`.
- `py -m pytest tests\unit\test_public_drive_upload_service.py tests\integration\test_public_drive_upload_api.py tests\integration\test_api_default_dependencies.py -q` -> `20 passed in 1.90s`.
- `git diff --check -- <TASK_346C package files>` -> passed with LF/CRLF warnings only for existing line-ending normalization behavior.
- Trailing whitespace scan on TASK_346C backend/API/test files -> no matches.
- Static no-real-folder scan on TASK_346C backend/API/test files for `D:\Test Project`, `D:\PublicProject`, `D:/Test Project`, and `D:/PublicProject` -> no matches.

## No-Real-Folder Safety Proof

- All new filesystem unit tests use `tmp_path`.
- API tests use dependency overrides and do not execute real filesystem operations.
- Migration tests use temporary SQLite files under pytest temp directories.
- No test or implementation path writes under real `D:\Test Project/**`, real `D:\PublicProject/**`, real public-drive folders, or real LTR workbook files.
- LTR workbook sheet-year support is implemented as optional read-only lookup. Tests use fakes and do not access real workbook files.

## Forbidden-Scope Status

Targeted status check showed TASK_346C package changes plus pre-existing external residuals.

TASK_346C implementation changes:

- backend/API/storage workflow files listed above
- focused TASK_346C tests listed above
- this Developer evidence file

Pre-existing external residuals still present and excluded:

- `docs/packaging_notes.md`
- `docs/task_board.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests
- `temp_agents_stash.md`

No frontend UI, `frontend/src/api/client.ts`, Projects list, Matrix Editor, real folder path, LTR workbook write, public-drive authority write, StepInstance, Report, AI, permissions, LAN/server, multi-user, `.agents/**`, or `docs/project_management/**` changes were made by this implementation pass.

## Known Residuals

- Browser/manual smoke is not run for this backend-only lane. TASK_346D/TASK_346E should perform UI wiring and temp-dir workflow smoke after frontend API client/wiring exists.
- `PublicFolderWorkflowService` intentionally keeps Sync/Submit/Pull semantics in one implementation unit to preserve the accepted single-lane contract. If Reviewer wants smaller maintenance boundaries, the accepted C1/C2 split fallback remains available for a follow-up refactor before merge.

## Fix Pass - Reviewer B1

Reviewer blocker:

- Submit preview/execute did not block unmanaged files already present in Public Open. A human-created `human-extra.txt` could remain untracked during preview and then move silently to Closed during Submit execute.

Root cause:

- `preview_submit(...)` only checked that Public Open existed and Public Closed did not exist, then planned a whole-directory Open-to-Closed move. It did not reconcile every Public Open file against TASK_346C workflow file records before allowing the directory move.

Changed files for this fix pass:

- `backend/application/public_folder_workflow_service.py`
- `tests/unit/test_public_folder_workflow_service.py`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`

Fix implemented:

- Submit preview now scans every file in Public Open before planning the directory move.
- A Public Open file is considered safe to move only when a workflow file record exists for the same relative path and the record points to that exact Public Open file path.
- Any unmanaged Public Open file is emitted as a conflict item with business-readable copy: `Public Open file is not managed by ConnLab; remove or sync through ConnLab before Submit.`
- Submit execute continues to use the existing recomputed preview hash and conflict validation. That means:
  - executing with a current conflict preview rejects safely;
  - executing with an older ready preview rejects as stale if an unmanaged file appears after preview;
  - Open and Closed contents remain unmoved when conflicts/stale previews are present.

Regression coverage added:

- `test_submit_preview_blocks_unmanaged_public_open_file`
  - creates a managed file through Sync using `tmp_path`;
  - adds unmanaged `human-extra.txt` directly under Public Open;
  - asserts Submit preview is `conflict`, `next_action` is `none`, execute rejects, Public Open remains intact, and Public Closed is not created.
- `test_submit_execute_rejects_stale_preview_when_unmanaged_file_appears`
  - takes a ready Submit preview;
  - adds unmanaged `human-extra.txt` after preview;
  - asserts execute rejects as stale and does not move Public Open to Closed.

Fix-pass validation:

- `py -m pytest tests\unit\test_public_folder_workflow_service.py -q` -> `7 passed in 0.59s`.
- `py -m pytest tests\unit\test_public_folder_year_resolver.py tests\unit\test_public_folder_workflow_service.py tests\unit\test_public_folder_workflow_gateway.py tests\integration\test_public_folder_workflow_api.py tests\integration\test_public_folder_workflow_migration.py -q` -> `19 passed in 2.07s`.
- `py -m pytest tests\unit\test_public_drive_upload_service.py tests\integration\test_public_drive_upload_api.py tests\integration\test_api_default_dependencies.py -q` -> `20 passed in 2.01s`.
- `py -m py_compile backend\application\public_folder_workflow_service.py backend\application\public_folder_year_resolver.py backend\application\public_folder_path_resolver.py backend\infrastructure\files\public_folder_workflow_gateway.py backend\infrastructure\storage\repositories\public_folder_workflow.py backend\api\routes_public_folder_workflow.py backend\api\dependencies.py backend\api\main.py` -> passed.
- `git diff --check -- <TASK_346C package files>` -> passed with existing LF/CRLF warnings only.
- Trailing whitespace scan on TASK_346C package files -> no matches.
- Static no-real-folder scan on TASK_346C backend/API/test files for `D:\Test Project`, `D:\PublicProject`, `D:/Test Project`, and `D:/PublicProject` -> no matches.
- Targeted forbidden-scope status showed no frontend UI, `frontend/src/api/client.ts`, Projects list, Matrix Editor, real folder path, LTR workbook write, public-drive authority write, `.agents/**`, or `docs/project_management/**` changes from this fix pass. Pre-existing release/packaging residuals remain excluded.

Backend/API decision:

- No backend contract expansion, frontend/API client change, public-drive authority write, or real folder mutation was needed. B1 was fixed inside the accepted TASK_346C backend preview/execute safety scope.

## Integrator Packaging / Readiness Closeout

Integrator gate: accepted.

Package scope accepted:

- TASK_346C backend/API/storage/service implementation files.
- TASK_346C focused backend unit/integration/API tests.
- TASK_346C task, plan, planner/developer/QA/reconciliation evidence, and `docs/task_board.md` TASK_346C closeout.

Excluded residuals:

- Release/packaging residuals: `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts, release docs, release task, and desktop-release tests.
- `temp_agents_stash.md`.
- `AGENTS.md`, `.agents/**`, `docs/project_management/**`.
- frontend runtime, `frontend/src/api/client.ts`, Projects registry, Matrix Editor, real `D:\Test Project`, real `D:\PublicProject`, real public-drive folders, real LTR workbook files, public-drive LTR workbook authority writes, TASK_346D+ future scope, StepInstance, Report, AI, permissions, LAN/server, and multi-user scope.

Integrator validation rerun:

- `py -m pytest tests\unit\test_public_folder_year_resolver.py tests\unit\test_public_folder_workflow_service.py tests\unit\test_public_folder_workflow_gateway.py tests\integration\test_public_folder_workflow_api.py tests\integration\test_public_folder_workflow_migration.py -q` -> `19 passed in 1.93s`.
- `py -m pytest tests\unit\test_public_drive_upload_service.py tests\integration\test_public_drive_upload_api.py tests\integration\test_api_default_dependencies.py -q` -> `20 passed in 1.90s`.
- `py -m py_compile backend\application\public_folder_workflow_service.py backend\application\public_folder_year_resolver.py backend\application\public_folder_path_resolver.py backend\infrastructure\files\public_folder_workflow_gateway.py backend\infrastructure\storage\repositories\public_folder_workflow.py backend\api\routes_public_folder_workflow.py backend\api\dependencies.py backend\api\main.py` -> passed.
- Static no-real-folder scan for `D:\Test Project`, `D:\PublicProject`, `D:/Test Project`, and `D:/PublicProject` on TASK_346C backend/API/test files -> no matches.
- Trailing whitespace scan on TASK_346C backend/API/test/docs/evidence files -> no matches.
- Forbidden-scope status showed only external release/packaging residuals and `temp_agents_stash.md`; no frontend/API-client/Projects/Matrix/.agents/docs_project_management changes were present for TASK_346C.

Remote push: intentionally not performed.
