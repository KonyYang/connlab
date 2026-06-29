# TASK_346B Workbench Folder Actions UI Refocus - Planner Evidence

Task: `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS`
Lane: `workbench-folder-actions-ui-refocus`
Role: Planner
Status: ready_for_review - Reviewer plan gate requested; not approved implementation
Created: 2026-06-29
Last Updated: 2026-06-29

## 1. Current Phase / Task / Lane

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
- Current task: `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS`
- Current lane: `workbench-folder-actions-ui-refocus`
- Planner action: created formal planning-first downstream lane after user approval and TASK_346A Reviewer plan re-gate pass.

## 2. Discovery Gate Conclusion

Definition of Ready for a planned UI refocus lane: satisfied.

Definition of Ready for Developer implementation: not satisfied in this Planner turn.

Reason:

- Upstream `TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT` is accepted per user/Reviewer handoff.
- User explicitly approved creating the downstream lane.
- Repository evidence shows the current UI still exposes the old readiness/status task model.
- Scope can be bounded to frontend Workbench UI/CSS/focused tests without backend or API-client changes.
- Reviewer plan gate should review the new lane before any Developer implementation route.

## 3. Fact Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `$impeccable` context via `node .agents/skills/impeccable/scripts/load-context.mjs`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `PRODUCT.md` / `DESIGN.md` through `$impeccable` context
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md`
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md`
- `docs/lane_evidence/TASK_346A_project-workbench-folder-actions-contract_planner.md`
- `docs/lane_evidence/DISCOVERY_project-workbench-folder-actions-workflow_planner.md`
- Targeted source scans of:
  - `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
  - `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
  - `frontend/src/features/project-workbench/ProjectWorkbenchActiveMatrixWorkspace.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx`
  - `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - focused Workbench tests
  - `frontend/src/api/client.ts`

## 4. Repository-Proven Current UI Facts

- `ProjectFolderTaskList.tsx` currently renders `Next step`, a project-folder progress section, detail panels, `Source Book`, `Public folder`, and `Upload preview items`.
- `projectFolderTaskSelectors.ts` currently derives old task rows and labels including `Request material`, `Required forms`, `Submitted Material`, `Public drive upload`, `Ready to upload`, `Partial`, `Not checked`, and `Already current`.
- `ProjectWorkbenchActiveMatrixWorkspace.tsx` currently exposes a `Folder Action` inspector with one selected task, status badge, summary, and action.
- `ProjectWorkbenchLayout.tsx` routes `public_drive_refresh` and `public_drive_upload` to existing preview/upload handlers.
- `ProjectWorkbenchLifecycleSections.tsx` hosts `ProjectFolderTaskList` and maps public-drive action targets to old upload handlers.
- `useProjectWorkbenchModel.ts` owns old public-drive preview/upload state and handlers.
- `frontend/src/api/client.ts` contains old upload-only helpers:
  - `fetchPublicDriveUploadPreview`
  - `uploadPublicDriveProjectFolder`
- Current focused tests assert the existing Folder Action/readiness behavior.

## 5. Planner Decisions

- Create `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS` as a formal planning-first lane.
- Keep lane status `planned - ready for Reviewer plan gate; not approved for Developer implementation`.
- Scope future implementation to frontend Workbench UI/CSS/focused tests only.
- Keep `frontend/src/api/client.ts` locked.
- Treat existing public-drive upload preview/execute helpers as old behavior, not the new accepted Sync/Submit/Pull workflow.
- Allow `ProjectWorkbenchLifecycleSections.tsx` and `frontend/src/workbench.css` as future May Touch paths only because they may host/style Folder Actions. Their current dirty changes remain external residuals until a future Developer evidence proves intentional TASK_346B edits.

## 6. May Touch

For future implementation after Reviewer/user gates:

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
- `frontend/src/features/project-workbench/ProjectWorkbenchLifecycleSections.tsx` only if Folder Actions hosting requires it
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` only to stop exposing old upload UI wiring
- focused Workbench Folder Actions tests
- `frontend/src/workbench.css` only for scoped Folder Actions toolbar styling

## 7. Must Not Touch

- `frontend/src/api/client.ts`
- `backend/`
- backend tests
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/`
- Matrix Editor business logic
- public-drive roots
- local project folders
- LTR workbook files
- `AGENTS.md`
- `.agents/`
- `docs/project_management/`
- `TASK_346C+` implementation
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

## 8. Locked Paths

- `frontend/src/api/client.ts`
- `backend/**`
- `tests/**` outside focused frontend tests
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

Reviewer plan gate should confirm:

- lane is UI refocus only;
- default Folder Actions UI must show only the four accepted groups;
- no persistent readiness/status-card content remains in default Folder Actions;
- Sync/Submit/Pull remain disabled/blocked placeholders until backend/wiring lanes exist;
- `frontend/src/api/client.ts` and backend/file-operation paths remain locked;
- dirty frontend residuals are documented and excluded from this Planner package;
- browser smoke and focused test expectations are sufficient.

## 10. Merge Gate

No merge from this Planner pass.

Future implementation requires:

- Reviewer plan gate pass;
- explicit user approval for Developer implementation;
- Developer evidence;
- focused frontend tests/build/source scans;
- Reviewer implementation gate;
- QA gate if routed;
- Integrator packaging/readiness gate.

## 11. Files Created / Updated

- Created `tasks/TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS.md`
- Created `docs/task_346b_workbench_folder_actions_ui_refocus_plan.md`
- Created `docs/lane_evidence/TASK_346B_workbench-folder-actions-ui-refocus_planner.md`
- Updated `docs/task_board.md`

## 12. Stop Point

Planner gate: ready.

Recommended next role: Reviewer plan gate for `TASK_346B_WORKBENCH_FOLDER_ACTIONS_UI_REFOCUS`.

Do not route Developer implementation until Reviewer plan gate passes and the user separately approves implementation.
