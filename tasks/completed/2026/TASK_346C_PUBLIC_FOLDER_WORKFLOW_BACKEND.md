# TASK_346C Public Folder Workflow Backend

Status: complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness
Lane: public-folder-workflow-backend
Owner Roles: Backend Developer / Reviewer / QA / Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-30
Last Updated: 2026-06-30

## 1. Purpose

Create the formal planning-first backend lane for the accepted Folder Actions workflow.

TASK_346C defines the backend/API/file-operation plan for future Workbench Folder Actions:

- public folder year resolution
- Open / Closed public path resolution
- Sync preview / execute
- Submit preview / execute
- Pull preview / execute
- conflict-safe filesystem gateway behavior
- operation/audit records
- temporary-directory validation strategy

This lane is complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness. It does not authorize frontend UI, `frontend/src/api/client.ts`, real public-drive mutation, or any operation against real `D:\Test Project`, `D:\PublicProject`, or LTR workbook files.

## 2. Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`
- `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`
- Current backend official workspace, public-drive upload, external-resource, LTR workbook, API, and tests by read-only scan.

## 3. User-Confirmed Business Model

- Project folder remains local under Settings `Project default save location`.
- Public Project locations is the public root; development may use a local root such as `D:\PublicProject`.
- Public structure is fixed:
  - `Open\<public_folder_year>\<project_folder_name>`
  - `Closed\<public_folder_year>\<project_folder_name>`
- Sync copies the local project folder to public Open before approval.
- Sync is disabled/locked after Submit.
- Submit enters approval stage after explicit confirmation and essential-file checks.
- Submit v1 is a safe move/archive placeholder only. It does not implement encryption, compression, or Windows permission automation.
- Pull copies the authoritative Closed folder back local while preserving the existing local folder as history.
- All Sync, Submit, and Pull operations must be preview-first.
- No workflow may silently overwrite, delete, move, or mutate real user folders.
- `public_folder_year` priority:
  1. ConnLab local LTR application/registration time.
  2. LTR Excel sheet year for the DL number.
  3. Project creation time.
  4. Human confirmation blocker.

## 4. Repository-Proven Starting Point

- `TASK_346A`, `TASK_346B`, and `TASK_346F` are complete/accepted in `docs/task_board.md`.
- Current public-drive backend is upload-only:
  - `GET /api/projects/{project_id}/public-drive/preview`
  - `POST /api/projects/{project_id}/public-drive/upload`
  - target path is currently `<public_drive_root>/<dl_number>/<official_folder_name>`.
- `PublicDriveUploadService` is preview-first and already has useful safety primitives for blockers, unmanaged public conflicts, file fingerprints, and add/update actions.
- `PublicDriveUploadGateway` supports no-overwrite file creation and fingerprint-guarded managed replacement.
- `OfficialProjectWorkspaceService` and `build_official_project_folder_name(...)` already own the local project folder naming rule.
- `OfficialProjectFolderCheckService` already reports required folder/file readiness for the local official folder.
- `ExternalResourceService` currently validates Public Project locations as an existing directory.
- `LtrRecord` has `registered_on` and `requested_date`; `ProjectModel` has `created_on`.
- `ExcelComLTRWorkbookGateway.find_ltr_number(...)` can locate a DL number and return the sheet name in read-only mode.
- Current models include `PublicDriveUploadFileRecordModel` but no operation-level Sync/Submit/Pull history table.
- Current frontend TASK_346B/F intentionally leaves Open/Auto sync/Sync/Submit/Pull disabled or placeholder-only until TASK_346C/TASK_346D.
- Current dirty workspace contains unrelated release-engineering residuals. They are not part of this lane.

## 5. Scope

TASK_346C may plan backend/API/file-operation implementation only:

- public folder year resolver
- public root classification and validation
- Open / Closed path resolver
- Sync preview and execute
- Submit preview and execute
- Pull preview and execute
- safe filesystem gateway for copy/move/archive operations
- operation/audit record model and repository
- service dependency wiring
- backend unit/integration/API tests using temporary directories
- documentation and lane evidence

## 6. Out Of Scope

TASK_346C must not implement:

- frontend Workbench UI changes
- `frontend/src/api/client.ts` helpers or frontend functional wiring
- Projects list or Matrix Editor changes
- real OS folder opening
- real encryption, compression, or Windows permission automation
- public-drive LTR workbook authority writes
- StepInstance, Report generation, AI review, permissions, LAN/server, or multi-user scope
- destructive operations against real local/public folders
- unrelated release-engineering or governance residual cleanup

## 7. Planned Backend Design

### 7.1 Public Folder Year Resolver

Create a resolver that returns:

- `year`
- `source`
- `evidence`
- `warnings`
- `blockers`
- `requires_human_confirmation`

Resolution order:

1. Local registered LTR date:
   - prefer `LtrRecord.registered_on.year`
   - fall back to `LtrRecord.requested_date.year` only as an explicit local LTR application/request date source.
2. LTR Excel sheet year:
   - read-only exact DL lookup
   - accept only unambiguous four-digit sheet names
   - do not infer from the DL number year.
3. Project creation date:
   - use `Project.created_on.year`.
4. Human confirmation:
   - block preview until a future approved UI/API lane supplies an explicit operator-confirmed year.

### 7.2 Root And Path Resolver

The resolver must:

- require the configured Public Project locations root to exist
- never create the root
- classify root as `local_development_root`, `public_like_root`, or `ambiguous_local_root`
- resolve:
  - `Open\<year>\<project_folder_name>`
  - `Closed\<year>\<project_folder_name>`
- use existing official workspace naming as the `project_folder_name` authority
- ensure every resolved target stays under the configured public root
- list missing `Open`, `Closed`, and year subdirectories in preview without creating them

### 7.3 Sync

Sync preview:

- confirms local official project folder exists
- confirms public root and year are resolved
- resolves public Open path
- lists proposed directory creations and copy/update actions
- detects unmanaged public conflicts and path escapes
- blocks when the project is already in submitted/approval stage

Sync execute:

- requires explicit confirmation or a short-lived preview token/snapshot
- revalidates source and target paths
- creates only preview-listed missing subdirectories
- copies/adds new files without overwrite
- updates only ConnLab-managed files using fingerprint checks
- records operation history

### 7.4 Submit

Submit preview:

- requires local folder readiness from `OfficialProjectFolderCheckService`
- requires resolved year and public Open path
- requires Open working copy exists or is planned from confirmed sync preview
- blocks when Closed target already exists
- blocks unresolved unmanaged conflicts
- lists planned Open-to-Closed archive/move.

Submit execute:

- requires explicit confirmation
- revalidates preview
- performs safe Open-to-Closed move/archive placeholder
- does not encrypt, compress, or mutate Windows permissions
- locks future Sync through operation state
- records operation history and approval-stage entry.

### 7.5 Pull

Pull preview:

- requires public Closed source exists
- resolves a local target that preserves existing local working folder
- blocks unsafe path escapes and ambiguous local conflicts
- lists copy target and conflict strategy.

Pull execute:

- requires explicit confirmation
- never overwrites the current local project folder
- copies Closed authoritative folder to a timestamped or otherwise unique local history target
- records operation history.

### 7.6 Operation / Audit Records

Plan a new operation-level persistence model such as `project_public_folder_workflow_operations` with:

- operation id
- project id
- operation type: `sync`, `submit`, `pull`
- preview id or snapshot fingerprint
- public root class
- resolved year and year source
- local source path
- public Open path
- public Closed path
- target path
- confirmation flags
- operator when available
- started/completed timestamps
- status
- blockers/conflicts/errors JSON
- metadata JSON for future extension

File-level managed upload records may be reused or extended only if this does not blur old upload-only semantics with the new workflow.

## 8. May Touch

Planner/Reviewer may touch now:

- `tasks/TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND.md`
- `docs/task_346c_public_folder_workflow_backend_plan.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_planner.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_reconciliation_planner.md`
- `docs/task_board.md`

Authorized Developer implementation may touch:

- `backend/application/public_folder_workflow_service.py`
- `backend/application/public_folder_year_resolver.py`
- `backend/application/public_folder_path_resolver.py`
- `backend/infrastructure/files/public_folder_workflow_gateway.py`
- `backend/infrastructure/storage/repositories/public_folder_workflow.py`
- `backend/infrastructure/storage/repositories/__init__.py`
- `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/api/routes_public_folder_workflow.py`
- `backend/api/dependencies.py`
- `backend/api/main.py`
- `backend/application/public_drive_upload_service.py` only if needed for compatibility or safe primitive extraction
- `backend/infrastructure/files/public_drive_upload_gateway.py` only if extracting shared no-overwrite/fingerprint primitives
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` only for read-only DL-to-sheet-year lookup support
- focused backend tests under `tests/unit/` and `tests/integration/`
- TASK_346C task/plan/evidence/board docs

## 9. Must Not Touch

- frontend Workbench UI, including accepted TASK_346B/TASK_346F files
- `frontend/src/api/client.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- real LTR workbook files
- public-drive LTR workbook authority write behavior
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope
- `.agents/**`
- `docs/project_management/**`
- release-engineering residuals such as `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts/tests, and `temp_agents_stash.md`

## 10. Locked Paths

- `frontend/**`
- `frontend/src/api/client.ts`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`
- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release-engineering scripts/tests
- `temp_agents_stash.md`

## 11. Validation Gate

Reviewer plan gate status: passed.

Reviewer implementation-readiness status: passed by conversational callback.

User authorization status: user approved TASK_346C reconciliation and Developer implementation after readiness.

Developer implementation must preserve:

- TASK_346C is backend/API/file-operation only.
- Frontend UI and `frontend/src/api/client.ts` remain locked.
- The plan preserves preview-first and explicit-confirmation semantics.
- Root classification and directory creation policy are conservative.
- `public_folder_year` does not infer from DL number.
- Submit v1 excludes encryption/permissions/compression.
- Pull preserves existing local folders.
- Operation history is sufficient for traceability.
- Tests use temporary directories only and never touch real local/public folders.

Future Developer validation must include:

- unit tests for public-folder year resolver
- unit tests for root classifier and Open/Closed path resolver
- unit tests for sync/submit/pull preview conflict cases
- filesystem gateway tests using temporary directories only
- integration/API tests for preview and execute success cases
- integration/API tests for missing root, unresolved year, existing Closed target, unmanaged Open conflicts, submit lock, pull local conflict, and path escape blockers
- targeted status proving no frontend/API-client/Projects/Matrix files changed
- no-real-folder mutation check

## 12. Merge Gate

Implementation is authorized but not complete.

Implementation can merge only after:

- Developer evidence proves scoped backend-only changes.
- Backend unit/integration/API tests pass.
- `git diff --check` and trailing whitespace scans pass.
- Reviewer implementation gate passes.
- QA integration smoke runs with temporary local/public roots if routed.
- Integrator confirms no frontend/API-client/Projects/Matrix/real-folder/future-scope or unrelated residuals are packaged.

## 13. Definition Of Ready

Definition of Ready for planned lane and Reviewer plan gate: satisfied.

Definition of Ready for Developer implementation: satisfied after Reviewer plan gate pass, user-approved Developer planning-first, Developer planning-first completion, Reviewer implementation-readiness pass, and explicit user approval for reconciliation plus Developer implementation.

Blocking clarification questions: none.

## 14. Reconciliation Checkpoint

Planner reconciliation on 2026-06-30 records:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness passed with `reviewer_pass`.
- Reviewer accepted one implementation lane with internal checkpoints: resolver/state/audit foundation; preview-only service/API; execute service/API.
- C1/C2 split fallback remains available if implementation proves too large.
- Reviewer confirmed `auto_sync_enabled` and submit lock are backend workflow state owned.
- Reviewer confirmed preview hash strategy, operation/audit/file-record schema, and temp-dir/no-real-folder validation plan are sufficient.
- User approved reconciliation and Developer implementation.
- Developer implementation was not performed by this Planner pass.

## 15. Stop Point

Current stop point: Developer implementation pass.

Do not route Reviewer, QA, or Integrator until Developer evidence is updated to `ready_for_review`.
