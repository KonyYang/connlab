# ConnLab Architecture Inventory (2026-05-15)

## 1) Inventory Purpose

Validate consistency between:

- product positioning docs (`README.md`);
- execution control (`docs/task_board.md`, `tasks/`);
- actual implemented code structure (`backend/`, `frontend/`).

Scope is diagnostic and governance-only. No behavior refactor is included.

## 2) High-Level Consistency Result

Result: **partial mismatch** before TASK_193 updates, now aligned at stage-definition layer.

- Old mismatch: README still stated MVP-only and Matrix out-of-scope.
- Code/task reality: Matrix + Approval Package chain already implemented and accepted in TASK_174~TASK_192.

## 3) Traceability Table (README vs Task Board vs Code)

1. Early-MVP-only positioning:
   - README (before TASK_193): claimed MVP-only and Matrix out-of-scope.
   - Task board: `TASK_174` onward includes Matrix baseline, draft persistence, edit/freeze semantics, authority workspace.
   - Code evidence:
     - `backend/api/routes_project_test_plan*.py`
     - `backend/api/routes_project_test_plan_matrix_edit.py`
     - `frontend/src/features/project-workbench/ProjectWorkbenchMatrix*.tsx`
2. Approval package flow:
   - Task board: `TASK_182`, `TASK_183` complete.
   - Code evidence:
     - `backend/api/routes_approval_package.py`
     - `frontend/src/components/workflow/ApprovalPackagePanel.tsx`
3. Output version ledger:
   - Task board: `TASK_188 ... ledger correction` complete.
   - Code evidence:
     - `backend/api/routes_project_output_records.py`
     - `frontend/src/features/project-workbench/projectWorkbenchVersionSelectors.ts`

## 4) Backend Architecture Layer Check (Against AGENTS Layering)

Observed top-level backend layout:

- `backend/domain`
- `backend/application`
- `backend/infrastructure`
- `backend/modules`
- `backend/api`
- `backend/shared`

This matches prescribed layered structure at directory level.

Route surface remains thin by pattern (route modules exist as separate files and call application/services by dependency wiring).

## 5) Frontend Workbench Stage Evidence

Project Workbench feature area includes dedicated stage components:

- matrix authority/review/overview/inspector/starter components;
- document status panel;
- evidence panel;
- model hook (`useProjectWorkbenchModel`) for orchestration.

This is consistent with post-MVP workbench stage, not minimal MVP shell stage.

## 6) Task Inventory Status

- `tasks/` contains continuous task history from `TASK_001` to `TASK_193`.
- `docs/task_board.md` records completion through `TASK_192` before this governance update.
- TASK_193 now formalizes stage freeze and doc/code/task alignment action.

## 7) Governance Conclusion

ConnLab current baseline should be treated as:

`Project Workbench / Matrix / Approval Package`

The original MVP statement remains useful only as historical phase context, not as current scope control text.

