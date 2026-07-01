# TASK_347A New Project Apply LTR Busy Lock UX - Planner Evidence

Status: planned
Date: 2026-07-02
Role: Planner
Task: `TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX`
Lane: `new-project-apply-ltr-busy-lock-ux`

## 1. Discovery Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: none. `TASK_346G_WORKBENCH_PROJECT_FOLDER_OPEN_ACTION_WIRING` is complete/accepted in `docs/task_board.md`.

Current role: Planner.

Why allowed: Orchestrator/User requested Planner Discovery and formal planning for a new New Project Apply LTR Number busy/interaction lock UX need.

## 2. User Goal Restatement

The New Project `Apply LTR Number` action is slow and important because it writes to the authoritative LTR workbook. During the operation, the operator should not be able to click sidebar navigation, `Import`, attachment actions, or other page actions that can interfere or make the workflow appear interrupted. The UI should show a compact in-progress state so the operator understands ConnLab is working.

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/PARALLEL_EXECUTION_MODEL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `$impeccable` product context from `PRODUCT.md` / `DESIGN.md`
- `docs/02_ARCHITECTURE_RULES.md`
- `docs/frontend_architecture_rules.md`
- `frontend/src/features/new-project/useNewProjectCompletion.ts`
- `frontend/src/features/new-project/NewProjectCompletionDock.tsx`
- `frontend/src/features/new-project/NewProjectApplicationEditor.tsx`
- `frontend/src/features/new-project/NewProjectSetupConfirmationPanel.tsx`
- `frontend/src/features/intake/IntakeSourcePanel.tsx`
- `frontend/src/pages/IntakeInboxPage.tsx`
- `frontend/src/App.tsx`
- `frontend/src/components/layout/AppShell.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/api/client.ts`
- `backend/api/routes_new_project_completion.py`
- `backend/application/new_project_completion_service.py`
- `backend/application/ltr_workbook_write_commit_service.py`
- project folder busy-lock pattern in `ProjectWorkbenchLayout.tsx` and `ProjectWorkbenchLayout.test.tsx`
- historical completed tasks `TASK_156`, `TASK_159`, and `TASK_160`
- `git status --short`

## 4. Confirmed Facts

Confirmed by user:

- `Apply LTR Number` can take a long time.
- The operator wants page actions blocked during LTR application.
- Sidebar buttons and `Import` are explicit concern points.
- The UX should communicate progress/status like the project folder creation workflow does.

Confirmed by repository evidence:

- `completeNewProject` is the frontend API helper for `POST /api/intake-cases/{case_id}/complete-new-project`.
- `useNewProjectCompletion` tracks `completionLoading`.
- `NewProjectCompletionDock` changes button text to `Applying LTR number...` and disables double submit through `completionDisabled`.
- `IntakeSourcePanel` currently disables `Import` only for `importing`, not for New Project completion.
- `Sidebar` has no navigation-lock prop.
- Backend completion remains a single request and does not expose progress phases.
- Existing project folder UX has a progress dialog pattern while a long workflow is running.

## 5. Planner Assumptions

- First lane should be frontend UX lock only.
- Backend phase progress should be a future lane if needed.
- Busy copy should be honest and compact, not fake step progress.
- Shell navigation lock can be scoped to New Project while `completionLoading` is true.

## 6. Missing Information / Blockers

Blockers: none for creating a planned lane.

Non-blocking unknown:

- Whether future users want real backend phase text such as workbook opened / row written / saved. This is not needed for TASK_347A and should remain a future backend progress lane if desired.

## 7. Planning Risk

If implemented without a lane, this could accidentally modify LTR workbook authority code, introduce fake progress states, or create broad global navigation lock behavior. The planned lane narrows the work to frontend busy lock and status UX.

## 8. Files Created / Updated

- `tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md`
- `docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md`
- `docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md`
- `docs/task_board.md`

## 9. Gate Decision

Definition of Ready is satisfied for a planned formal lane.

Planner gate: ready_for_reviewer_plan_gate.

Recommended next role: Reviewer plan gate.

Implementation is not authorized.

## 10. Validation

Docs diff check:

```powershell
git diff --check -- docs/task_board.md tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md
```

Result: passed with the existing `docs/task_board.md` LF/CRLF working-copy warning only.

Trailing whitespace scan:

```powershell
rg -n "[ \t]$" docs/task_board.md tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md
```

Result: no matches.

Source-of-truth scan:

```powershell
rg -n "TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX|new-project-apply-ltr-busy-lock-ux|Reviewer plan gate|Implementation is not authorized|planned" docs/task_board.md tasks/TASK_347A_NEW_PROJECT_APPLY_LTR_BUSY_LOCK_UX.md docs/task_347a_new_project_apply_ltr_busy_lock_ux_plan.md docs/lane_evidence/TASK_347A_new-project-apply-ltr-busy-lock-ux_planner.md
```

Result: planned lane status, Reviewer plan gate stop point, and implementation-not-authorized wording are present.

Targeted status note:

- This Planner pass changed only TASK_347A source-of-truth docs and `docs/task_board.md`.
- Existing unrelated dirty residuals remain visible in status, including Settings/LTR helper files, external resource route/test files, Office gateway/parser files, release/packaging files, desktop packaging files, and `temp_agents_stash.md`.
- Those residuals remain excluded from TASK_347A and are not adopted into this lane.
