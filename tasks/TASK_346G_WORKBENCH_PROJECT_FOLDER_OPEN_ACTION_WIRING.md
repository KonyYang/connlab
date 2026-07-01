# TASK_346G Workbench Project Folder Open Action Wiring

Status: complete/accepted after Developer implementation, Reviewer implementation gate, QA keyboard re-smoke, and Integrator packaging/readiness
Lane: workbench-project-folder-open-action-wiring
Owner Roles: Planner / Reviewer / Developer / QA / Integrator
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-07-01

## 1. Purpose

Create the formal planning-first lane to finish the `Project folder -> Open` action in the Workbench Folder Actions panel.

The accepted TASK_346D wiring connected Auto sync, Sync, Submit, and Pull to the new public-folder workflow, but the `Project folder` row still has `actionTarget: null` and remains a placeholder even when `publicFolderWorkflowContext.local_official_folder_path` is available.

TASK_346G plans the missing Open action without changing Sync/Submit/Pull file movement, public folder year resolution, LTR workbook authority, Projects registry, Matrix Editor, or future-scope features.

## 2. User / Repository Facts

Confirmed by user/Orchestrator investigation:

- User project URL: `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
- Local folder exists at `D:\Test Project\DL-2026-05-011`.
- Backend public-folder workflow context returns the deeper local official folder path:
  `D:\Test Project\DL-2026-05-011\DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing`.
- That deeper path exists locally.
- Project API status is `ltr_registered`.
- Legacy `/folder/latest` returns 404, so the old folder-record path is not a reliable source for this fixture.

Confirmed by repository evidence:

- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts` hard-codes the `Project folder` row with `actionTarget: null`.
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` still derives `folderReady` from old project status / official workspace preview logic, not from `publicFolderWorkflowContext.local_official_folder_path`.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` maps `actionTarget === "folder"` to create/update project folder, not to open an existing folder.
- No existing backend/frontend `open folder` or Explorer bridge was found by code search.
- `frontend/src/api/client.ts` already exposes `local_official_folder_path` fields from TASK_346C/D DTOs.

## 3. Scope Decision

TASK_346G should be a narrow Workbench Open-action wiring lane.

Implementation should prefer this behavior:

1. Use `publicFolderWorkflowContext.local_official_folder_path` as the primary local folder availability fact.
2. Enable `Project folder -> Open` when a local official folder path is present and no lifecycle readonly policy blocks the surface.
3. In browser/local-server mode, call a small safe backend open-folder bridge only if available.
4. If the bridge is unavailable or blocked, copy the path to clipboard and show short operator copy.
5. If clipboard is unavailable, show the folder path as a short actionable message.

Planner explicitly permits a tiny safe backend/desktop open-folder bridge inside this lane only if the implementation keeps it non-mutating:

- validate path exists and is a directory;
- resolve the path from backend-owned project context, not arbitrary user input;
- open the folder through a local Windows gateway;
- do not create, move, delete, copy, overwrite, sync, submit, pull, or inspect file contents.

## 4. May Touch

Future Developer implementation may touch only these product paths:

- `frontend/src/api/client.ts` for a typed open-local-project-folder helper only
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` only if needed to pass the open action through the accepted Folder Actions surface
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only if needed for no-Matrix Workbench Folder Actions parity
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts` only if needed to expose the already-loaded local folder path/action state
- `frontend/src/workbench.css` only for concise feedback styling if existing styles are insufficient

Tiny backend bridge May Touch, only if Reviewer accepts it as necessary:

- `backend/api/routes_folder.py` or a narrowly named project-folder access route module
- `backend/api/main.py` only if a new route module must be included
- `backend/api/dependencies.py` only for the narrow open-folder service dependency
- `backend/application/project_folder_open_service.py` or equivalent narrow application service
- `backend/infrastructure/files/local_folder_open_gateway.py` or equivalent Windows gateway
- focused backend tests under `tests/unit/` and `tests/integration/`

Governance/evidence May Touch:

- `tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md`
- `docs/task_346g_workbench_project_folder_open_action_wiring_plan.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md`
- future `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`
- future `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_qa.md`
- `docs/task_board.md` through normal lane flow

## 5. Must Not Touch / Locked Paths

Must Not Touch:

- Sync/Submit/Pull workflow semantics or file movement
- public folder year resolver
- public Open/Closed path resolver
- public-drive LTR workbook authority writes
- real folder create/move/delete/copy/overwrite
- Projects registry/list
- Matrix Editor business logic
- StepInstance, Report, AI, permissions, LAN/server, multi-user
- unrelated Settings/LTR helper residuals
- release/packaging residuals
- `temp_agents_stash.md`
- `.agents/**`
- `docs/project_management/**`

Locked paths:

- real `D:\Test Project/**` and `D:\PublicProject/**`
- real public-drive folders
- real LTR workbook files
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `backend/application/public_folder_year_resolver.py`
- `backend/application/public_folder_path_resolver.py`
- `backend/application/public_folder_workflow_service.py` unless a Reviewer-approved read-only helper call is needed without changing workflow semantics
- `backend/infrastructure/files/public_folder_workflow_gateway.py`
- release paths: `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts/tests/tasks/docs

## 6. Expected UX Behavior

When a local official folder path exists:

- `Project folder` row context should show a concise path fragment or `Local folder available`.
- Button label remains `Open`.
- Clicking `Open` should first try the safe local open behavior if implemented and available.
- Browser fallback copy:
  - success copy: `Project folder path copied. Open it in File Explorer.`
  - bridge blocked: show the backend's short blocker and keep the path available.
  - clipboard unavailable: show `Copy this path from the folder context.`

When no local official folder path exists:

- `Open` remains disabled.
- Short blocker: `Project folder is not available yet.`

Do not add long instructions, readiness/status cards, old public-drive copy, or source-material cards.

## 7. Validation Gate

Reviewer plan gate must confirm:

- the lane is the correct follow-up after TASK_346D/E;
- `local_official_folder_path` is the primary fact source for existing folder availability;
- the tiny backend bridge boundary is non-mutating if included;
- no Sync/Submit/Pull, resolver, real folder mutation, public-drive authority, Projects registry, Matrix Editor, release, or Settings/LTR residual scope is included.

Future Developer validation should include:

- focused selector tests proving `Project folder -> Open` enables from `local_official_folder_path`;
- component tests proving the Open button calls the new action target and fallback copy/message behavior is accessible;
- model/layout tests for bridge success, bridge blocker, clipboard fallback, missing path, readonly behavior, and no-Matrix parity if touched;
- backend service/API tests only if the tiny bridge is implemented, with gateway mocked and temp paths only;
- `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run`;
- `npm run build`;
- backend focused tests if backend bridge files are touched;
- static no-real-folder-mutation scan;
- forbidden-scope status checks.

Browser/manual smoke:

- Open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
- Confirm `Project folder -> Open` is enabled when `local_official_folder_path` exists.
- In browser/local-server mode, confirm Explorer opens through the safe bridge or the path is copied/shown with the short fallback message.
- Confirm Sync/Submit/Pull behavior is unchanged.

## 8. Merge Gate

Future acceptance requires:

- Reviewer plan gate pass.
- User approval before Developer implementation.
- Developer evidence and focused validation.
- Reviewer implementation gate.
- QA/browser smoke if routed.
- Integrator packaging/readiness.
- Package checks proving no real folder mutation, no resolver changes, no Sync/Submit/Pull semantic changes, no LTR workbook/public-drive authority writes, no release residuals, no `.agents/**`, and no `docs/project_management/**`.

Remote push is not authorized by this lane.

## 9. Current Stop Point

TASK_346G is complete/accepted after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness gate passed.
- User approved `TASK_346G` reconciliation and Developer implementation.
- Developer implementation and fix passes completed.
- Reviewer implementation re-gate passed.
- QA live in-app browser keyboard re-smoke passed.
- Integrator packaging/readiness accepted.

Accepted outcome:

- `Project folder -> Open` is enabled from the backend-resolved local official folder path.
- Open uses the non-mutating `open-local` bridge and keeps fallback copy/path messaging.
- Pointer click, semantic click, Enter, and Space each trigger one open request in QA smoke.
- Sync, Submit, Pull, old create/update folder actions, public-folder resolvers, real folder mutation, LTR/public-drive authority writes, Projects registry, Matrix Editor, and future scope remain unchanged.

Current stop point: Integrator accepted. Remote push is not authorized by this lane.
