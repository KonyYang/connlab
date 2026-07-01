# TASK_346G Workbench Project Folder Open Action Wiring - Developer Evidence

Status: implementation complete - Reviewer/QA passed - Integrator accepted
Date: 2026-07-01
Role: Developer
Task: `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`
Lane: `workbench-project-folder-open-action-wiring`

## 1. Current Phase / Task / Lane

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Current task: `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING`.
- Current lane: `workbench-project-folder-open-action-wiring`.
- Current role: Developer planning-first.
- Allowed reason: Reviewer plan gate passed and user approved Developer planning-first. This pass is docs/evidence only.
- Stop point: Reviewer implementation-readiness gate.

## 2. Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product context through `node .agents/skills/impeccable/scripts/load-context.mjs`
- `$impeccable` product reference
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `tasks/TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING.md`
- `docs/task_346g_workbench_project_folder_open_action_wiring_plan.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_planner.md`
- current Workbench Folder Actions code and tests by read-only inspection
- `frontend/src/api/client.ts`
- `backend/api/routes_public_folder_workflow.py`
- `backend/application/public_folder_workflow_service.py`
- `backend/api/routes_folder.py`
- `backend/api/dependencies.py`
- current `git status --short`

## 3. Read-Only Code Findings

Repository facts match the Reviewer-verified root cause:

- `PublicFolderWorkflowContext.local_official_folder_path` exists in the frontend DTO.
- `projectFolderTaskSelectors.ts` still sets the `Project folder` row `actionTarget` to `null`.
- `useProjectWorkbenchModel.ts` still loads legacy `getLatestProjectFolder(...)` and stores `latestProjectFolderPath` from `/folder/latest`.
- `ProjectWorkbenchLayout.tsx` routes `actionTarget === "folder"` to `handleProjectFolderCreateClick()`, so `folder` cannot safely mean Open.
- `ProjectFolderTaskList.tsx` already renders a single row action button and can call a distinct action target.
- `useProjectRuntimeConsoleModel.ts` already bridges public-folder workflow context and handlers from the model into the Workbench layout.
- Code search found Settings path picker support, but no existing safe open-folder or Explorer bridge.

## 4. Implementation Strategy Decision

Developer recommends a bridge-first implementation with browser-safe fallback.

Reasoning:

- A real `Open` action on Windows needs local shell behavior. A frontend-only implementation can only copy or display the path in normal browser mode.
- Browser `file://` links are unreliable and would expose local path behavior outside the accepted API boundary.
- A tiny backend bridge can keep the request project-id-only, backend-resolved, existing-directory-only, and non-mutating.
- Frontend fallback still protects browser/dev mode when the bridge is unavailable or blocked.

Chosen strategy:

1. Add a distinct `project_folder_open` action target.
2. Derive availability from `publicFolderWorkflowContext.local_official_folder_path`.
3. Add a typed frontend helper for a project-id-only open endpoint.
4. Add a narrow backend service and gateway to open only the backend-resolved local official folder.
5. Fall back to clipboard/path display when bridge behavior is unavailable or blocked.

## 5. Backend Bridge Safety Contract

Future implementation may add `POST /api/projects/{project_id}/folder/open-local`.

Safety requirements:

- route accepts `project_id` only;
- no arbitrary path request body;
- service resolves the local official folder from accepted project context, preferably the existing public-folder workflow context path;
- gateway validates `exists` and `is_dir` immediately before opening;
- gateway is mocked in tests;
- no create, move, delete, copy, overwrite, sync, submit, pull, file listing, file content read, year resolver change, Open/Closed path resolver change, or LTR workbook authority write;
- response is typed and browser-safe: `opened`, `blocked`, or `unsupported` with concise message and the backend-resolved path if available.

## 6. Frontend Behavior Contract

- `Project folder` row context when available: `Local folder available.`
- Button label remains `Open`.
- Available path sets `actionTarget: "project_folder_open"`.
- Missing path keeps Open disabled with `Project folder is not available yet.`
- Bridge success shows concise success feedback.
- Bridge blocker shows backend blocker without raw stack traces.
- Bridge unavailable falls back to clipboard copy.
- Clipboard unavailable shows the already-known context path and short copy.
- Existing `folder` action target remains create/update only.
- Sync, Submit, Pull, Auto sync, and their confirmation flows remain unchanged.
- Folder Actions remains the accepted compact contextual panel.

## 7. Future Implementation File List

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
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx` only if action propagation requires it
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only if no-Matrix parity requires it
- `frontend/src/workbench.css` only if existing feedback styles are insufficient

Backend bridge:

- `backend/api/routes_folder.py`
- `backend/api/dependencies.py` only if a narrow service dependency is needed
- `backend/application/project_folder_open_service.py`
- `backend/infrastructure/files/local_folder_open_gateway.py`
- focused backend tests under `tests/unit/` and `tests/integration/`

Docs/evidence:

- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`

`backend/api/main.py` should remain untouched if the existing folder router can host the endpoint.

## 8. Locked Scope

Implementation must not touch:

- Sync/Submit/Pull workflow semantics;
- public folder year resolver;
- public Open/Closed path resolver;
- real folder create, move, delete, copy, overwrite;
- real `D:\Test Project/**`, `D:\PublicProject/**`, public-drive folders, or LTR workbook files;
- LTR workbook or public-drive authority writes;
- Projects registry/list;
- Matrix Editor business logic;
- StepInstance, Report, AI, permissions, LAN/server, multi-user;
- Settings/LTR helper residuals;
- release/packaging residuals;
- `temp_agents_stash.md`;
- `.agents/**`;
- `docs/project_management/**`.

## 9. Existing Dirty Residuals

Current status includes unrelated residuals outside this planning pass:

- Settings/LTR helper residuals in frontend/backend settings files;
- release/packaging residuals such as `docs/packaging_notes.md`, `pyproject.toml`, `backend/desktop/**`, `dist_release/**`, `packaging/**`, release scripts/tests, and release task docs;
- intake/parser/Office gateway test residuals;
- `temp_agents_stash.md`;
- Planner-created TASK_346G task/plan/planner evidence and board updates.

This Developer planning-first pass modified only:

- `docs/task_346g_workbench_project_folder_open_action_wiring_plan.md`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`

## 10. Validation Plan For Implementation

Future implementation should run:

- `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run`
- `npm run build`
- focused backend tests for the open service/API/gateway if backend bridge is implemented
- `git diff --check` for the TASK_346G package
- trailing whitespace scan
- static no-real-folder-mutation scan
- scan proving `project_folder_open` does not call the old `folder` create/update target
- forbidden-scope status excluding external residuals

Browser smoke:

- open `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`;
- confirm `Project folder -> Open` is enabled from `local_official_folder_path`;
- click `Open`;
- verify Explorer opens through the bridge or the clipboard/path fallback message appears;
- confirm Sync, Submit, Pull, and Auto sync behavior is unchanged.

## 11. Planning Validation

Completed:

- required TASK_346G task, plan, and planner evidence files exist;
- Developer evidence created;
- `git diff --check -- docs/task_346g_workbench_project_folder_open_action_wiring_plan.md docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md` passed;
- trailing whitespace scan on the TASK_346G plan/evidence returned no matches;
- targeted status confirms no product source, backend implementation, frontend implementation, tests, `.agents/**`, `docs/project_management/**`, Settings/LTR residuals, release residuals, real folders, or `temp_agents_stash.md` were changed by this planning-first pass.

## 12. Stop Point

Developer planning-first gate: complete.

Recommended next role: Reviewer implementation-readiness gate.

Do not start implementation until the next approved gate.

## 13. Developer Implementation Pass

Status: implementation complete - pending Reviewer implementation gate.

Implementation summary:

- Added a narrow backend `open-local` bridge under the existing folder API route. The endpoint accepts only `project_id`; it does not accept arbitrary local paths.
- Added `ProjectFolderOpenService` to resolve the trusted local folder path from the accepted public-folder workflow context.
- Added `LocalFolderOpenGateway` to open only an existing directory and return `opened`, `blocked`, or `unsupported`.
- Added `openLocalProjectFolder(...)` frontend API helper and `ProjectFolderOpenResponse` DTO.
- Changed Folder Actions `Project folder` row to derive Open availability from `PublicFolderWorkflowContext.local_official_folder_path`.
- Added distinct `project_folder_open` action target so Open no longer reuses the old `folder` create/update target.
- Wired `project_folder_open` through the Workbench layout/model/runtime bridge to the backend helper.
- Added browser-safe fallback copy: if the bridge is unavailable or blocked but a trusted context path exists, the UI reports path-copy or path-display guidance instead of failing silently.
- Preserved Sync, Submit, Pull, Auto sync, old create/update folder behavior, Matrix Editor behavior, and Projects registry behavior.

Changed TASK_346G files:

- `backend/api/routes_folder.py`
- `backend/api/dependencies.py`
- `backend/application/project_folder_open_service.py`
- `backend/infrastructure/files/local_folder_open_gateway.py`
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
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `tests/unit/test_project_folder_open_service.py`
- `tests/unit/test_local_folder_open_gateway.py`
- `tests/integration/test_project_folder_open_api.py`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`

Files intentionally not touched:

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`
- `backend/api/main.py`
- `docs/task_board.md`
- locked Settings/LTR, release/packaging, Projects registry, Matrix Editor, real folder, `.agents/**`, and `docs/project_management/**` paths.

Pre-existing dirty residuals:

- The worktree still contains unrelated Settings/LTR, release/packaging, intake/parser, Office gateway, board, and release-task residuals. They were not cleaned, staged, or packaged for this pass.
- `frontend/src/api/client.ts` already contains unrelated LTR workbook password/settings diff in the same file. TASK_346G's client hunk is limited to `ProjectFolderOpenResponse` and `openLocalProjectFolder(...)`.

Validation completed:

- Red tests before implementation:
  - `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run` failed before wiring.
  - `py -m pytest tests\unit\test_project_folder_open_service.py -q` failed before the service existed.
- Focused frontend tests:
  - `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run` passed: 4 files, 63 tests.
- Focused backend tests:
  - `py -m pytest tests\unit\test_project_folder_open_service.py tests\unit\test_local_folder_open_gateway.py tests\integration\test_project_folder_open_api.py -q` passed: 5 tests.
- Python compile:
  - `py -m py_compile backend\application\project_folder_open_service.py backend\infrastructure\files\local_folder_open_gateway.py backend\api\routes_folder.py backend\api\dependencies.py` passed.
- Frontend build:
  - `npm run build` passed. Vite reported the existing chunk-size warning only.
- Diff and whitespace:
  - `git diff --check` on the TASK_346G tracked package passed with LF/CRLF warnings only.
  - trailing whitespace scan on package files returned no matches.
- Static scope scans:
  - `project_folder_open` is distinct from `actionTarget === "folder"` and routes to `onOpenLocalProjectFolder()`.
  - production scan found no TASK_346G writes to real `D:\Test Project` or `D:\PublicProject` paths.
  - scan hits in `backend/api/dependencies.py` are pre-existing dependency code and not TASK_346G open-bridge file operations.
  - targeted forbidden-scope status showed only known external release/packaging residuals.

Browser smoke:

- Attempted Playwright smoke against `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f`.
- Tooling blocker: Playwright package is present, but the local Chromium headless executable is not installed at `C:\Users\White\AppData\Local\ms-playwright\chromium_headless_shell-1200\chrome-headless-shell-win64\chrome-headless-shell.exe`.
- No browser smoke was completed in this Developer thread. QA should re-smoke the live in-app browser and verify `Project folder -> Open` is enabled when `local_official_folder_path` is present, then verify Explorer opens or the path-copy fallback appears without console errors.

Residual risk:

- Actual Windows Explorer launch is intentionally delegated to QA/browser smoke because automated headless browser tooling is unavailable here.
- Backend unit and API tests verify the bridge accepts project id only, resolves through service context, blocks missing directories, and never creates or mutates files.

Stop point:

- Developer implementation pass complete.
- Recommended next role: Reviewer implementation gate.

## 14. Developer Fix Pass - QA B1 Live Browser Smoke

Status: fix pass complete - pending Reviewer implementation re-gate / QA re-smoke.

QA blocker handled:

- Live in-app browser smoke found `Project folder -> Open` enabled with `Local folder available.`, but pointer hit-test at the Open button center resolved to Matrix/close-confirmation text `Current`.
- Pointer click, semantic locator click, and keyboard Enter did not trigger `POST /folder/open-local` and did not show fallback copy.

Root cause:

- The Open action wiring and enabled state were present, but the compact lifecycle close confirmation is a sticky bottom panel with `z-index: 5`.
- When the close confirmation was expanded, it occupied the same viewport area as the right-rail Folder Actions surface during scroll. The Folder Actions side column did not establish a higher stacking layer, so the sticky confirmation content intercepted pointer hit-testing over the visible Open button area.
- This is a layout/hit-test bug, not a backend bridge or API-client contract bug.

Fix summary:

- Added a stable stacking context to `.runtime-console-side-column` so the right-rail operation controls remain the actionable layer above the compact sticky lifecycle panel.
- Added a focused regression test proving `Project folder -> Open` still invokes `onOpenLocalProjectFolder` while the inline Close confirmation is expanded, and still does not trigger the old create/update folder path.
- No Sync, Submit, Pull, Auto sync, backend bridge, public-folder resolver, Matrix Editor, Projects registry, real folder, or LTR/public-drive authority behavior was changed.

Fix-pass changed files:

- `frontend/src/workbench.css`
  - TASK_346G fix-pass addition only: `.runtime-console-side-column` now has `position: relative` and `z-index: 6`, one layer above the compact lifecycle panel's `z-index: 5`.
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
  - TASK_346G fix-pass addition only: close-confirmation-expanded Open regression.
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`

Pre-existing dirty context:

- `ProjectWorkbenchLayout.test.tsx` already contained TASK_346G implementation-pass changes before this fix pass, including the base Open routing test and public-folder workflow context fixture fields.
- `frontend/src/workbench.css` was newly touched by this fix pass to address QA B1.
- Existing backend, Settings/LTR, release/packaging, board, `.agents`, and governance residuals remain outside this fix pass and were not cleaned, staged, or packaged.

Validation completed:

- Focused frontend tests:
  - `npm test -- ProjectFolderTaskList projectFolderTaskSelectors ProjectWorkbenchLayout --run` passed: 3 files, 54 tests.
- Focused backend open bridge tests:
  - `py -m pytest tests\unit\test_project_folder_open_service.py tests\unit\test_local_folder_open_gateway.py tests\integration\test_project_folder_open_api.py -q` passed: 5 tests.
- Frontend build:
  - `npm run build` passed with the existing Vite chunk-size warning only.
- Diff and whitespace:
  - `git diff --check -- frontend/src/workbench.css frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md` passed with LF/CRLF warnings only.
  - Because the Developer evidence file is still untracked from earlier TASK_346G packaging, `git diff --check --no-index` against a temporary empty file was also run on the evidence file and passed with LF/CRLF warnings only.
  - trailing whitespace scan on the fix-pass files returned no matches.
- Static scans:
  - `project_folder_open` remains distinct from the old `actionTarget === "folder"` create/update path.
  - no-real-folder mutation scan on TASK_346G open-bridge package files returned no matches for real `D:\Test Project` / `D:\PublicProject` mutation patterns.
  - UI anti-pattern scan on `workbench.css` found existing gradients and an existing thick `border-left` outside this fix-pass hunk; this pass added only `position: relative` and `z-index: 6` to `.runtime-console-side-column`.
- Forbidden-scope status:
  - fix-pass product edits are limited to `frontend/src/workbench.css` and `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`.
  - targeted status still shows pre-existing backend/API client, Settings/LTR, release/packaging, board, and untracked TASK_346G implementation files from earlier gates. They were not changed for this B1 fix pass.

Browser smoke status:

- Developer thread still lacks usable browser automation for the in-app browser; prior Playwright smoke was blocked by the missing local Chromium headless executable.
- QA should re-smoke `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f` and verify the Open button's center hit-test resolves to the button or its descendants, then verify `POST /folder/open-local` or the explicit fallback message appears.

Stop point:

- Developer fix pass complete.
- Recommended next role: Reviewer implementation re-gate, followed by QA live browser re-smoke for B1.

## 15. Developer Fix Pass - QA Re-smoke Keyboard Activation

Status: fix pass complete - pending Reviewer implementation re-gate / QA re-smoke.

QA blocker handled:

- QA re-smoke closed the original pointer/hit-test blocker: the Open button center now resolves to `BUTTON Open`, and coordinate/semantic clicks trigger `POST /folder/open-local`.
- Remaining blocker: focused native `Open` button Enter-only keyboard activation did not produce an additional `open-local` request in the live in-app browser, even though focus was on the enabled `button[type="button"]`.

Root cause:

- The Open action relied only on the browser's native synthesized `click` for keyboard activation.
- In the live in-app browser re-smoke, pointer and semantic clicks reached the button, but the Enter-only path did not synthesize the same click request. The component had no explicit keyboard fallback for Enter/Space.
- This is a frontend activation-path bug in the Folder Actions button, not a backend bridge, resolver, or Sync/Submit/Pull workflow issue.

Fix summary:

- Added a shared `activateTaskAction()` path in `ProjectFolderTaskList.tsx`.
- Kept pointer `onClick` behavior unchanged by routing it through the shared function.
- Added explicit `onKeyDown` handling for `Enter` and Space on Folder Actions buttons. The handler calls the same action target and prevents the default native synthesis to avoid double invocation in browsers where native keyboard click works.
- Added a focused regression test proving `Project folder -> Open` invokes `project_folder_open` from both Enter and Space while focused.
- No backend, API client, Sync/Submit/Pull, resolver, real folder, LTR/public-drive authority, Projects registry, Matrix Editor, Settings/LTR, or release residual behavior was changed.

Fix-pass changed files:

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md`

Validation completed:

- Keyboard-focused red/green check:
  - Initial `npm test -- ProjectFolderTaskList --run` failed only because the test used unavailable `toHaveFocus`; the assertion was corrected to `document.activeElement`.
  - `npm test -- ProjectFolderTaskList --run` then passed: 1 file, 6 tests.
- Focused frontend suite:
  - `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run` passed: 4 files, 65 tests.
- Focused backend open bridge tests:
  - `py -m pytest tests\unit\test_project_folder_open_service.py tests\unit\test_local_folder_open_gateway.py tests\integration\test_project_folder_open_api.py -q` passed: 5 tests.
- Frontend build:
  - `npm run build` passed with the existing Vite chunk-size warning only.
- Diff and whitespace:
  - `git diff --check -- frontend/src/features/project-workbench/ProjectFolderTaskList.tsx frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx frontend/src/workbench.css frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx docs/lane_evidence/TASK_346G_workbench-project-folder-open-action-wiring_developer.md` passed with LF/CRLF warnings only.
  - `git diff --check --no-index` against a temporary empty file was also run for the untracked Developer evidence file and passed with LF/CRLF warnings only.
  - trailing whitespace scan on the fix-pass/package files returned no matches.
- Static scans:
  - no-real-folder mutation scan on TASK_346G open-bridge/fix package files returned no matches.
  - action-target scan confirms `project_folder_open` remains distinct from the old `actionTarget === "folder"` create/update path.
  - old copy/action-target scan still reports pre-existing legacy Workbench/test hits such as `public_drive_upload`, `Request material`, and `Source material`; these are outside this keyboard fix hunk.
  - UI anti-pattern scan on the changed Folder Actions component/test files returned no matches.
- Forbidden-scope status:
  - this keyboard fix pass modified only `ProjectFolderTaskList.tsx`, `ProjectFolderTaskList.test.tsx`, and this evidence file.
  - targeted status still shows pre-existing TASK_346G package files and unrelated backend/API client, Settings/LTR, release/packaging, board, and untracked residuals from earlier gates. They were not changed for this keyboard fix pass.

Browser smoke status:

- Developer thread does not have usable live in-app browser automation. QA should re-smoke the same project URL and verify focused `Open` plus Enter triggers `POST /folder/open-local` without triggering Sync/Submit/Pull or old create/update requests.

Stop point:

- Developer keyboard fix pass complete.
- Recommended next role: Reviewer implementation re-gate, followed by QA live browser keyboard re-smoke.

## 16. Integrator Packaging / Readiness Closeout

Status: integrator_accepted.

Integrator accepted TASK_346G after Reviewer implementation re-gate and QA live in-app browser keyboard re-smoke passed.

Package accepted:

- backend non-mutating project-folder open bridge:
  - `backend/api/routes_folder.py`
  - `backend/api/dependencies.py` TASK_346G open-service hunk only
  - `backend/application/project_folder_open_service.py`
  - `backend/infrastructure/files/local_folder_open_gateway.py`
  - focused backend tests
- frontend Workbench Open wiring:
  - `frontend/src/api/client.ts` TASK_346G open-helper hunk only
  - Workbench Folder Actions selector/component/model/layout/runtime files and focused tests
  - `frontend/src/workbench.css` z-index hit-test fix only
- TASK_346G task/plan/planner/developer/reconciliation/QA evidence and QA artifacts
- `docs/task_board.md` TASK_346G closeout only

Explicitly excluded:

- Settings/LTR helper residuals in backend/frontend/API client files;
- release/packaging residuals, `temp_agents_stash.md`, `.agents/**`, `docs/project_management/**`;
- Projects registry, Matrix Editor, real local/public folders, LTR workbook/public-drive authority writes, StepInstance, Report, AI, permissions, LAN/server, and multi-user scope.

Integrator validation:

- focused frontend Workbench suite: `npm test -- projectFolderTaskSelectors ProjectFolderTaskList ProjectWorkbenchLayout useProjectWorkbenchModel --run` passed (`4` files / `65` tests);
- focused backend open bridge suite: `py -m pytest tests\unit\test_project_folder_open_service.py tests\unit\test_local_folder_open_gateway.py tests\integration\test_project_folder_open_api.py -q` passed (`5` tests);
- `npm run build` passed with the existing Vite chunk-size warning only;
- `py -m py_compile` passed for TASK_346G backend bridge files;
- staged `git diff --cached --check` passed with LF/CRLF warnings only;
- staged whitelist/forbidden-path, no-real-folder mutation, and trailing-whitespace checks passed.

Remote push was intentionally not performed.
