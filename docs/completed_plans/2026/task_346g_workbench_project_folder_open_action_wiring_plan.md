# TASK_346G Workbench Project Folder Open Action Wiring Plan

Status: complete/accepted after Developer implementation, Reviewer implementation gate, QA keyboard re-smoke, and Integrator packaging/readiness
Task: `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`
Lane: `workbench-project-folder-open-action-wiring`
Date: 2026-07-01
Owner Roles: Planner / Reviewer / Developer / QA / Integrator

## 1. Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`.
- Current lane: `workbench-project-folder-open-action-wiring`.
- Current role: Developer planning-first.
- Allowed reason: TASK_346A/B/F/C/D/E are complete/accepted, Reviewer plan gate passed, and Orchestrator/User approved Developer planning-first for this lane.
- Developer planning-first stop point: Reviewer implementation-readiness gate. That gate has since passed; section 12 is the current source-of-truth authorizing Developer implementation after user approval.

## 2. Discovery Gate

Confirmed by user / Orchestrator:

- The user opened Workbench project `72fbbfa290294da9a507344b68ff900f`.
- The local project folder exists under `D:\Test Project\DL-2026-05-011`.
- The backend public-folder workflow context returns the deeper existing local official folder path:
  `D:\Test Project\DL-2026-05-011\DL-2026-05-011 Coolpower HDF 3.40mm pin Qualification Testing`.
- The legacy `/folder/latest` endpoint returns 404 for this project.
- The user agreed to start the recommended follow-up, but this delegated Planner pass must create a planning-first lane only.

Confirmed by repository evidence:

- `docs/task_board.md` shows no active implementation lane after `TASK_346E_FOLDER_WORKFLOW_INTEGRATION_QA` complete/accepted.
- `TASK_346B` and `TASK_346F` accepted the Folder Actions UI surface.
- `TASK_346C` accepted the public-folder workflow context that includes `local_official_folder_path`.
- `TASK_346D` accepted Sync/Submit/Pull frontend wiring but left `Project folder -> Open` as a placeholder.
- `projectFolderTaskSelectors.ts` hard-codes the Project folder row as `actionTarget: null`.
- `useProjectWorkbenchModel.ts` derives `folderReady` from old status/preview logic rather than the accepted public-folder workflow context.
- `ProjectWorkbenchLayout.tsx` still routes `actionTarget === "folder"` to create/update project folder.
- Code search found no existing safe open-folder bridge or Explorer launcher.

Inferred by Planner:

- This is a narrow follow-up lane, not a reopening of TASK_346D.
- A browser-only implementation can enable the button and copy/show the path, but a true `Open` action in the local browser release likely needs a tiny backend/desktop bridge.
- The bridge can be safely contained if it validates an existing backend-resolved directory and performs no write operation.

Not yet confirmed:

- Whether Reviewer/user prefer bridge-first or copy-path-only implementation. This does not block creating a planned lane because the plan explicitly supports both and requires Reviewer/user gates before implementation.

Planning risk:

- If this is patched inside TASK_346D or done ad hoc, it can mix with unrelated `frontend/src/api/client.ts` Settings/LTR residuals or accidentally change Sync/Submit/Pull behavior.
- If the lane allows arbitrary path input, it could become an unsafe local file launcher. The lane therefore requires backend-resolved paths only.

Questions: none before Reviewer plan gate.

Recommendation: create TASK_346G as a planned lane, then route Reviewer plan gate.

## 3. Implementation Shape

The accepted implementation should be a small vertical slice:

1. Selector/model:
   - derive folder availability from `publicFolderWorkflowContext.local_official_folder_path`;
   - give the Project folder row a distinct action target such as `project_folder_open`;
   - keep create/update folder action separate from open existing folder action.
2. Frontend handler:
   - handle `project_folder_open` separately from `folder` create/update;
   - try backend open helper if implemented;
   - fall back to copying the path to clipboard;
   - show a short message when copied, blocked, missing, or unsupported.
3. Optional tiny backend bridge:
   - endpoint receives project id only, not an arbitrary path;
   - service resolves the same local official folder path used by `public-folder-workflow/context`;
   - gateway validates `exists && is_dir`;
   - Windows/local launch is isolated behind infrastructure;
   - tests mock the launch gateway and use temp paths.

Do not use `file://` links as the primary solution because browser handling is inconsistent and can expose path behavior outside the accepted API boundary.

## 4. Browser Mode vs Desktop Mode

Browser/local-server mode:

- Primary safe behavior: API bridge if available, otherwise clipboard fallback.
- User-facing fallback copy: `Project folder path copied. Open it in File Explorer.`
- If clipboard is unavailable: show the path and `Copy this path from the folder context.`

Desktop/local shell mode:

- The same backend bridge may open Explorer because the server runs on the operator workstation.
- The bridge must remain local, non-mutating, and project-context-resolved.

No LAN/server, remote filesystem, permissions, or multi-user semantics are included.

## 5. May Touch

Frontend May Touch:

- `frontend/src/api/client.ts` for the narrow open-local-project-folder helper only
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` only if needed for action propagation
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only if needed for no-Matrix parity
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts` only if needed for model propagation
- `frontend/src/workbench.css` only if needed for existing short feedback style

Backend tiny bridge May Touch if accepted by Reviewer:

- `backend/api/routes_folder.py` or a narrow project-folder access route module
- `backend/api/main.py` only if a new route module is needed
- `backend/api/dependencies.py` only for narrow service dependency wiring
- `backend/application/project_folder_open_service.py` or equivalent
- `backend/infrastructure/files/local_folder_open_gateway.py` or equivalent
- focused backend tests under `tests/unit/` and `tests/integration/`

Docs/evidence May Touch:

- `tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md`
- `docs/task_346g_workbench_project_folder_open_action_wiring_plan.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md`
- future Developer/QA evidence for this lane
- `docs/task_board.md` through normal lane flow

## 6. Must Not Touch / Locked Paths

Must Not Touch:

- Sync/Submit/Pull workflow behavior
- `public_folder_year` resolver
- Open/Closed public path resolver
- real folder create/move/delete/copy/overwrite
- public-drive LTR workbook authority writes
- Projects registry/list
- Matrix Editor business logic
- StepInstance, Report, AI, permissions, LAN/server, multi-user
- Settings/LTR helper residuals
- release/packaging residuals
- `temp_agents_stash.md`

Locked Paths:

- real `D:\Test Project/**`
- real `D:\PublicProject/**`
- real public-drive folders
- real local project folders
- real LTR workbook files
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `backend/application/public_folder_year_resolver.py`
- `backend/application/public_folder_path_resolver.py`
- `backend/application/public_folder_workflow_service.py` unless Reviewer explicitly permits a read-only reuse call with no workflow semantic change
- `backend/infrastructure/files/public_folder_workflow_gateway.py`
- `.agents/**`
- `docs/project_management/**`
- `docs/packaging_notes.md`
- `pyproject.toml`
- `backend/desktop/**`
- `dist_release/**`
- `packaging/**`
- release scripts/tests/tasks/docs
- `temp_agents_stash.md`

## 7. UX Acceptance Criteria

- `Project folder -> Open` is enabled when `publicFolderWorkflowContext.local_official_folder_path` is present and lifecycle policy does not block the surface.
- The row uses concise copy:
  - available: `Local folder available.`
  - copied fallback: `Project folder path copied. Open it in File Explorer.`
  - unavailable: `Project folder is not available yet.`
- Button remains labeled `Open`.
- Missing path keeps the button disabled with a short blocker.
- Browser mode does not silently fail.
- Sync, Submit, Pull, Auto sync, and their confirmation flows are unchanged.
- The UI remains the accepted compact Folder Actions panel, not a readiness/status dashboard.

## 8. Validation Plan

Future Developer validation:

- `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run`
- `npm run build`
- selector tests:
  - enables `Project folder -> Open` from `local_official_folder_path`;
  - disables it when missing;
  - does not route to create/update folder action.
- component/model/layout tests:
  - click calls the new open action target;
  - bridge success shows a short success message;
  - bridge blocker shows a short blocker;
  - clipboard fallback succeeds;
  - clipboard unavailable path is visible;
  - readonly lifecycle behavior remains respected;
  - no-Matrix surface parity if touched.
- backend tests only if bridge implemented:
  - service resolves project context path, not arbitrary path input;
  - missing path / non-directory blocks;
  - gateway is mocked and no real Explorer process is required;
  - route returns typed success/blocker response.
- static scans:
  - no real folder create/move/delete/copy/overwrite;
  - no `D:\Test Project` or `D:\PublicProject` production literals;
  - no Sync/Submit/Pull semantic diff;
  - forbidden-scope status.

Browser/manual smoke:

- open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`;
- verify `Project folder -> Open` is enabled from the backend context path;
- click `Open`;
- observe Explorer open through bridge or the path copied/shown with short fallback;
- confirm Sync/Submit/Pull remain unchanged.

## 9. Merge Gate

Future acceptance requires:

- Reviewer plan gate pass.
- Explicit user approval before Developer implementation.
- Developer evidence with tests/build and static scans.
- Reviewer implementation gate.
- QA/browser smoke if routed.
- Integrator packaging/readiness.
- Package excludes unrelated Settings/LTR/release residuals and all locked paths.

Remote push is not authorized.

## 10. Developer Planning-First Historical Stop Point

Developer planning-first confirmed the lane was implementable as a narrow Workbench open-action slice and stopped at Reviewer implementation-readiness gate.

This gate has since passed. See section 12 for the current implementation authorization source-of-truth.

## 11. Developer Planning-First Refinement

Developer read the current Workbench code, TASK_346C/D accepted contracts, and current dirty status after Reviewer plan gate passed.

### Implementation strategy

Recommended implementation is bridge-first with browser-safe fallback:

1. Add a tiny non-mutating backend open bridge.
2. Frontend enables `Project folder -> Open` from `publicFolderWorkflowContext.local_official_folder_path`.
3. Frontend uses a distinct action target, `project_folder_open`, so the existing `folder` create/update target keeps its current meaning.
4. On click, frontend calls the backend bridge.
5. If the bridge is unavailable, unsupported, or blocked, frontend falls back to copying the already-returned local official folder path to the clipboard.
6. If clipboard is unavailable, frontend shows the path in the existing short feedback area.

This avoids reviving the legacy `/folder/latest` dependency and avoids treating a browser `file://` link as a reliable product action.

### Backend bridge contract

The backend bridge must be project-id-only:

- route receives `project_id` only, with no arbitrary path request body;
- application service resolves the path from accepted project context, preferably via the existing public folder workflow context `local_official_folder_path`;
- if the workflow context has no local official folder path, return a typed blocked response;
- gateway validates the resolved path exists and is a directory immediately before opening;
- gateway opens the directory through local Windows/desktop infrastructure only;
- no create, move, delete, copy, overwrite, sync, submit, pull, file enumeration, file content read, public-folder-year resolver change, public Open/Closed resolver change, or LTR workbook authority write is allowed;
- tests must mock the gateway and use temporary directories only.

Suggested route shape:

- `POST /api/projects/{project_id}/folder/open-local`

Suggested response shape:

- `project_id: string`
- `status: "opened" | "blocked" | "unsupported"`
- `message: string`
- `local_official_folder_path: string | null`

The response may include the backend-resolved path because the frontend already receives the same path through `public-folder-workflow/context`; it must not echo user-supplied paths.

### Frontend model and selector changes

Use `publicFolderWorkflowContext.local_official_folder_path` as the source of truth for the Project folder row:

- available path -> context `Local folder available.`, action label `Open`, action target `project_folder_open`;
- missing path -> disabled button, blocker `Project folder is not available yet.`;
- lifecycle readonly must not block a read/open action, but any backend bridge blocker should still be displayed;
- Basic Information / Required Forms blockers must not block Open, because Open is a read/navigation action, not a folder-generation write.

`folderReady` may remain as legacy create/update readiness for other surfaces, but Folder Actions `Project folder -> Open` should not depend on old `project.status === "folder_created"`, `officialWorkspacePreview.status === "completed"`, or `/folder/latest`.

### Future exact May Touch

Frontend:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.test.tsx`
- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` only if the existing active-Matrix Folder Actions surface needs propagation
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only if no-Matrix parity needs propagation
- `frontend/src/workbench.css` only if existing short feedback styles are insufficient

Backend bridge:

- `backend/api/routes_folder.py`
- `backend/api/dependencies.py` only for a narrow open service dependency
- `backend/application/project_folder_open_service.py`
- `backend/infrastructure/files/local_folder_open_gateway.py`
- focused backend tests under `tests/unit/` and `tests/integration/`

`backend/api/main.py` should not need changes if the route is added to the existing `routes_folder.py` router. If implementation proves otherwise, record the reason before touching it.

Docs/evidence:

- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`

### Locked paths preserved

Implementation must still exclude:

- Sync/Submit/Pull semantics and DTO behavior except unaffected shared compile fallout;
- `backend/application/public_folder_year_resolver.py`;
- `backend/application/public_folder_path_resolver.py`;
- `backend/application/public_folder_workflow_service.py` unless a read-only context call is unavoidable and does not change semantics;
- `backend/infrastructure/files/public_folder_workflow_gateway.py`;
- real `D:\Test Project/**`, `D:\PublicProject/**`, public-drive folders, and real LTR workbook files;
- Settings/LTR helper residuals, release/packaging residuals, `temp_agents_stash.md`, `.agents/**`, and `docs/project_management/**`.

### Validation additions

Developer implementation should run:

- `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run`
- `npm run build`
- focused backend tests for the open service/API/gateway with mocked launcher and temp directories
- `git diff --check` on the TASK_346G package
- trailing whitespace scan
- static no-real-folder-mutation scan for create/move/delete/copy/overwrite and real path literals
- scan proving `Project folder -> Open` does not call the old `folder` create/update action target
- forbidden-scope status excluding Settings/LTR/release residuals

Browser smoke should open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`, verify `Project folder -> Open` is enabled from workflow context, click `Open`, and observe either Explorer launch through the bridge or the short clipboard/path fallback message.

## 12. Planner Reconciliation

Planner reconciliation aligned repository source-of-truth after:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness gate passed.
- User approved `TASK_346G` reconciliation and Developer implementation.

## 13. Integrator Closeout

Status: complete/accepted.

Integrator packaging/readiness accepted TASK_346G after Developer implementation/fix passes, Reviewer implementation re-gate, and QA live in-app browser keyboard re-smoke.

Accepted package:

- narrow backend `open-local` project-folder bridge;
- Workbench Folder Actions Open wiring, fallback messaging, focused tests, and minimal z-index hit-test fix;
- TASK_346G task/plan/planner/developer/reconciliation/QA evidence and QA artifacts;
- `docs/task_board.md` TASK_346G closeout only.

Validation summary:

- focused frontend Workbench suite passed: `4` files / `65` tests;
- focused backend open bridge suite passed: `5` tests;
- frontend build passed with the existing Vite chunk-size warning only;
- backend `py_compile` passed for the TASK_346G bridge files;
- QA browser keyboard re-smoke passed for pointer click, semantic click, Enter, and Space with no double trigger;
- package diff, whitespace, staged whitelist, forbidden-path, and no-real-folder mutation checks passed.

Remote push was intentionally not performed.
