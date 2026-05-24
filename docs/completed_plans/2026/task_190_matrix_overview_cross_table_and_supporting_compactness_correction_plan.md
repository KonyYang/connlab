# TASK_190 Correction Plan: Matrix Cross-Table + Supporting Compactness

> Task: `TASK_190_MATRIX_OVERVIEW_CROSS_TABLE_AND_SUPPORTING_COMPACTNESS_CORRECTION`  
> Status: plan proposed (implementation not started)  
> Date: 2026-05-14

---

## 1) Execution Context

- Current phase: `Phase 11 - Project planning data foundation before downstream document automation`
- Current board state: TASK_190 implemented but acceptance not granted.
- Why this task is allowed now: acceptance review found one high-severity gap and two medium-severity gaps within TASK_190 scope.

---

## 2) Problem Statement

Remaining TASK_190 mismatches:

1. High: Matrix overview is flat step list, not Matrix cross-table.
2. Medium: supporting workflows are still visually heavy (default expanded).
3. Medium: `ProjectWorkbenchMatrixReviewPanel.tsx` is too large for sustainable iteration.

Impact:

- Operators cannot scan "test item x groups x token" relationship in one matrix surface.
- First viewport still competes with downstream panels instead of Matrix-first planning.
- Future controlled iterations (inspector enrichment/result linkage) carry higher change risk.

---

## 3) Scope

### In Scope

- Frontend-only correction inside project-workbench feature.
- Matrix overview conversion to cross-table.
- Supporting workflow compactness defaults.
- Matrix panel component split.
- Static test updates and build verification.

### Out Of Scope

- No backend/API changes.
- No new business workflows.
- No report/AI/history/image/test-result import scope.

---

## 4) Design Decisions

### A. Matrix overview contract (cross-table)

- Row grain: normalized test item/context row.
- Left fixed columns: `Test item`, `Method`, `Condition`, `Requirement` (plus lightweight context if already available).
- Right dynamic columns: one column per visible group label.
- Cell value: comma-separated step tokens for that row x group intersection.
- Empty cell: `-`.

Normalization rules (frontend view-layer only):

1. Build row key from step semantic tuple:
   - `test_item + method_summary + condition_summary + judgement_criteria`
2. Aggregate all matching steps under each group.
3. Render deduplicated tokens in stable order.

This keeps existing draft payload unchanged while achieving matrix-like readability.

### B. Supporting compactness rules

- Supporting workflows are reachable but collapsed by default:
  - `Project folder`
  - `Approval package`
  - `Evidence placement`
  - `Read-only lookup`
- First screen keeps matrix workspace and downstream status visible without long expanded forms.

### C. Component split target

Minimum split:

- `ProjectWorkbenchMatrixAuthorityBar.tsx`
- `ProjectWorkbenchMatrixOverview.tsx`
- `ProjectWorkbenchMatrixInspector.tsx` (or `ProjectWorkbenchGroupEditor.tsx`)

Container component keeps orchestration only; helper transforms move to dedicated utility file if needed.

---

## 5) File-Level Change Plan

Primary frontend files:

- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx`
  - reduce orchestration size and delegate rendering to subcomponents.

- New files (expected):
  - `frontend/src/features/project-workbench/ProjectWorkbenchMatrixAuthorityBar.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx`
  - `frontend/src/features/project-workbench/ProjectWorkbenchMatrixInspector.tsx`
  - optional: `frontend/src/features/project-workbench/projectWorkbenchMatrixOverviewSelectors.ts`

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - ensure supporting sections default to compact/collapsed state.

- `frontend/src/workbench.css`
  - cross-table styles and compact supporting-section behavior.

Tests:

- `tests/unit/test_frontend_shell_files.py`
  - assert cross-table markers and group-column rendering hooks.
  - assert supporting panels default compactness.
  - assert component split presence.

Docs:

- `docs/task_board.md` (after implementation only).

---

## 6) Risks and Mitigations

1. **Risk:** cross-table mapping loses per-step detail.  
   **Mitigation:** keep inspector/editor unchanged as detail surface; overview is for navigation/readability.

2. **Risk:** group columns overflow on smaller screens.  
   **Mitigation:** keep horizontal scroll at table wrapper and fixed minimum column widths.

3. **Risk:** component split causes prop drift.  
   **Mitigation:** keep prop contracts explicit and covered by static shell tests.

---

## 7) Validation Plan

```powershell
cd frontend
npm run build
```

```powershell
python -m pytest tests\unit\test_frontend_shell_files.py -q -k "workbench or matrix or task190"
```

```powershell
python -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

---

## 8) Completion Criteria

- Matrix overview visually and structurally matches cross-table contract.
- Supporting workflows are compact by default and do not dominate first viewport.
- Matrix review code is split into smaller feature components with preserved behavior.
- Build/tests pass and board wording is synchronized.
