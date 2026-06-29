# TASK_346A Project Workbench Folder Actions Contract Plan

Status: complete/accepted contract after Reviewer plan re-gate; not approved product implementation
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Current Lane: project-workbench-folder-actions-contract
Created: 2026-06-29
Last Updated: 2026-06-29

## 1. Discovery Gate Continuation

### User Confirmed Facts

- Folder Actions should be a quiet file operation toolbar, not a status/readiness panel.
- The default surface should expose four operation groups:
  - Project folder: `Open`
  - Public working copy: `Auto sync` and `Sync now`
  - Approval package: `Submit`
  - Approved folder: `Pull`
- User clicking `Submit`, after explicit confirmation and prerequisite checks, enters the approval stage.
- Once Submit succeeds, Sync is locked.
- Submit v1 should be a safe move/archive placeholder only. It should not implement real encryption, Windows permissions, or compressed package rules.
- Public Project locations may be a real public drive or a local development directory.
- The Planner contract should propose a safety policy for recognizing local-development paths vs public-drive-like paths and for creating `Open`, `Closed`, and year subdirectories.
- `public_folder_year` priority remains local LTR date, LTR Excel sheet year, project creation date, then human confirmation.
- Sync, Submit, and Pull must be preview-first and must not silently overwrite, delete, or move folders.

### Repository-Proven Facts

- `docs/task_board.md` reports no active implementation lane after `TASK_345D`.
- Current Workbench Folder Actions are implemented as task/readiness flows in `ProjectFolderTaskList.tsx`, `projectFolderTaskSelectors.ts`, `ProjectWorkbenchActiveMatrixWorkspace.tsx`, and `ProjectWorkbenchLayout.tsx`.
- Current public-drive backend is upload-only:
  - preview endpoint: `GET /api/projects/{project_id}/public-drive/preview`
  - execute endpoint: `POST /api/projects/{project_id}/public-drive/upload`
  - target path: `<public_drive_root>/<dl_number>/<official_folder_name>`
- Current public-drive backend does not implement `Open/<year>`, `Closed/<year>`, Submit, Pull, approval lock, auto-sync preference, or operation-level history.
- `OfficialProjectWorkspaceService` and `build_official_project_folder_name(...)` already define the local project folder naming source.
- `ExternalResourceService` validates Public Project locations as an existing directory.
- `LtrRecord` has `registered_on` and `requested_date`; `ProjectModel` has `created_on`; Excel COM LTR workbook gateway can locate DL rows with sheet names.
- Architecture rules require file operations in application/infrastructure services, not React components or API route bodies.

### Planner Inferences

- A contract lane should precede backend and frontend implementation because public-drive path authority and file movement safety are cross-cutting.
- The existing `PublicDriveUploadGateway` safety primitives can be reused later, but the upload service shape should not be treated as the final workflow contract.
- A local development public root should be permitted, but execute-time file creation/move behavior should be stricter when the path is ambiguous.
- Auto sync should start as an explicit project preference and manual trigger contract. Background filesystem watching is out of scope unless a later lane approves it.

## 2. Definition Of Ready

Ready for planned contract lane and Reviewer plan gate: yes.

Ready for approved implementation: no.

Reason:

- The user has answered the original blocker questions sufficiently for a contract draft.
- The remaining public root strategy is now explicitly delegated to Planner as a contract decision, not an implementation blocker.
- Backend/frontend implementation still depends on the accepted contract and later user approval.

## 3. Public Root Classification Strategy

The contract should define a conservative classifier for `Public Project locations`.

### Root Existence

- Product runtime should not silently create the configured public root.
- If the configured root does not exist, preview blocks with a Settings correction message.
- Test and QA lanes may create temporary roots inside controlled temp directories.

### Path Classification

Recommended classes:

- `local_development_root`
  - Existing local absolute path intended for development or QA.
  - Examples: a temp fixture root, a repo/test controlled temp root, or a configured local path whose final folder name clearly indicates a development public root such as `PublicProject`.
  - Allowed in development and local smoke.
- `public_like_root`
  - Existing UNC path, mapped/network drive when detectable, or path explicitly confirmed in Settings as the public project root.
  - Treated as higher-risk because other users may observe the files.
- `ambiguous_local_root`
  - Existing local path that is not clearly development/test and not explicitly confirmed as public authority.
  - Preview may resolve paths but execute should require explicit operator confirmation before directory creation, Submit, or Pull.

### Directory Creation Policy

- Preview may list missing `Open`, `Closed`, `Open/<year>`, and `Closed/<year>` directories as proposed creations.
- Preview itself must not create them.
- Execute may create those subdirectories only when:
  - the configured root exists,
  - the final resolved path is inside the configured root,
  - the preview lists the creation,
  - the operator explicitly confirms the operation,
  - the path class allows creation under the accepted policy.
- For `public_like_root`, creation is allowed only after explicit confirmation and should be recorded in operation history.
- For `ambiguous_local_root`, creation should block unless the operator confirms the root role in Settings or the operation request includes an explicit one-time confirmation.

## 4. Folder Actions Contract

### Project Folder: Open

- Purpose: open the tester's local project folder.
- It also covers manual addition of raw source material.
- It must not expose Source material as a separate Folder Actions card.
- Browser/desktop open behavior must be defined by a later implementation lane. If desktop open is unavailable, implementation must use an accepted fallback rather than fake a successful OS open.

### Public Working Copy: Auto Sync / Sync Now

- Sync target: `Open/<public_folder_year>/<project_folder_name>`.
- Sync is allowed only before Submit succeeds.
- Sync locks after Submit succeeds.
- `Auto sync` v1 should be a persisted preference and an explicit UI state. It should not imply an unapproved filesystem watcher.
- `Sync now` must be preview-first and then execute with explicit confirmation when files/directories will be created or changed.

### Approval Package: Submit

- Submit is the approval-stage entry point.
- Submit requires human confirmation.
- Submit prerequisites should include:
  - local project folder exists,
  - basic function folders/files are present according to the accepted backend checker,
  - `public_folder_year` is resolved or explicitly confirmed,
  - Open working copy exists or is created through a confirmed preview,
  - sync preview has no unresolved conflict,
  - Closed target does not already exist,
  - no unmanaged public path conflict is detected.
- Submit v1 moves/archives the Open working copy into Closed as a safe placeholder.
- Submit v1 does not encrypt, compress, or mutate Windows permissions.
- Encryption, permissions, and package format rules are future scope.

### Approved Folder: Pull

- Pull source: `Closed/<public_folder_year>/<project_folder_name>`.
- Pull must be preview-first.
- Pull must never overwrite the current local project folder.
- Recommended v1 preservation strategy:
  - copy the Closed authoritative folder into a timestamped local approved-pull folder or sibling,
  - leave the existing local working folder untouched,
  - record the source Closed path and target local path in operation history.
- Any future canonical local replacement strategy must be a separate explicit decision.

## 5. `public_folder_year` Resolver Contract

Resolver order:

1. Local ConnLab LTR record:
   - prefer `registered_on.year`,
   - use `requested_date.year` only when accepted as the application/registration date source.
2. LTR Excel sheet:
   - read-only lookup of exact DL number,
   - use unambiguous four-digit sheet name only.
3. Project creation date:
   - use project `created_on.year`.
4. Human confirmation:
   - block preview until operator confirms year.

The resolver must return:

- resolved year
- source
- evidence text
- warnings
- whether human confirmation was required

It must not infer from the DL number year.

## 6. UI Acceptance Standards

- Folder Actions renders as a compact toolbar/action cluster.
- Default UI shows only operation controls:
  - `Open`
  - `Auto sync`
  - `Sync now`
  - `Submit`
  - `Pull`
- The UI must not persistently show:
  - target paths
  - file counts
  - last sync/submit/pull timestamps
  - Ready, Partial, Waiting, Not current, or similar readiness statuses
  - Source material as a separate card
  - public-drive preview item lists
- Short inline errors are allowed only for actionable blockers or operation failures.
- Copy must be terse and business-readable.
- Visual style remains restrained, dense, and operational.
- React must not contain filesystem business logic.

## 7. Backend File Operation Acceptance Standards

- All Sync, Submit, and Pull operations expose preview before execute.
- Execute revalidates the preview state or uses a short-lived preview token/snapshot.
- All resolved paths must stay inside the configured root.
- The configured public root itself is never silently created by product runtime.
- Missing subdirectories may be created only by explicit execute confirmation after preview.
- No silent overwrite, delete, or move of local or public files/folders.
- Submit may move only the ConnLab-managed Open working copy after confirmation.
- Pull must preserve existing local folders.
- Operation records capture:
  - operation type,
  - project id,
  - public root class,
  - resolved year and source,
  - source and target paths,
  - confirmation flags,
  - operator if available,
  - timestamp,
  - result status,
  - conflicts/errors,
  - relevant fingerprints or snapshot identifiers.

## 8. Recommended Lane Split

### TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT

- Owner: Planner/Reviewer
- Status: planned, ready for Reviewer plan gate
- Scope: this contract only

### TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS

- Owner: Frontend Developer after separate approval
- Scope: replace readiness/status UI with quiet toolbar and disabled/blocked contract states only
- Depends on: TASK_346A accepted

### TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND

- Owner: Backend Developer after separate approval
- Scope: resolver, Open/Closed path contract, sync/submit/pull preview/execute, operation records, tests
- Depends on: TASK_346A accepted

### TASK_346D_WORKBENCH_FOLDER_ACTIONS_FUNCTIONAL_WIRING

- Owner: Frontend Developer after separate approval
- Scope: typed API client and Workbench wiring to TASK_346C backend
- Depends on: TASK_346B and TASK_346C

### TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA

- Owner: QA/Integrator after separate approval
- Scope: temporary directory end-to-end smoke with local root and public root fixtures
- Depends on: TASK_346B/C/D

## 9. May Touch / Must Not Touch / Locked Paths

May Touch for TASK_346A:

- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `docs/task_board.md`

Must Not Touch:

- product backend code
- product frontend code
- tests
- real local/public folders
- LTR workbook files
- Matrix Editor logic
- Projects list implementation
- StepInstance, Report, AI, permissions, LAN/server, multi-user
- unrelated governance/orchestration residuals

Locked Paths:

- `backend/**`
- `frontend/**`
- `tests/**`
- real public-drive roots
- local project folders
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`

## 10. Validation Recommendations

Reviewer plan gate:

- Confirm contract consistency and scope locks.
- Confirm UI acceptance removes status/readiness-card behavior.
- Confirm public root strategy handles local development without unsafe public-drive writes.
- Confirm Submit/Sync/Pull are preview-first and explicit-confirmation based.

Future backend validation:

- Unit tests for root classifier, year resolver, path resolver, and operation state transitions.
- Integration tests with temp local root and temp public root.
- Conflict tests for unmanaged Open files, existing Closed target, missing root, ambiguous year, and pull local-folder preservation.

Future frontend validation:

- Focused Workbench component/model tests.
- Static scan against readiness/status labels in Folder Actions default UI.
- Frontend build.
- Browser smoke at Workbench widths used by ConnLab operators.

Future integration QA:

- Use temp directories to simulate:
  - `D:\Test Project`
  - `D:\PublicProject\Open\2026`
  - `D:\PublicProject\Closed\2026`
- Verify Sync creates/copies only under temp public root.
- Verify Submit locks Sync and moves/archives Open to Closed without encryption.
- Verify Pull preserves existing local folder and copies authoritative Closed folder to a new local target.

## 11. Stop Point

TASK_346A is ready for Reviewer plan gate only.

Do not route Developer implementation until:

- Reviewer plan gate passes,
- user explicitly approves a downstream implementation lane,
- that downstream lane has its own task file, plan, evidence, May Touch, Must Not Touch, Locked Paths, validation gate, and merge gate.
