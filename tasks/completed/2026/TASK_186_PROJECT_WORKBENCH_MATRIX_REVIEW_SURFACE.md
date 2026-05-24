# TASK_186 Project Workbench Matrix Review Surface

> Status: complete
> Created: 2026-05-13
> Phase: Phase 11 - Project planning data foundation before downstream document automation

---

## 0. Execution Gate

- Current phase at creation time: `Phase 11`.
- Current active task in board at creation time: `TASK_185_PROJECT_WORKBENCH_STATE_MODEL_AND_LAYOUT_REFACTOR` complete.
- Why this task is allowed now: TASK_184 defined the Matrix-first Workbench direction and TASK_185 established the feature model/layout boundary needed for a controlled UI implementation.
- Implementation gate: do not write implementation code until the user explicitly approves this task (example: `批准执行 TASK_186`).

---

## 1. Model Fit

`gpt-5.3-codex` is suitable for implementation.

Reason:

- The task is bounded to frontend wiring and display of existing Project-stage test-plan draft data.
- It requires React/TypeScript feature work and typed API client additions.
- It does not require new backend endpoints, Office writes, document generation, parser changes, or persistence changes.

---

## 2. Purpose

Add a Matrix-first review surface to Project Workbench using existing ProjectTestPlanDraft backend APIs.

The operator should be able to see:

- active ProjectTestPlanDraft availability;
- Matrix groups and test steps;
- duration assumptions when present;
- source traceability;
- missing-data warnings;
- clear empty/error states when no draft exists.

---

## 3. Scope

In scope:

- Add typed frontend API client coverage for existing ProjectTestPlanDraft list/detail responses.
- Extend `useProjectWorkbenchModel` to load active test-plan draft state for the current Project.
- Add a dedicated Matrix review component under `frontend/src/features/project-workbench/`.
- Place the Matrix review surface near the top of `ProjectWorkbenchLayout`, after project status and before downstream document stages.
- Add static frontend guard expectations for the new Workbench ownership.

Out of scope:

- No new backend API.
- No Matrix parser changes.
- No ProjectTestPlanDraft editing.
- No version/stale status persistence.
- No Section 2 write-back wiring changes.
- No test record, fee, approval package autofill changes.
- No Office file write behavior.
- No report generation, AI review, standards search, or historical report search.

---

## 4. Design Constraints

- Keep `Project` as the system center; Matrix is the first work view, not the system data model.
- Treat `ProjectTestPlanDraft` as the structured intermediate object.
- UI must remain a restrained product workbench, not a spreadsheet clone or decorative dashboard.
- Do not place report narrative, measurement records, or fee workbook layout details inside Matrix.
- Route page remains thin; Workbench orchestration stays in `useProjectWorkbenchModel`.
- API calls remain centralized in `frontend/src/api/client.ts`.

---

## 5. Expected Files

Likely touched:

- `frontend/src/api/client.ts`
- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py`

Docs:

- `docs/task_186_project_workbench_matrix_review_surface_plan.md`
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
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix"
```

Task board guard:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

Manual smoke path:

1. Open a Project with at least one active ProjectTestPlanDraft.
2. Confirm Workbench shows Matrix groups/steps and source traceability.
3. Open a Project without a draft.
4. Confirm Workbench shows a clear empty state and does not block folder/evidence/approval package behavior.

---

## 7. Acceptance Criteria

- Matrix review surface exists in Project Workbench and appears before downstream document stages.
- Existing ProjectTestPlanDraft data is displayed without backend changes.
- Missing draft and draft-load error states are business-readable.
- Folder creation, evidence placement, lookup, and approval package panels remain behavior-compatible.
- No Office write behavior is added.
- Frontend build passes.
- Target tests pass.
- Task board is updated after implementation.

---

## 8. Stop Condition

After plan creation:

- stop and wait for explicit user approval before implementation.

After approved implementation:

- update task board;
- record validation;
- stop;
- do not start TASK_187 without explicit user approval.

---

## 9. Completion Notes

Completed on 2026-05-13.

Implemented:

- Added frontend test-plan draft DTOs and API client requests:
  - `listProjectTestPlanDrafts`
  - `getProjectTestPlanDraft`
- Extended Workbench model hook to load one active (non-superseded) Project test-plan draft with dedicated loading/error state.
- Added `ProjectWorkbenchMatrixReviewPanel` under `features/project-workbench` to render:
  - source draft identity and status;
  - group/step counts;
  - group and step-level Matrix review rows;
  - duration hint summary text;
  - missing-draft empty state;
  - draft warning list.
- Updated Workbench layout to place Matrix review after status/folder context and before lookup/approval/evidence operations.
- Added Workbench CSS classes for Matrix panel summary and step rows.
- Added static guard assertions for TASK_186 wiring in `tests/unit/test_frontend_shell_files.py`.

Validation:

- `npm run build` passed (frontend).
- `py -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix"` passed (`4 passed, 55 deselected`).
- `py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q` passed (`17 passed`).
