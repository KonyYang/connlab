# TASK_185 Project Workbench State Model And Layout Refactor

> Status: complete
> Created: 2026-05-12
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`.
- Current active task in board at creation time: `TASK_184_PROJECT_WORKBENCH_MATRIX_FIRST_REDESIGN_BASELINE` complete.
- Why this task is allowed now: TASK_184 baseline is complete and defines Matrix-first Workbench direction. The immediate next step is structural frontend refactor to reduce page complexity and establish stage-oriented layout while preserving current behavior.
- Implementation gate: do not write implementation code until the user explicitly approves this task (example: `批准执行 TASK_185`).

---

## 1. Model Fit

`gpt-5.3-codex` is suitable for implementation.

Reason:

- The task is bounded to frontend architecture cleanup and layout refactor.
- It primarily requires TypeScript/React state extraction and component composition changes.
- It does not require new backend endpoints or Office processing changes.

---

## 2. Purpose

Refactor Project Workbench from a page-heavy orchestration file into a feature-oriented structure:

- extract a `useProjectWorkbenchModel` state hook;
- introduce a stage layout shell;
- move evidence and approval package workflow rendering out of the route page;
- preserve current business behavior and API calls.

---

## 3. Scope

In scope:

- `frontend/src/pages/ProjectWorkbenchPage.tsx` slimming.
- Add `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`.
- Add stage layout/presentation components under `frontend/src/features/project-workbench/`.
- Move evidence placement panel into feature boundary.
- Move approval package panel into feature boundary (or keep wrapper compatibility if required by tests).
- Keep folder creation panel integration through existing feature path.
- Keep current API contracts unchanged.

Out of scope:

- No new backend API.
- No Matrix review implementation UI (that belongs to TASK_186).
- No auto-carry path behavior change (TASK_187).
- No stale/version state implementation (TASK_188).
- No report generation or standards lookup.

---

## 4. Design Constraints

- Route page should only own route params/navigation and high-level loading boundary.
- API fetch boundary must remain `frontend/src/api/client.ts`.
- Keep existing user-visible behavior stable:
  - folder creation behavior unchanged;
  - evidence preview/place behavior unchanged;
  - approval package preview/execute behavior unchanged.
- Keep CSS within current product design language and existing workbench styles.

---

## 5. Expected Files

Likely touched:

- `frontend/src/pages/ProjectWorkbenchPage.tsx`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchStagePanel.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchEvidencePanel.tsx`
- `frontend/src/features/project-workbench/ProjectFolderCreationPanel.tsx` (if prop boundaries change)
- `frontend/src/components/workflow/ApprovalPackagePanel.tsx` (move/re-export or feature relocation)
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (if static expectations require updates)

Docs:

- `docs/task_185_project_workbench_state_model_and_layout_refactor_plan.md`
- `docs/task_board.md`

---

## 6. Validation Plan

Frontend build:

```powershell
cd frontend
npm run build
```

Workbench static guard:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"
```

Task board guard:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 7. Acceptance Criteria

- Route page no longer contains large evidence-placement JSX and heavy workflow state logic.
- A dedicated feature model hook coordinates Workbench API calls and local state.
- Stage layout component exists and organizes current features in stage-oriented structure.
- Existing folder/evidence/approval package flows still work without backend changes.
- Frontend build passes.
- Target tests pass.
- Task board is updated.

---

## 8. Stop Condition

After implementation and validation:

- update task board;
- record validation;
- stop;
- do not start TASK_186 without explicit user approval.

---

## 9. Completion Notes

Completed on 2026-05-12.

Implemented:

- Added `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts` to centralize:
  - Project/LTR/resource loading
  - evidence preview/place state and actions
  - approval package input/preview/execute state and actions
  - baseline status items and folder readiness derivation
- Added `frontend/src/features/project-workbench/ProjectWorkbenchEvidencePanel.tsx` to extract the evidence placement UI block from the route page.
- Added `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx` as stage-oriented composition layout for:
  - summary/status
  - folder creation
  - lookup
  - approval package
  - evidence placement
- Slimmed `frontend/src/pages/ProjectWorkbenchPage.tsx` to a route-level shell:
  - model hook usage
  - loading/error/message boundary
  - layout composition only
- Updated frontend static tests to accept model/layout based Workbench ownership while preserving business assertions:
  - `tests/unit/test_frontend_shell_files.py`

Validation:

- `npm run build` (frontend) passed.
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or approval or folder"` passed (`5 passed, 53 deselected`).
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
