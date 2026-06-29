# TASK_346F Workbench Folder Actions Contextual Panel Polish - Planner Evidence

Task: `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`
Lane: `workbench-folder-actions-contextual-panel-polish`
Role: Planner
Status: ready_for_review - planned lane, not approved implementation
Created: 2026-06-29
Last Updated: 2026-06-29

## 1. Current Phase / Task / Lane

- Phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation
- Current active implementation lane: none after TASK_346B complete/accepted
- Current task: `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`
- Current lane: `workbench-folder-actions-contextual-panel-polish`
- Planner action: Discovery and formal planning-first lane creation only.

## 2. Current Fact Source Summary

Sources read:

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/connlab-lane-orchestrator/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` product context through `node .agents/skills/impeccable/scripts/load-context.mjs`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- TASK_346A task, plan, and planner evidence
- TASK_346B task, plan, developer evidence, QA evidence, and board closeout
- current Workbench Folder Actions frontend code/tests/CSS by targeted read-only scans

## 3. User-Confirmed Facts

- User wants a contextual file operation panel style.
- The panel should show four file operation entries:
  - `Project folder`
  - `Public working copy`
  - `Approval package`
  - `Approved folder`
- Each entry should use icon, title, helper/context text, and right-side control.
- Thin separators and restrained operational UI are desired.
- Necessary context is allowed, including path fragments, Open/Closed year, file count, last sync, `keep local history`, and `after confirmation`.
- The UI must not restore old readiness/status panels or old workflow copy.
- Missing backend data must be hidden, disabled, or treated as safe placeholder.

## 4. Repository-Proven Facts

- `docs/task_board.md` records `TASK_346A` complete/accepted and `TASK_346B` complete/accepted.
- `TASK_346B` implemented the four-action model and left Open/Auto sync/Sync/Submit/Pull disabled or blocked placeholders.
- `ProjectFolderTaskList.tsx` now renders `ProjectFolderActionsSurface`.
- `projectFolderTaskSelectors.ts` now returns four operation rows, but summaries are generic placeholder copy.
- `frontend/src/workbench.css` currently renders a two-column `.runtime-console-folder-operation-grid` and bordered operation tiles.
- Focused tests assert current four-action behavior and banned old copy.
- Existing `UiIcon` has relevant icons such as `folder`, `upload`, `refresh`, and `package`.

## 5. TASK_346C Numbering Decision

`TASK_346C` is reserved and should not be reused for this UI polish lane.

Evidence:

- `tasks/TASK_346A_PROJECT_WORKBENCH_FOLDER_ACTIONS_CONTRACT.md` recommends `TASK_346C_PUBLIC_FOLDER_WORKFLOW_BACKEND`.
- `docs/task_346a_project_workbench_folder_actions_contract_plan.md` lists TASK_346C as backend public folder workflow and TASK_346D as frontend/API-client wiring that depends on TASK_346C.
- Discovery evidence states TASK_346C backend should proceed before functional UI wiring.

Planner decision:

- Use `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`.
- Record this as a numbering conflict avoidance, not a product dependency change.

## 6. Why Formal Lane Is Needed

Formal lane is required because:

- TASK_346B is already accepted and packaged.
- The new target changes visual structure and context policy beyond the accepted TASK_346B toolbar.
- Context helper policy can accidentally imply fake backend data if not scoped.
- The lane must preserve backend/API/client locks and not steal TASK_346C backend workflow.

Do not directly continue TASK_346B because it would mix a post-acceptance UI polish into a closed package.

## 7. Recommended Task / Lane

- Task ID: `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`
- Lane: `workbench-folder-actions-contextual-panel-polish`
- Status: planned - ready for Reviewer plan gate; not approved implementation
- Next role: Reviewer plan gate

## 8. May Touch

Future implementation May Touch after Reviewer/user gates:

- `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_planner.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_developer.md`
- `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_qa.md` if QA is routed
- `docs/task_board.md`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.ts`
- `frontend/src/features/project-workbench/ProjectFolderTaskList.test.tsx`
- `frontend/src/features/project-workbench/projectFolderTaskSelectors.test.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.test.tsx`
- `frontend/src/workbench.css`

## 9. Must Not Touch / Locked Paths

Must Not Touch:

- `backend/**`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `frontend/src/features/projects-registry/**`
- `D:\Test Project/**`
- `D:\PublicProject/**`
- real public-drive folders
- LTR workbook files
- `AGENTS.md`
- `.agents/**`
- `docs/project_management/**`
- StepInstance, Report, AI, permissions, LAN/server, multi-user scope

Locked Paths are the same as Must Not Touch.

## 10. UI Acceptance Standards

- Single-column contextual Folder Actions panel.
- Four groups in order: Project folder, Public working copy, Approval package, Approved folder.
- Each group shows icon, title, helper/context text, and right-side control.
- Rows are compact and divided by thin separators.
- Matrix table remains primary.
- Necessary context is allowed only when real existing data or safe placeholder.
- Bottom short blocker appears only when needed.
- No old readiness/status vocabulary or old workflow copy appears.
- Disabled placeholders must not call old public-drive upload behavior.

## 11. Validation Gate

Reviewer plan gate:

- Confirm TASK_346C is preserved for backend public folder workflow.
- Confirm TASK_346F scope is frontend UI polish only.
- Confirm context helper policy does not invent backend facts.
- Confirm `frontend/src/api/client.ts`, backend, Projects list, and Matrix Editor remain locked.
- Confirm tests and browser smoke expectations are adequate.

## 12. Merge Gate

No merge from Planner pass.

Future implementation merge requires:

- Reviewer plan gate pass.
- User implementation approval.
- Developer evidence with scoped frontend-only changes.
- Focused tests and `npm run build`.
- Browser smoke for `http://localhost:5173/projects/72fbbfa290294da9a507344b68ff900f` if routed.
- Reviewer implementation gate.
- QA if routed.
- Integrator packaging/readiness.

## 13. Blocking Clarification Questions

None.

Definition of Ready for planned lane and Reviewer plan gate: satisfied.

Definition of Ready for Developer implementation: not satisfied until Reviewer plan gate passes and user explicitly approves implementation.

## 14. Files Created / Updated

- Created `tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md`
- Created `docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md`
- Created `docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_planner.md`
- Updated `docs/task_board.md`

## 15. Planner Validation

- TASK_346F source-of-truth reference scan passed across board, task, plan, and planner evidence.
- `git diff --check -- docs/task_board.md tasks/TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH.md docs/task_346f_workbench_folder_actions_contextual_panel_polish_plan.md docs/lane_evidence/TASK_346F_workbench-folder-actions-contextual-panel-polish_planner.md`: passed with CRLF conversion warning for `docs/task_board.md` only.
- Trailing whitespace scan for touched docs: passed, no matches.
- Targeted status confirms this Planner pass changed only `docs/task_board.md` and new TASK_346F planning/evidence files. No backend, frontend, or tests product files were changed.

## 16. Stop Point

Planner gate: ready.

Recommended next role: Reviewer plan gate for `TASK_346F_WORKBENCH_FOLDER_ACTIONS_CONTEXTUAL_PANEL_POLISH`.

Do not route Developer implementation.
