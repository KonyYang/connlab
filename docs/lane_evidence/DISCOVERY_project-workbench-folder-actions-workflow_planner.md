# Discovery: Project Workbench Folder Actions Workflow

Date: 2026-06-29
Role: Planner
Status: discovery_checkpoint
Discovery scope: Project Workbench Folder Actions workflow redesign
Approved lane created: no
Product code changed: no
Developer routed: no
Follow-up status: TASK_346A planned contract lane created; not approved implementation

## Current Phase / Task / Role

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task/lane: none. `docs/task_board.md` reports `TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI` complete and accepted, with no active implementation lane.
- Current role: Planner Discovery.
- Why allowed: the user requested a Planner Discovery Gate for a new Folder Actions workflow redesign and explicitly forbade approved lane creation, product code edits, and Developer routing.

## Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `.agents/skills/impeccable/reference/product.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- Frontend Folder Actions and Workbench code:
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - `frontend/src/components/workflow/FolderActionPanel.tsx`
  - `frontend/src/api/client.ts`
- Backend folder/public-drive/LTR code:
  - `backend/application/official_project_workspace_service.py`
  - `backend/application/official_project_workspace_naming.py`
  - `backend/application/public_drive_upload_service.py`
  - `backend/infrastructure/files/public_drive_upload_gateway.py`
  - `backend/api/routes_public_drive_upload.py`
  - `backend/infrastructure/storage/repositories/public_drive_upload.py`
  - `backend/application/external_resource_service.py`
  - `backend/application/ltr_service.py`
  - `backend/application/ltr_local_commit_service.py`
  - `backend/application/ltr_registration_preview_service.py`
  - `backend/application/ltr_workbook_compatibility_service.py`
  - `backend/application/ltr_authority.py`
  - `backend/infrastructure/office/excel_com_ltr_workbook_gateway.py`
  - `backend/infrastructure/office/ltr_workbook_readonly_open_gateway.py`
  - `backend/infrastructure/office/models.py`
  - `backend/infrastructure/storage/models.py`
  - `backend/infrastructure/storage/repositories/records.py`

## Confirmed By User

- Folder Actions must be a simple folder operation entry point, not a state/readiness panel.
- Folder Actions must not show persistent target paths, file counts, recent sync time, or readiness labels such as Ready, Partial, Waiting, or Not current.
- Project folder action:
  - Show `Open`.
  - Opens the tester local project folder.
  - Users may view files and manually add raw source material there.
  - This merges the previous Open local folder and Add source material ideas.
- Public working copy action:
  - Show an `Auto sync` toggle and `Sync now`.
  - Before approval submission, sync the local project folder to the public-drive Open area.
  - The Open area is a real public working copy viewed by approvers and related users for startup material, test process material, and draft reports.
  - Sync is disabled after the project enters approval.
- Approval package action:
  - Show `Submit`.
  - On approval submission, encrypt/organize the public Open project folder and move it to the Closed area.
  - This is the approval-entry action, not passive status display.
- Approved folder action:
  - Show `Pull`.
  - After approval completion, copy the final authoritative folder from public Closed back to local.
  - An existing local project folder must be preserved as history and never silently overwritten.
- Settings path semantics:
  - Project default save location is the tester local root, for example `D:\Test Project`.
  - Public Project locations is the public-drive root, and may be a local development path such as `D:\PublicProject`.
  - Public structure is fixed as `Open\<public_folder_year>\<project_folder_name>` and `Closed\<public_folder_year>\<project_folder_name>`.
  - Missing public root should block and require Settings correction.
  - Project folder name should reuse the existing local project folder naming rule.
- `public_folder_year` priority:
  - ConnLab local LTR application/registration time.
  - LTR Excel sheet year containing the DL number.
  - Project creation time.
  - If unresolved, block and require human confirmation.
- UI principle:
  - Quiet file operation toolbar.
  - Default display only action buttons and the Auto sync toggle.
  - Show short errors only for exception, blocked config, missing path, conflict, sync locked after submit, or operation failure.
  - Do not display Source material as a separate card or state item.
  - Keep ConnLab restrained, dense, and operational.
- This Discovery turn must not create an approved lane, write product code, route Developer, push, or do destructive git/file operations.

## Confirmed By Repository Evidence

- Board state:
  - `docs/task_board.md` shows `TASK_345D_WORKBENCH_LIFECYCLE_PRIMARY_ACTION_UI` complete and accepted.
  - No active implementation lane is currently listed.
- Architecture rules:
  - Frontend and API route bodies must not directly perform file system or Office operations.
  - File operations belong behind application/infrastructure services and must be preview-first for risky workflows.
  - User-facing UI copy should be operational and business-readable, without exposing future or inactive product scope.
- Current Workbench Folder Action frontend:
  - `ProjectFolderTaskList.tsx` renders a "Next step" primary card, progress rows, details panels, metrics, paths, preview item lists, blockers, and warnings.
  - It exposes details for Request material, Required forms, and Public drive upload, including counts and target paths.
  - `projectFolderTaskSelectors.ts` models a multi-step readiness flow with keys such as `request_material`, `required_forms`, `submitted_material`, and `public_drive_upload`.
  - Current status labels include "Ready to collect", "Partial", "Already current", "Not checked", "Ready to upload", "Conflict", and similar readiness vocabulary.
  - `ProjectWorkbenchActiveMatrixWorkspace.tsx` shows a side card labelled `Folder Action` with current task title, status badge, summary, messages, and one action button.
  - Existing tests assert the current Folder Action card and public-drive checklist behavior.
- Current frontend API client:
  - `fetchPublicDriveUploadPreview(projectId)` calls `GET /api/projects/{project_id}/public-drive/preview`.
  - `uploadPublicDriveProjectFolder(projectId)` calls `POST /api/projects/{project_id}/public-drive/upload`.
  - No client helpers were found for public Open/Closed path resolution, sync preview/execute, submit preview/execute, pull preview/execute, folder open, or auto-sync preference.
- Current local official workspace service:
  - `OfficialProjectWorkspaceService.preview(...)` validates local workspace root, template path, DL identity, and public-drive root availability.
  - Local workspace path is currently `<local_root>/<dl_number>`.
  - Official project folder path is `<local_root>/<dl_number>/<project_folder_name>`.
  - `build_official_project_folder_name(...)` already provides the existing folder naming rule and should be the source for `project_folder_name`.
- Current public-drive service:
  - `PublicDriveUploadService` is preview-first and safe for add/update upload.
  - It validates local official folder, public root, folder check blockers, file fingerprints, and unmanaged public-drive conflicts.
  - Current public target path is `<public_drive_root>/<dl_number>/<official_folder_name>`.
  - It does not implement `Open/<year>/...` or `Closed/<year>/...`.
  - It does not implement submit, move-to-Closed, encrypted/organized approval package staging, pull-from-Closed, approval lock, auto sync, or operation history.
  - The filesystem gateway uses no-overwrite new file copy, fingerprint-guarded managed updates, and same-directory temporary files for atomic replacement.
- Current public-drive API:
  - Existing endpoints are upload-specific: preview and upload only.
  - Response DTOs expose counts, items, local path, public path, blockers, warnings, and `next_action`.
- Current external resource validation:
  - `ExternalResourceService` validates `OFFICIAL_PUBLIC_DRIVE_ROOT` as an existing directory labelled `Public Project locations`.
  - Missing/non-directory public roots already produce validation failures.
- Current LTR/project date evidence:
  - `LtrRecord` has `registered_on` and `requested_date`.
  - `LtrService.register_ltr(...)` sets `registered_on = date.today()`.
  - Local LTR commit carries `requested_date` and audit notes from preview.
  - `ProjectModel` has `created_on`.
  - LTR workbook compatibility detects annual sheets with four-digit names such as `2026`.
  - Excel COM LTR workbook gateway can read annual sheets and locate existing rows by DL number with `sheet_name` and `row_number`.
  - The general `LtrWorkbookSnapshot` stores sheet names and existing LTR numbers, but not a direct `ltr_number -> sheet_name` index.
- Worktree note:
  - Current dirty product files existed before this Discovery write: `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` and `frontend/src/workbench.css`.
  - These are treated as unrelated residuals and are excluded from this Planner checkpoint.

## Existing Code Boundary Summary

- Frontend boundary:
  - Current UI is built around task readiness and preview detail, not the requested four-action toolbar.
  - Current Workbench model fetches and executes public-drive upload, request material collection, required forms generation, official workspace creation/repair, and lifecycle actions in one large hook.
  - A redesign should avoid placing file-system workflow rules in React components. React should call typed API client helpers and render compact actions/errors.
- Backend boundary:
  - Local project folder creation is already an application service with preview and conflict handling.
  - Public-drive upload is already an application service with conservative copy/update primitives, but its domain is upload-only.
  - A new public folder workflow should likely be a new application service or a controlled replacement of `public_drive_upload_service`, not ad hoc code in FastAPI routes.
  - Existing `PublicDriveUploadGateway` safety primitives are reusable for copy/fingerprint/no-overwrite behavior, but submit/move/pull need new preview-first contracts.
- LTR/year boundary:
  - Local LTR and project dates can support parts of `public_folder_year`.
  - Workbook sheet-year resolution is feasible but needs a read-only lookup/index extension because the currently broad snapshot does not preserve the sheet for each DL number.

## Gap Analysis

| Area | Current repository behavior | Target user direction | Gap |
|---|---|---|---|
| Folder Actions UI | Multi-step task/readiness panel with details, metrics, paths, and status labels. | Quiet toolbar with Project folder, Public working copy, Approval package, Approved folder actions. | Requires frontend IA and component/model rewrite. |
| Source material | Separate Request material task/card and details. | Merged into Project folder Open action; users manually add raw source files. | Remove Source material as default Folder Action state item. |
| Public path | `<public_root>/<dl_number>/<folder_name>`. | `<public_root>/Open/<year>/<folder_name>` and `<public_root>/Closed/<year>/<folder_name>`. | Backend path resolver and data migration/compat policy needed. |
| Public folder year | Not resolved. Existing DL/year utilities use DL number and preview command year. | Resolve by local LTR date, workbook sheet year, project created date, then human confirmation. | Need `public_folder_year` resolver and tests. |
| Sync | Current upload preview/execute add/update to one target. | Sync local folder to public Open working copy before approval. | Need new sync semantics, approval lock, operation record, and endpoint names. |
| Auto sync | No auto-sync preference/workflow found. | Toggle Auto sync for public working copy. | Need policy: preference only, trigger points, and locking after submit. |
| Submit | No Open-to-Closed submit/move/encrypt flow. | Encrypt/organize public Open folder and move to Closed when entering approval. | Requires contract for encryption/organizing, conflict handling, and approval stage source. |
| Pull | No Closed-to-local pull workflow. | Copy authoritative Closed folder to local after approval; preserve existing local folder history. | Need pull preview/execute and local conflict preservation policy. |
| Operation history | Upload stores per-file records only. | Sync/submit/pull should be traceable and safe. | Need operation-level audit records for action, actor, paths, year source, preview token, conflicts, timestamps. |
| UI error surface | Details always show metrics/status and item lists. | Only short blocking/error messages when needed. | UI acceptance must ban persistent counts/status/path display. |
| File safety | Upload uses conservative no-overwrite/fingerprint logic. | No silent overwrite/delete/move of real folders. | Reuse primitives but add preview tokens, staging, conflict policy, and explicit execute commands. |

## Formal Lane Need

Formal lanes are required. This is not a Quick Fix.

Reasons:

- The request changes both frontend information architecture and backend file workflow semantics.
- It touches public-drive authority paths and real filesystem movement.
- Submit and pull have destructive or authority-changing implications if mis-scoped.
- The requested `public_folder_year` resolver spans local DB records, LTR workbook sheet metadata, and project creation dates.
- The UI goal requires removing a previously implemented status/readiness mental model, not just renaming labels.
- Current backend API lacks the required Open/Closed/year, submit, pull, auto-sync, and operation-history contracts.

## Recommended Task Split

### TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT

Type: Planner/Designer contract
Recommended status now: proposed/planned only
Recommended next role: Reviewer plan gate after user approval to create the proposed lane

Goal:
Define the product contract for the four Folder Actions, public path rules, `public_folder_year` resolver, preview-first sync/submit/pull semantics, auto-sync locking, operation history, and UI acceptance rules before implementation.

May Touch draft:

- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/task_board.md` planning/proposed section only after explicit user approval

Must Not Touch draft:

- backend product code
- frontend product code
- tests
- public-drive files
- LTR workbook writes
- existing accepted TASK_345D implementation

Locked Paths draft:

- `backend/**`
- `frontend/**`
- `tests/**`
- real `D:\Test Project`, `D:\PublicProject`, or public-drive folders

### TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS

Type: Frontend UI implementation after TASK_346A contract
Recommended status now: future planned, blocked by TASK_346A

Goal:
Replace the current Workbench Folder Action readiness/status panel with the four quiet action groups. This lane may show non-dangerous disabled/blocked states for unavailable backend actions, but must not fake working sync/submit/pull.

May Touch draft:

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` only for UI-facing state plumbing allowed by the contract
- `frontend/src/workbench.css`
- focused Workbench Folder Action tests
- task/plan/evidence files for TASK_346B

Must Not Touch draft:

- backend/API/schema/services
- file-system execute behavior
- Matrix Editor business logic
- Projects list unless separately approved
- StepInstance, Report, AI, permissions, LAN/server, multi-user

Locked Paths draft:

- `backend/**`
- public-drive roots and local project folders
- LTR workbook files
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx` unless a later lane includes it

### TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND

Type: Backend implementation after TASK_346A contract
Recommended status now: future planned, blocked by TASK_346A and three policy questions below

Goal:
Implement `public_folder_year` resolver, Open/Closed path resolver, sync preview/execute, submit preview/execute, pull preview/execute, safe conflict handling, operation records, API DTOs, and backend tests.

May Touch draft:

- new or replacement backend application service for public folder workflow
- public-drive filesystem gateway extensions
- API routes/DTOs for preview/execute operations
- storage models/repositories/migrations for operation history and auto-sync preference if approved
- read-only LTR workbook lookup support for DL-to-sheet-year resolution
- backend tests for resolver, path rules, sync, submit, pull, conflicts, and blocked settings
- task/plan/evidence files for TASK_346C

Must Not Touch draft:

- frontend UI implementation, except API contract docs if needed
- public-drive LTR authority write workflows
- Matrix Editor business logic
- StepInstance, Report, AI, permissions, LAN/server, multi-user
- destructive move/delete of real user folders outside tests

Locked Paths draft:

- `frontend/**` except generated type updates if a separate approved lane allows them
- real public-drive/local project roots
- LTR workbook write adapters for write authority
- `backend/application/project_test_plan_*`
- `backend/modules/runtime_projection/**`

### TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING

Type: Frontend/API-client integration after TASK_346C
Recommended status now: future planned, blocked by TASK_346C

Goal:
Wire the UI from TASK_346B to backend workflow endpoints from TASK_346C, including short errors, disabled sync after submit, and browser/manual smoke behavior.

May Touch draft:

- `frontend/src/api/client.ts`
- Workbench Folder Actions components/model
- Workbench tests and browser smoke notes
- task/plan/evidence files for TASK_346D

Must Not Touch draft:

- backend implementation
- public-drive file semantics
- Projects list, unless a later copy/routing lane explicitly adds it
- StepInstance, Report, AI, permissions, LAN/server, multi-user

Locked Paths draft:

- `backend/**`
- public-drive/local roots
- Matrix Editor implementation

### TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA

Type: QA/Integrator after TASK_346B/C/D
Recommended status now: future planned

Goal:
Validate the complete workflow with temporary directories that simulate `D:\Test Project` and `D:\PublicProject\Open\2026` / `Closed\2026`, with no real public-drive mutation.

May Touch draft:

- QA evidence
- temporary test fixture directories under approved temp paths
- focused backend/frontend smoke scripts if approved
- `docs/task_board.md` closeout after gates pass

Must Not Touch draft:

- product code unless QA findings route back to Developer
- real public-drive/local user folders
- git destructive operations or remote push

Locked Paths draft:

- real public-drive roots
- public LTR workbook files
- unrelated governance/orchestration residuals

## Parallel / Serial Recommendation

- Serial first: TASK_346A contract must come first.
- After TASK_346A:
  - TASK_346B UI refocus can proceed before backend only if it remains non-functional for sync/submit/pull and does not expose fake working actions.
  - TASK_346C backend should proceed before functional UI wiring.
- Serial later:
  - TASK_346D depends on TASK_346C stable API.
  - TASK_346E depends on implementation lanes.
- Parallel candidate:
  - UI visual refocus and backend implementation can be parallel only after the contract is accepted and if UI consumes mocked/disabled contract states without inventing backend fields.

## UI Acceptance Standards Draft

- Folder Actions appears as a compact toolbar/action cluster, not a status panel.
- Default visible groups/actions:
  - Project folder: `Open`
  - Public working copy: `Auto sync` toggle and `Sync now`
  - Approval package: `Submit`
  - Approved folder: `Pull`
- No persistent display of:
  - target paths
  - file counts
  - recent sync/submit/pull timestamps
  - Ready/Partial/Waiting/Not current/current status labels
  - Source material as a separate card
  - public-drive preview item lists
- Short error/blocker text may appear only for actionable exceptions:
  - missing settings
  - root/path does not exist
  - path conflict
  - sync locked after submit
  - approval stage not ready
  - operation failure
  - manual year confirmation needed
- UI remains dense, restrained, and operational under `$impeccable` and frontend architecture rules.
- React components do not perform file-system logic or path mutation decisions.
- If an action is not implemented in a lane, it must be clearly blocked/disabled by accepted contract state rather than pretending to run.

## Backend File Operation Acceptance Standards Draft

- All sync/submit/pull operations have read-only preview endpoints before execute endpoints.
- Execute endpoints use fresh validation or a short-lived preview token/snapshot to detect changed filesystem state.
- Missing public root blocks with a Settings correction message.
- Local and public target paths are resolved by application services, not API route bodies.
- No silent overwrite of local or public folders/files.
- No silent delete of local or public folders/files.
- No destructive move from a non-ConnLab-managed path.
- Open/Closed/year directories are never created in preview.
- Any execute-time directory creation must be explicit in the preview/result and confined under the configured public root.
- Public Open sync detects unmanaged/conflicting public files.
- Submit detects existing Closed target conflicts before any move/copy.
- Pull preserves existing local folder history with an explicit, tested naming/location policy.
- Operation records capture action, project, resolved paths, year source, operator if available, timestamp, status, conflict/error summary, and source fingerprints/snapshot as applicable.
- Backend tests use temporary directories only.

## `public_folder_year` Resolver Recommendation

Recommended resolver order:

1. Local ConnLab LTR evidence:
   - Prefer a registered local LTR record linked to the project.
   - Use `registered_on.year` when present.
   - If absent, use `requested_date.year` only if the accepted contract confirms it represents application/registration timing.
2. LTR workbook sheet year:
   - Use a read-only workbook lookup that finds the exact DL number and returns the annual sheet name.
   - Accept only unambiguous four-digit sheet names.
   - Block if multiple sheets contain the DL number or the sheet name cannot be parsed as a year.
3. Project creation date:
   - Use `Project.created_on.year`.
4. Human confirmation:
   - Block preview and ask for explicit year confirmation if no source resolves a reliable year.

Required backend design:

- A resolver result should include `year`, `source`, `evidence`, and `warnings`.
- The chosen year source must be stored in operation history for sync/submit/pull traceability.
- The resolver must not infer year from the DL number unless a future contract explicitly allows it.

## Sync / Submit / Pull Safety Strategy Draft

### Sync

- Preview:
  - Validate local official folder exists.
  - Validate public root exists.
  - Resolve `public_folder_year` and `project_folder_name`.
  - Resolve target `Open/<year>/<project_folder_name>`.
  - Compare local and Open file trees with fingerprints.
  - Report conflicts without writing.
- Execute:
  - Revalidate preview inputs.
  - Create missing Open/year/project directories only if accepted by contract and listed by preview.
  - Add new files with no-overwrite semantics.
  - Update only ConnLab-managed files whose previous public fingerprint still matches.
  - Block after submit/approval lock.

### Submit

- Preview:
  - Validate public Open folder exists and belongs to this project.
  - Validate approval-entry conditions.
  - Resolve Closed target.
  - Detect existing Closed conflicts.
  - List any directory creation, package staging, encryption/organizing steps, and move/copy plan.
- Execute:
  - Revalidate snapshot.
  - Stage package in a ConnLab temporary/staging path under the same public root where possible.
  - Do not delete local folder.
  - Do not overwrite Closed target.
  - Mark sync locked after successful submit.
  - Record operation history.

### Pull

- Preview:
  - Validate Closed folder/package exists.
  - Validate local root exists.
  - Detect current local folder and propose a history-preserving strategy.
- Execute:
  - Preserve the current local folder according to approved policy.
  - Copy authoritative Closed folder to the approved local destination without silent overwrite.
  - Record operation history.

## Blocking Clarification Questions

Resolved by user follow-up on 2026-06-29:

1. Submit click, after manual confirmation and prerequisite checks, enters approval stage.
2. Submit v1 is safe move/archive placeholder only. It does not implement real encryption, permissions, or compression.
3. Public Project locations may be a local development root. Planner should define a safety policy for classifying local-development vs public-like roots and for preview/execute creation of `Open`, `Closed`, and year subdirectories.

No remaining blocker prevents a planned contract lane. Developer implementation remains blocked until the contract is reviewed, accepted, and a downstream implementation lane is separately approved.

## Follow-Up Contract Decisions

- TASK_346A should be the first formal lane.
- TASK_346A status is planned and ready for Reviewer plan gate, not approved implementation.
- Submit after confirmation is the approval-stage entry point.
- Submit success locks Sync.
- Submit v1 excludes encryption, permission automation, and compressed package rules. Those stay future scope.
- Product runtime should not silently create the configured public root.
- Preview may propose missing `Open`, `Closed`, `Open/<year>`, and `Closed/<year>` subdirectory creation, but preview must not create them.
- Execute may create listed subdirectories only under the configured root after explicit confirmation and path containment checks.
- Root classification should distinguish:
  - local development root,
  - public-like root,
  - ambiguous local root that needs explicit confirmation before risky execute operations.

## Definition Of Ready Judgment

- Ready for approved implementation lane: no.
- Ready for proposed/planned contract lane: yes.
- Reason implementation is not ready:
  - TASK_346A is contract-only and has not passed Reviewer plan gate yet.
  - Downstream backend/frontend/QA lanes have not been separately approved.
  - Backend APIs for sync/submit/pull do not exist.
  - Current UI and backend mental models differ materially from the requested workflow.

## Recommended Next Action

Created a formal planned lane:

- TASK_ID: `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT`
- lane: `project-workbench-folder-actions-contract`
- status: planned, ready for Reviewer plan gate, not approved implementation
- next role: Reviewer plan gate

Do not route Developer until TASK_346A is created, reviewed, and explicitly approved according to ConnLab lane protocol.

## Validation Performed For This Discovery

- Read required governance, architecture, UI, frontend, backend, public-drive, and LTR evidence listed above.
- Confirmed no product code was edited.
- Confirmed no approved lane was created.
- Existing unrelated dirty files were not modified or reverted.
- Follow-up created only planned contract/task/evidence/board draft files for TASK_346A.

## Completion Callback Text

来源角色：ConnLab｜总计划者 Planner
完成状态：ready_for_review
TASK_ID：TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT
lane：project-workbench-folder-actions-contract
evidence 路径：docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md
建议下一角色：Reviewer plan gate
阻塞摘要：none for plan review. TASK_346A is planned contract-only and not approved for Developer implementation. 请立即执行一次全自动编排扫描，只执行一个合法路由动作。
