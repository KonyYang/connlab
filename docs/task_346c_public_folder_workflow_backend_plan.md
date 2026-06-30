# TASK_346C Public Folder Workflow Backend Plan

Status: complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: public-folder-workflow-backend
Created: 2026-06-30
Last Updated: 2026-06-30

## 1. Discovery Gate

Current active task/lane:

- `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND` is complete/accepted after Developer implementation, Reviewer implementation gate, QA gate, and Integrator packaging/readiness.
- This plan remains the accepted backend/API/file-operation contract for the packaged TASK_346C implementation.

Why Planner is allowed:

- `docs/task_board.md` says the next Folder Actions lane such as backend TASK_346C should be created or activated by Orchestrator/Planner.
- TASK_346A contract, TASK_346B UI refocus, and TASK_346F contextual panel polish are complete/accepted.
- The user requested planning/creation only and explicitly forbade product code and Developer routing.

## 2. User Goal Restatement

The user wants the backend foundation for the accepted Folder Actions workflow. The backend must support future UI operations for local project folder facts, public Open working copy sync, Submit into approval/Closed area, and Pull from Closed back local. The workflow must be preview-first, conflict-safe, and must not mutate real local/public folders silently. This lane is backend/API/file-operation planning only; frontend wiring remains downstream.

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- TASK_346A task, plan, Discovery evidence, Planner evidence
- TASK_346B task, plan, Developer evidence
- TASK_346F task, plan, Developer evidence, QA evidence, board closeout
- Backend folder/public-drive/LTR code and tests:
  - `backend/application/official_project_workspace_service.py`
  - `backend/application/official_project_workspace_naming.py`
  - `backend/application/official_project_folder_check_service.py`
  - `backend/application/public_drive_upload_service.py`
  - `backend/infrastructure/files/public_drive_upload_gateway.py`
  - `backend/api/routes_public_drive_upload.py`
  - `backend/infrastructure/storage/repositories/public_drive_upload.py`
  - `backend/application/external_resource_service.py`
  - `backend/application/ltr_service.py`
  - `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
  - `backend/infrastructure/storage/models.py`
- `backend/infrastructure/storage/database.py`
- `backend/api/dependencies.py`
- relevant unit/integration tests
- Developer planning-first re-read:
  - `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
  - `docs/project_management/ROLE_THREAD_REGISTRY.md`
  - `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_planner.md`
  - `tests/unit/test_public_drive_upload_service.py`
  - `tests/integration/test_public_drive_upload_api.py`

## 4. Confirmed By User

- Public Project locations is the public root; local development paths such as `D:\PublicProject` are allowed.
- Public structure must be `Open\<public_folder_year>\<project_folder_name>` and `Closed\<public_folder_year>\<project_folder_name>`.
- Sync copies local project folder to public Open before approval.
- Sync must be disabled after Submit.
- Submit enters approval stage after explicit confirmation and essential-file checks.
- Submit v1 is safe move/archive placeholder only, not encryption.
- Pull copies authoritative Closed folder back local and preserves existing local folder history.
- All operations are preview-first and conflict-safe.
- No silent overwrite/delete/move of real user folders is allowed.
- `public_folder_year` priority is local LTR date, workbook sheet year, project creation date, then human confirmation.

## 5. Confirmed By Repository Evidence

- TASK_346A accepted the Folder Actions contract and reserved `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`.
- TASK_346B and TASK_346F completed frontend-only placeholder UI. Both explicitly excluded backend workflow, `frontend/src/api/client.ts`, real file operations, public folder resolver, and Sync/Submit/Pull execute behavior.
- Current `PublicDriveUploadService` is preview-first but upload-only; it targets `<public_drive_root>/<dl_number>/<official_folder_name>`, not Open/Closed/year paths.
- Current `PublicDriveUploadGateway` already has conservative file-copy primitives: exclusive creation for new files and fingerprint-guarded replacement for managed files.
- Current public-drive API exposes only `/preview` and `/upload`, not sync/submit/pull workflow endpoints.
- `OfficialProjectWorkspaceService` owns local workspace preview/creation and uses the configured Project default save location.
- `build_official_project_folder_name(...)` owns the project folder naming rule.
- `OfficialProjectFolderCheckService` already supplies local folder readiness checks that Submit can reuse.
- `ExternalResourceService` treats Public Project locations as an existing directory and reports missing directories as validation failures.
- Local LTR/project date data exists: `LtrRecord.registered_on`, `LtrRecord.requested_date`, and `Project.created_on`.
- `ExcelComLTRWorkbookGateway.find_ltr_number(...)` can read exact DL rows and return the workbook `sheet_name`.
- Current persistence has file-level public upload records but no operation-level Sync/Submit/Pull record.

## 6. Planner Inferences

- TASK_346C can be planned as one cohesive backend lane because year resolution, path resolution, operation preview, execute safety, and operation history are tightly coupled.
- If Reviewer considers the implementation too large, split before implementation into:
  - `TASK_346C1_PUBLIC_FOLDER_RESOLVERS_AND_AUDIT_MODEL`
  - `TASK_346C2_PUBLIC_FOLDER_SYNC_SUBMIT_PULL_EXECUTION`
- Existing upload code should not be renamed into Sync/Submit/Pull, because old upload semantics differ from the accepted business model.
- Safe primitives can be extracted or reused, but API and operation history should be new workflow concepts.

## 7. Existing Backend Boundary Summary

Current backend areas:

- Local workspace:
  - `OfficialProjectWorkspaceService.preview/create`
  - validates local root/template/DL identity
  - produces `official_folder_path`
- Required folder/file readiness:
  - `OfficialProjectFolderCheckService.preview/repair-folders`
  - can block Submit when essential project/folder files are missing
- Public-drive upload:
  - `PublicDriveUploadService.preview/upload`
  - safe add/update upload to old target path
  - no Open/Closed/year, Submit, Pull, approval lock, auto-sync preference, or workflow operation history
- External resources:
  - Settings resource path is stored as `OFFICIAL_PUBLIC_DRIVE_ROOT`
  - validation expects an existing directory
- LTR/year:
  - local LTR records and project dates exist
  - Excel COM gateway has exact DL-to-sheet lookup capability
- API:
  - public-drive routes are old upload-specific and must not be treated as TASK_346C workflow routes

## 8. Lane Split Decision

Developer planning-first decision: keep one implementation lane, `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`, but require staged internal implementation checkpoints.

Reason:

- The backend contract should be reviewed as one unit so API DTOs, operation records, preview tokens, root policy, and file safety rules stay consistent.
- Existing public-drive upload code already proves the safe-copy primitive shape, but the accepted workflow needs one coherent resolver/state/audit contract before Sync, Submit, and Pull are exposed.
- Splitting resolver/audit from execution before implementation would create temporary API/data contracts that immediately need revision when execution semantics are added.
- The lane is implementation authorized after Reviewer implementation-readiness pass and explicit user approval for reconciliation plus Developer implementation.

Required implementation checkpoints inside this one lane:

1. Resolver/state/audit foundation:
   - public root validation/classification
   - `public_folder_year` resolution
   - Open/Closed path resolution
   - workflow state repository
   - operation/audit repository
   - preview hash builder
2. Preview-only service/API:
   - context
   - sync preview
   - submit preview
   - pull preview
   - no filesystem mutation beyond reads
3. Execute service/API:
   - sync execute
   - submit execute and submit-lock update
   - pull execute to history target
   - operation audit records
   - no-overwrite and path-containment tests

Reviewer split fallback if implementation-readiness still judges this too large:

- `TASK_346C1_PUBLIC_FOLDER_RESOLVER_STATE_AUDIT_PREVIEW`
- `TASK_346C2_PUBLIC_FOLDER_SYNC_SUBMIT_PULL_EXECUTION`

Downstream lanes remain:

- `TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING`: frontend API client and Workbench wiring after TASK_346C.
- `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA`: temp-dir workflow QA after backend and frontend wiring.

## 9. Backend API / Service Design Draft

### 9.1 Proposed Service Shape

Create `PublicFolderWorkflowService` with:

- `context(project_id)`
- `preview_sync(project_id, command)`
- `execute_sync(project_id, command)`
- `preview_submit(project_id, command)`
- `execute_submit(project_id, command)`
- `preview_pull(project_id, command)`
- `execute_pull(project_id, command)`

Create helper components:

- `PublicFolderYearResolver`
- `PublicFolderPathResolver`
- `PublicFolderRootClassifier`
- `PublicFolderWorkflowGateway`
- `PublicFolderWorkflowStateRepository`
- `PublicFolderWorkflowOperationRepository`
- `PublicFolderWorkflowPreviewHasher`

### 9.2 API Draft

Suggested prefix:

```text
/api/projects/{project_id}/public-folder-workflow
```

Suggested endpoints:

- `GET /context`
- `POST /sync/preview`
- `POST /sync/execute`
- `POST /submit/preview`
- `POST /submit/execute`
- `POST /pull/preview`
- `POST /pull/execute`

Execute requests should include explicit confirmation and either:

- a preview snapshot hash, plus
- enough explicit confirmation flags for directory creation, move/archive, and overwrite-safe managed updates.

### 9.3 Shared Response Contract

Preview responses should include:

- project id
- operation type
- status: `ready`, `blocked`, `conflict`, `warning`, `current`
- local official folder path
- public root path
- public root class
- resolved year / source / evidence
- Open path
- Closed path
- planned creations
- planned copy/move/archive items
- blockers
- warnings
- conflicts
- required confirmations
- preview id or snapshot hash
- next action

Execute responses should include:

- operation id
- operation status
- copied / updated / moved / skipped / failed counts
- conflicts / errors
- operation record snapshot
- follow-up preview

### 9.4 Auto Sync Preference Ownership

Auto sync preference is backend-owned workflow state, not a frontend-only local setting.

TASK_346C should persist the preference in a new per-project workflow state record so future frontend wiring can render the toggle consistently across sessions and after restart. The preference does not imply a background scheduler in this lane.

Recommended state fields:

- `project_id`
- `auto_sync_enabled`
- `sync_locked`
- `submitted_at`
- `submit_operation_id`
- `last_sync_operation_id`
- `last_pull_operation_id`
- `created_at`
- `updated_at`

Accepted behavior:

- `GET /context` returns `auto_sync_enabled` and `sync_locked`.
- A backend preference update endpoint may be added only if Reviewer accepts it as API foundation for TASK_346D. If it is considered frontend wiring scope, implementation should still create the persisted state model and leave preference writes to a downstream lane.
- No automatic timer, watcher, or background sync is introduced in TASK_346C.

### 9.5 Submit-Lock Persistence Ownership

Submit lock is backend-owned and must not rely on frontend disabled state.

The lock is derived from the persisted workflow state after a successful Submit execute:

- `sync_locked = true`
- `submitted_at = <operation completion time>`
- `submit_operation_id = <operation id>`

Sync preview and sync execute must return a blocked response when `sync_locked` is true. Lifecycle Activate/Close behavior is not part of this lane; this lock only protects public-folder workflow operations after approval submission.

### 9.6 Preview Snapshot Strategy

Use recomputable preview hashes instead of durable preview tokens.

Preview response includes `preview_hash` computed from:

- operation type
- project id
- workflow state version fields
- resolved public root and root class
- resolved year and year source
- local official folder path
- Open/Closed target paths
- planned directory creations
- planned file/move/pull items with fingerprints, size, and modified time where available
- blockers, warnings, conflicts, and required confirmations

Execute requests must include `preview_hash`. Execute recomputes the preview immediately before mutation and returns `409 preview_stale` when the hash no longer matches. Operation/audit records store the executed hash and snapshot JSON.

### 9.7 Operation / Audit Schema Refinement

Add new workflow tables instead of overloading old public-drive upload records.

Recommended tables:

- `project_public_folder_workflow_states`
- `project_public_folder_workflow_operations`
- `project_public_folder_workflow_file_records`

`project_public_folder_workflow_operations` should capture:

- `operation_id`
- `project_id`
- `operation_type`: `sync`, `submit`, `pull`
- `status`: `completed`, `blocked`, `conflict`, `failed`
- `preview_hash`
- `requested_at`
- `started_at`
- `completed_at`
- `operator`
- `public_root`
- `public_root_class`
- `public_folder_year`
- `year_source`
- `local_official_folder_path`
- `public_open_path`
- `public_closed_path`
- `target_path`
- count fields for created/copied/updated/moved/skipped/conflict/error
- `blockers_json`
- `warnings_json`
- `conflicts_json`
- `snapshot_json`
- `metadata_json`

`project_public_folder_workflow_file_records` should track ConnLab-managed public files separately from the legacy upload table because Open/Closed/year workflow semantics differ from old `/public-drive/upload`.

## 10. Safety Strategy

- Preview never creates roots, subdirectories, files, operation records, or LTR workbook changes.
- Product runtime never silently creates the configured public root.
- Execute revalidates all resolved paths and keeps them inside the configured root.
- Execute may create missing `Open`, `Closed`, and year subdirectories only when preview listed them and the request explicitly confirms creation.
- Sync may add files and update ConnLab-managed files only; unmanaged public file conflicts block.
- Submit may move/archive only the ConnLab-managed Open working copy to Closed after confirmation.
- Submit v1 does not encrypt, compress, or mutate permissions.
- Pull must never overwrite the existing local folder; it copies to a unique history target.
- Tests must use temporary directories only.

## 11. May Touch

Planner/Reviewer now:

- `tasks/TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND.md`
- `docs/task_346c_public_folder_workflow_backend_plan.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_planner.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_developer.md`
- `docs/lane_evidence/TASK_346C_public-folder-workflow-backend_reconciliation_planner.md`
- `docs/task_board.md`

Authorized Developer implementation:

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
- `backend/application/public_drive_upload_service.py` only for compatibility or shared primitive extraction
- `backend/infrastructure/files/public_drive_upload_gateway.py` only for shared no-overwrite/fingerprint primitive extraction
- `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py` only for read-only DL-to-sheet-year lookup support
- `tests/unit/test_public_folder_year_resolver.py`
- `tests/unit/test_public_folder_workflow_service.py`
- `tests/unit/test_public_folder_workflow_gateway.py`
- `tests/integration/test_public_folder_workflow_api.py`
- `tests/integration/test_public_folder_workflow_migration.py`
- TASK_346C docs/evidence/board files

## 12. Must Not Touch / Locked Paths

Must Not Touch:

- frontend Workbench UI and accepted TASK_346B/TASK_346F frontend files
- `frontend/src/api/client.ts`
- Projects list and Matrix Editor
- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- real LTR workbook files
- public-drive LTR workbook authority writes
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope
- `.agents/**`
- `docs/project_management/**`
- release-engineering residuals: `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts/tests, and `temp_agents_stash.md`

Locked Paths:

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

## 13. Validation Gate

Reviewer implementation-readiness gate:

- Status: passed by conversational callback.
- Reviewer confirmed backend-only scope and frontend/API-client locks.
- Reviewer confirmed API/service design is preview-first with explicit confirmation.
- Reviewer confirmed root classification policy does not silently create or mutate real public roots.
- Reviewer confirmed Submit v1 excludes encryption/permissions/compression.
- Reviewer confirmed `public_folder_year` priority and no DL-number-year inference.
- Reviewer confirmed auto sync preference ownership is backend workflow state, with no background scheduler in TASK_346C.
- Reviewer confirmed submit-lock persistence is backend workflow state and not frontend-only disablement.
- Reviewer confirmed preview hash strategy is adequate and avoids durable preview token cleanup.
- Reviewer confirmed operation/state/file-record model is adequate.
- Reviewer confirmed temp-dir-only test strategy.

Developer validation after approval:

- Unit tests for year resolver, root classifier, path resolver.
- Unit tests for Sync/Submit/Pull preview blockers and conflicts.
- Unit tests for auto-sync preference state and submit-lock behavior.
- Unit tests for preview hash stale rejection.
- Gateway tests for no-overwrite copy, fingerprint update, safe move/archive, and path containment.
- Integration/API tests using temporary local and public roots.
- API tests for preview/execute success and conflict/blocker cases.
- Migration/backward-compatibility tests that start from an existing database without TASK_346C tables and verify `init_db` creates workflow state, operation, and file-record tables without touching existing public-drive upload data.
- No-real-folder mutation checks.
- Static/path checks proving tests do not write under `D:\Test Project`, `D:\PublicProject`, real public-drive folders, or real LTR workbook paths.
- Targeted forbidden-scope status showing no frontend/API-client/Projects/Matrix changes.

## 14. Merge Gate

Implementation is authorized but not complete.

Future merge requires Developer implementation evidence, backend tests, Reviewer implementation gate, QA temp-dir smoke if routed, and Integrator packaging/readiness.

## 15. Blocking Questions

None.

Definition of Ready for planned lane and Reviewer plan gate: satisfied.

Developer planning-first gate: satisfied.

Reviewer implementation-readiness gate: satisfied by callback.

User implementation approval: satisfied.

Definition of Ready for Developer implementation: satisfied; source-of-truth aligned by Planner reconciliation.

## 16. Planner Reconciliation

Planner reconciliation on 2026-06-30 records:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed as docs-only.
- Reviewer implementation-readiness passed with `reviewer_pass`.
- Reviewer confirmed one implementation lane is acceptable with internal checkpoints:
  1. resolver/state/audit foundation
  2. preview-only service/API
  3. execute service/API
- C1/C2 split fallback remains available if implementation proves too large.
- Reviewer confirmed `auto_sync_enabled` and submit lock are backend workflow state owned.
- Reviewer confirmed preview hash strategy, operation/audit/file-record schema, and temp-dir/no-real-folder validation plan are sufficient.
- User approved TASK_346C reconciliation and Developer implementation.
- This reconciliation does not implement product code and does not widen TASK_346C scope.

## 17. Stop Point

Current stop point: Developer implementation pass.

Do not route Reviewer, QA, or Integrator until Developer evidence is updated to `ready_for_review`.
