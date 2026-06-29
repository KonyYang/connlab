# TASK_346B Developer Evidence - Workbench Folder Actions UI Refocus

Status: ready_for_review - implementation complete pending Reviewer implementation gate
Current Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Task: TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS
Lane: workbench-folder-actions-ui-refocus
Role: Developer
Date: 2026-06-29

## Authorization

Developer planning-first is allowed by the user delegation after the reported Reviewer plan gate pass. This pass is intentionally docs-only and does not authorize frontend/backend/test/API-client product implementation.

The local `docs/task_board.md` still contains pre-existing board residuals, so this evidence treats the current delegation and TASK_346B plan/evidence as the planning-first authority while avoiding product code changes.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product context through `node .agents/skills/impeccable/scripts/load-context.mjs`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_planner.md`
- Workbench Folder Actions source/tests by read-only `rg` reconnaissance

## Planning Findings

The existing Workbench Folder Actions UI is still a readiness/status flow:

- `ProjectFolderTaskList.tsx` renders `Next step`, `Project Folder progress`, detail panels, metrics, path rows, and old public-drive/source material details.
- `projectFolderTaskSelectors.ts` derives old task rows such as `Request material`, `Required forms`, `Submitted Material`, and `Public drive upload`, with status copy such as `Ready to upload`, `Partial`, `Not checked`, and `Already current`.
- `ProjectWorkbenchActiveMatrixWorkspace.tsx` exposes a singular `Folder Action` inspector.
- `ProjectWorkbenchLayout.tsx` and `ProjectWorkbenchLifecycleSections.tsx` still route old public-drive refresh/upload action targets.
- `projectWorkbenchLifecycleSelectors.ts` can still surface old next-action copy such as `Refresh public-drive preview` and `Upload to public drive`.
- `useProjectWorkbenchModel.ts` still owns old public-drive preview/upload state and messages.

No clear existing frontend helper was found for a safe local `Open project folder` action. Future implementation must not map `Open` to old create/update/generate behavior unless a safe existing open path is proven.

## Confirmed Future Implementation Shape

The future implementation should expose a compact `Folder Actions` surface with four entries:

- `Project folder` -> `Open`
- `Public working copy` -> `Auto sync` + `Sync now`
- `Approval package` -> `Submit`
- `Approved folder` -> `Pull`

`Open` is enabled only if a safe existing local-folder open action exists. Otherwise it remains disabled with a short blocker.

`Auto sync`, `Sync now`, `Submit`, and `Pull` remain disabled or blocked placeholders in TASK_346B because backend workflow/API wiring belongs to later TASK_346C+ lanes.

## Exact Future File List

Expected future implementation files:

- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only where required for Folder Actions hosting
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts` only if old public-drive next-action copy remains visible
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` only to stop exposing old upload wiring from the new default surface
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts` if selector copy is changed
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`

Locked:

- `frontend/src/api/client.ts`
- backend/API/file-operation implementation
- Projects registry / `ProjectListPage`
- Matrix Editor business logic
- public-drive authority writes
- TASK_346C+ workflow execution
- StepInstance / Report / AI / permissions / LAN/server / multi-user
- unrelated governance/orchestration residuals

## Copy And UI Rules

Remove or hide from the default Folder Actions surface:

- readiness/status cards
- `Next step`
- `Project Folder progress`
- singular `Folder Action` inspector card
- `Request material` / source-material card treatment
- `Source Book` / `Public folder` path rows
- persistent path, file-count, preview-item, last-sync, submit-time, or pull-time displays
- long explanatory copy
- `Ready`, `Partial`, `Waiting`, `Not current`, `Already current`, `Ready to upload`, `Refresh public-drive preview`, and `Upload to public drive`

Short disabled/blocker copy is allowed when it is directly actionable and business-readable, such as:

- `Project folder open is not connected yet.`
- `Sync workflow is not connected yet.`
- `Submit workflow is not connected yet.`
- `Pull workflow is not connected yet.`

## Dirty Residual Classification

Pre-existing dirty files observed before this planning-first edit:

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/workbench.css`
- `docs/task_board.md`

These were not edited by this TASK_346B Developer planning-first pass. They should be treated as external residuals unless a later approved TASK_346B implementation deliberately touches the Workbench files and records the exact reason.

## Validation

Planning validation completed:

- Required TASK_346B task/plan/planner-evidence/developer-evidence files exist: pass.
- `git diff --check -- docs/task_346b_workbench_folder_actions_ui_refocus_plan.md docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`: pass.
- trailing whitespace scan on the same two files: pass, no matches.
- targeted forbidden-scope status: no backend, tests, API-client, Projects registry, or ProjectListPage changes were introduced by this planning-first pass.
- Targeted status still shows pre-existing residuals in `docs/task_board.md`, `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`, and `frontend/src/workbench.css`; these are classified above as external residuals, not TASK_346B planning-first edits.

## Stop Point

Developer implementation is complete. Stop after callback. Recommended next role: Reviewer implementation gate.

## Implementation Pass

Implementation was authorized after Planner reconciliation recorded Reviewer plan gate pass, Developer planning-first completion, Reviewer implementation-readiness pass, and explicit user implementation approval.

### Changed Files

- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.ts`
- `frontend/src/features/project-workbench/projectWorkbenchLifecycleSelectors.test.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/workbench.css`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`

No backend, API client, Projects registry, Matrix Editor business logic, real folder path, or public-drive authority file was changed.

### Implementation Summary

- Replaced the old Folder Actions readiness/task selector with a quiet four-operation model:
  - `Project folder` -> `Open`
  - `Public working copy` -> `Auto sync` + `Sync now`
  - `Approval package` -> `Submit`
  - `Approved folder` -> `Pull`
- Kept all backend-dependent controls disabled/placeheld in TASK_346B. The new model emits no old public-drive upload/refresh action targets.
- Rebuilt `ProjectFolderTaskList` as a compact `Folder Actions` surface with short blockers only. It no longer renders task progress, detail panels, paths, file counts, preview item lists, or old status cards.
- Reused the same `ProjectFolderActionsSurface` in active Matrix and no-Matrix Workbench side areas, replacing singular `Folder Action` inspector cards.
- Updated Workbench next-action selector copy so old request-material/source-book/public-drive upload labels do not leak through the default Workbench banner.
- Updated `useProjectWorkbenchModel` user-facing messages from old source/request-material copy to neutral `Folder inputs` copy without changing API calls or state flow.
- Added scoped CSS for the compact Folder Actions grid. No thick side-stripe styling was added.

### Pre-Existing Residual Classification

Pre-existing residuals before this implementation:

- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - Existing residual: lifecycle activate button class from a prior button-style fix.
  - TASK_346B intentional edit: no-Matrix Folder Actions hosting.
- `frontend/src/workbench.css`
  - Existing residual: lifecycle close/activate button and confirmation button styling from a prior button-style fix.
  - TASK_346B intentional edit: `.runtime-console-folder-actions*` operation surface styles.
- `docs/task_board.md`, `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`, `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`, and reconciliation evidence remain governance/planning residuals from Planner reconciliation, not product implementation code.

Full Workbench-wide old-copy scan still finds legacy copy in files outside this implementation package, including `OfficialWorkspaceActionPanel.tsx` and `ProjectFolderCreationPanel.tsx`. Those files are outside TASK_346B implementation May Touch and were not changed. The TASK_346B package-file production scan has no matches for the banned old Folder Actions copy.

### Validation Results

- Focused frontend tests:
  - `npm test -- ProjectFolderTaskList projectFolderTaskSelectors projectWorkbenchLifecycleSelectors ProjectWorkbenchLayout useProjectWorkbenchModel --run`
  - Result: pass, 5 files / 76 tests.
- Frontend build:
  - `npm run build`
  - Result: pass. Existing Vite chunk-size warning remains.
- Diff check:
  - `git diff --check -- <TASK_346B package files>`
  - Result: pass with LF/CRLF normalization warnings only.
- Trailing whitespace scan:
  - `Select-String` over TASK_346B package files with `[ \t]+$`
  - Result: pass, no matches.
- Static copy scan for TASK_346B production package files:
  - scanned for `Ready to upload`, `Upload to public drive`, `Refresh public-drive preview`, `Project Folder progress`, `Next step`, `Public drive upload`, `Source Book`, `Already current`, `Request material`, `Source material`, `Not current`, `Waiting`, and `Partial`
  - Result: pass, no matches in the changed production package files.
- Forbidden-scope status:
  - targeted status showed no changes to `backend`, `frontend/src/api/client.ts`, `frontend/src/pages/ProjectListPage.tsx`, `frontend/src/features/projects-registry`, `frontend/src/features/matrix-editor`, or root `tests`.

### Browser Smoke

Browser smoke was not run in this thread because no in-app Browser MCP control tool was available after tool discovery. QA should smoke `/projects/:project_id` with an active Matrix project and a no-Matrix project to confirm the visible Folder Actions surface shows the four quiet entries, wraps cleanly, and does not show old readiness/status cards.

### Stop Point

Developer implementation complete. Recommended next role: Reviewer implementation gate.

## Integrator Packaging Checkpoint - 2026-06-29

Integrator gate: `accepted`.

### Package Scope Accepted

- Approved TASK_346B Workbench Folder Actions UI/CSS/test implementation files.
- TASK_346B task, plan, planner/developer/QA/reconciliation evidence, QA screenshots, and `docs/task_board.md` closeout.
- TASK_346A contract and Discovery source-of-truth files are included as upstream source-consistency inputs because the board and TASK_346B package depend on the accepted TASK_346A contract.

### Excluded Scope

- No backend/API/schema/file-operation implementation.
- No public folder resolver.
- No Sync/Submit/Pull execute behavior or public-drive authority writes.
- No `frontend/src/api/client.ts` changes.
- No Projects list, `ProjectListPage`, Matrix Editor business logic, real local/public folders, LTR workbook files, TASK_346C+ implementation, StepInstance, Report, AI, permissions, LAN/server, multi-user, `AGENTS.md`, `.agents/`, `docs/project_management/`, or unrelated governance/orchestration files.

### Integrator Validation

- Focused frontend tests rerun:
  - `npm test -- ProjectFolderTaskList projectFolderTaskSelectors projectWorkbenchLifecycleSelectors ProjectWorkbenchLayout useProjectWorkbenchModel --run`
  - Result: passed, `5` files / `76` tests.
- Frontend build rerun:
  - `npm run build`
  - Result: passed with existing Vite chunk-size warning only.
- Staged package checks:
  - `git diff --cached --check` passed with LF/CRLF normalization warnings only.
  - Staged whitelist and forbidden-path checks passed.
- QA browser smoke confirmed active Matrix `DL-2026-05-011`, registered no-Matrix `DL-2026-05-002`, and temporary/no-LTR `TMP-C4F39233` show the compact Folder Actions surface and keep Open/Auto sync/Sync now/Submit/Pull disabled or blocked as placeholders.

### QA Residual

Wide `1280px` screenshot capture returned left-shell-only images in the QA thread, while DOM verification and `514px` screenshots passed. This is accepted as non-blocking because the visual/narrow layout target and page DOM checks passed for all available fixtures.

### Final Stop Point

TASK_346B is packaged locally by Integrator. Remote push was intentionally not performed. Recommended next role: Orchestrator/Planner for one legal next routing action, or User if the Folder Actions series should pause.
