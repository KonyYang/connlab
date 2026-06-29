# TASK_346B Workbench Folder Actions UI Refocus

Status: complete/accepted after Reviewer implementation gate, QA gate, and Integrator packaging/readiness
Lane: workbench-folder-actions-ui-refocus
Owner Roles: Planner / Reviewer, then Frontend Developer after separate approval
Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
Created: 2026-06-29

## 1. Purpose

Create the formal planning-first lane for the first downstream implementation slice after `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT`.

TASK_346B should refocus the Project Workbench Folder Actions surface into a quiet four-action toolbar:

- Project folder: `Open`
- Public working copy: `Auto sync` and `Sync now`
- Approval package: `Submit`
- Approved folder: `Pull`

This lane is UI refocus only. It must not implement dangerous file operations, public-folder workflow backend behavior, resolver logic, or Sync/Submit/Pull execute behavior. Those remain downstream `TASK_346C+`.

## 2. Inputs

- `AGENTS.md`
- `docs/task_board.md`
- `$impeccable` product UI guidance
- `PRODUCT.md`
- `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- Existing Workbench Folder Actions frontend code and focused tests

## 3. Repository-Proven Starting Point

- Current Workbench Folder Actions still use a task/readiness model:
  - `ProjectFolderTaskList.tsx` renders `Next step`, task steps, detail panels, path lines, preview details, and status labels.
  - `projectFolderTaskSelectors.ts` produces `Request material`, `Required forms`, `Submitted Material`, and `Public drive upload` tasks with labels such as `Ready to upload`, `Partial`, `Not checked`, and `Already current`.
  - `ProjectWorkbenchLayout.tsx` and `ProjectWorkbenchLifecycleSections.tsx` currently wire `public_drive_refresh` and `public_drive_upload` actions to existing preview/upload handlers.
  - `frontend/src/api/client.ts` already contains old public-drive upload preview/execute helpers, but those helpers do not represent the accepted `TASK_346A` Sync/Submit/Pull workflow contract.
- Existing focused tests assert the current readiness/status UI and will need controlled updates in the implementation lane.
- Current workspace has pre-existing frontend dirty residuals in:
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - `frontend/src/workbench.css`

Those residuals are not part of this Planner pass. They must be inspected and separated by Developer/Integrator if TASK_346B later intentionally edits the same files.

## 4. Scope

TASK_346B may plan and later implement only the frontend Workbench Folder Actions UI refocus:

- Replace the default readiness/status-card Folder Actions surface with a compact file-action toolbar.
- Show only the four accepted operation groups by default.
- Keep real Sync, Submit, and Pull execution disabled or blocked with short inline blockers until backend `TASK_346C` and wiring `TASK_346D` exist.
- Keep `Open` constrained to an existing safe frontend/workspace affordance if one already exists; otherwise show it as disabled/blocked with a short reason. Do not fake a successful OS folder open.
- Remove or hide persistent default displays of target paths, file counts, timestamps, preview item lists, readiness status labels, and separate Source material cards from the Folder Actions surface.
- Preserve Workbench shell, lifecycle primary action UI, Matrix authority, and existing readonly guard behavior.

## 5. Out Of Scope

TASK_346B must not implement:

- backend public folder resolver
- `public_folder_year` resolver
- Sync preview or execute
- Submit preview or execute
- Pull preview or execute
- public-drive file move/copy/archive behavior
- public-drive LTR workbook authority write
- new API client helpers or API contract changes
- Projects list changes
- Matrix Editor business logic
- StepInstance, Report generation, AI review, permissions, LAN/server, or multi-user scope
- cleanup or packaging of unrelated governance/orchestration residuals

## 6. May Touch

For the Developer implementation pass authorized after Reviewer plan/readiness gates and explicit user approval:

- `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_planner.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_developer.md`
- `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_qa.md` if QA is routed
- `docs/task_board.md`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only if Folder Actions placement/wiring requires it
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` only to stop old upload UI wiring from being exposed by the new toolbar, not to add new API behavior
- focused Workbench Folder Actions tests under `frontend/src/features/project-workbench/`
- `frontend/src/workbench.css` only for the Folder Actions toolbar layout/states

## 7. Must Not Touch

- `frontend/src/api/client.ts`
- `backend/`
- `tests/` backend tests except no touch in this lane
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/`
- Matrix Editor business logic
- public-drive roots
- local project folders such as `D:\Test Project`
- development public roots such as `D:\PublicProject`
- LTR workbook files
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- `TASK_346C+` future lane implementation files
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 8. Locked Paths

- `frontend/src/api/client.ts`
- `backend/**`
- `tests/**` outside focused frontend tests under `frontend/src/features/project-workbench/`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `frontend/src/features/matrix-editor/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `.agents/**`
- `docs/project_management/**`

## 9. Validation Gate

Reviewer plan gate has passed and Reviewer implementation-readiness content review has passed per current delegation. Developer implementation may proceed only within the approved scope.

Developer implementation must confirm:

- TASK_346B is UI refocus only and does not authorize backend/API/file-operation work.
- `frontend/src/api/client.ts` remains locked because no new Sync/Submit/Pull API contract exists in this lane.
- The old public-drive upload preview/execute helpers are not treated as the accepted Sync/Submit/Pull workflow.
- Default Folder Actions UI removes readiness/status-card behavior and exposes only the four accepted operation groups.
- Sync, Submit, and Pull remain disabled/blocked placeholders or non-executing affordances until downstream backend/wiring lanes exist.
- The implementation plan preserves existing lifecycle readonly guard behavior and does not touch Projects list or Matrix Editor business logic.
- Existing dirty frontend residuals are recorded and must not be silently packaged unless the future Developer evidence proves they are intentional TASK_346B edits.

## 10. Merge Gate

Implementation is now authorized after user approval, but is not complete.

Implementation can merge only after:

- Reviewer plan gate passes.
- User explicitly approves Developer implementation.
- Developer evidence proves scoped frontend-only changes.
- Focused frontend tests pass.
- Frontend build passes or any existing warnings are explicitly classified.
- Reviewer implementation gate passes.
- QA gate runs if routed by the board.
- Integrator packaging confirms no backend/API/client/Projects/Matrix/future-scope or unrelated residuals are included.

## 11. Planner Reconciliation

2026-06-29 source-of-truth reconciliation:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and updated only TASK_346B plan/evidence.
- Reviewer implementation-readiness content review passed.
- User explicitly approved Developer implementation.
- Repository source-of-truth is now aligned to implementation-authorized, pending Developer implementation.
- Reconciliation evidence: `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_reconciliation_planner.md`.

Current stop point: Developer implementation pass. Do not route Reviewer until Developer evidence is updated to `ready_for_review`.
