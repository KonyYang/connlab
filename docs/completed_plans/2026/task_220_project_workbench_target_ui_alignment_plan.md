# TASK_220 Plan - Project Workbench Target UI Alignment

## 1. Task Context

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task on board: `none`
- Allowed now because `TASK_219F` is complete and this is a controlled frontend-only alignment task.
- Task type: UI alignment only, not redesign.

## 2. Goal

Make the current Project Workbench page converge to the target visual contract `Project workbench UI.png` while keeping Runtime Console positioning and existing business boundaries unchanged.

Required constraints:

- English UI labels.
- Reuse existing component system.
- No backend, API contract, domain model, or persistence changes.
- No restoration of lower legacy workflow panels removed in `TASK_219F`.

## 3. Current vs Target Delta Summary

### 3.1 Missing Areas

- Compact top readiness strip with full item sequence and right-side setup action.
- Target-level spacing rhythm in header and filter bars.
- Target-like density in right Step Workspace cards and actions.

### 3.2 Excess / Mismatch Areas

- Header right section can crowd/wrap and lose target rhythm.
- Some labels and helper lines are still generic runtime wording instead of target-equivalent operational wording.
- Bottom surfaces are present but visual hierarchy/density differs from target.

### 3.3 Layout Differences

- Top header block proportions differ from target.
- Matrix/Step split and internal paddings differ from target.
- Bottom three surfaces need closer target proportions and alignment.

### 3.4 Information Hierarchy Differences

- Readiness context needs stronger top-level placement directly below header.
- Step workspace needs clearer action-first, data-second order matching target.
- Runtime attention should emphasize operator-facing issues over system-internal counters.

## 4. Execution Scope

In scope:

- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx` (only if needed for target structure/density)
- `frontend/src/workbench.css`
- `tests/unit/test_frontend_shell_files.py` (TASK_220 static expectations)

Out of scope:

- `backend/**`
- `frontend/src/api/client.ts`
- Domain objects, SQL schema, endpoints, request/response contracts
- New routes, new dependencies, workflow feature expansion

## 5. File-Level Change Plan

## 5.1 `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`

- Align top header structure to target block order:
  - left shell title/menu
  - product identity + badge
  - metadata row
  - progress block
  - metrics band
  - updated timestamp + refresh control
- Align top readiness strip to target sequence and wording (English).
- Keep filter row controls but reorder/compact to target hierarchy.
- Keep Matrix/Step and bottom three surfaces in same runtime-console flow; adjust section titles/copy to match target-equivalent English.
- Do not add new state sources or behavior branches.

## 5.2 `frontend/src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx` (conditional)

- Apply minimal structure/copy adjustments only if matrix title, table frame, or caption cannot be aligned from parent layout/CSS alone.
- Keep existing read-only projection mapping unchanged.

## 5.3 `frontend/src/workbench.css`

- Adjust spacing, grids, widths, paddings, card heights, and typography rhythm to match target.
- Tighten header and readiness strip density.
- Align matrix-left / step-right split proportions.
- Align bottom three-surface proportions and card density.
- Keep existing token direction and current design language; no redesign styling.

## 5.4 `tests/unit/test_frontend_shell_files.py`

- Add or update static assertions for TASK_220 target structure:
  - required section labels/landmarks
  - forbidden legacy panels still absent
  - runtime-console section ordering expectations
- Keep tests bounded to TASK_220 scope; do not rewrite unrelated historical tests.

## 6. Component Reuse Strategy

- Reuse existing runtime console components and surfaces:
  - matrix overview
  - step workspace
  - runtime attention
  - recent activity
  - fee estimate
- Prefer JSX structure and CSS alignment over introducing new component abstractions.
- Only extract small local helper markup when duplication is unavoidable.

## 7. Risk and Guardrails

Primary risks:

- Accidental redesign instead of alignment.
- Reintroducing removed legacy support/process panels.
- Unintended behavioral coupling from JSX restructuring.

Guardrails:

- Target image treated as visual contract.
- Keep data bindings unchanged.
- Keep readonly/runtime boundaries unchanged.
- Validate forbidden panel absence by static tests and manual smoke.

## 8. Validation Plan

Required:

```powershell
cd frontend
npm run build
```

Targeted tests:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task220 or task219 or task188 or task190"
```

Recommended board/governance checks after completion:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 9. Manual Smoke Checklist

1. Open Project Workbench route with runtime sample data.
2. Compare against `Project workbench UI.png` for:
3. Header structure and density.
4. Top readiness strip structure.
5. Filter row ordering and compactness.
6. Matrix overview dominance on left.
7. Step workspace structure and action layout on right.
8. Bottom Runtime attention / Recent activity / Fee estimate proportions.
9. Confirm removed legacy lower workflow panels do not appear.
10. Confirm `Edit Matrix` navigation still works.

## 10. Done Criteria

Task implementation is done only when:

- Target visual hierarchy is matched without redesign drift.
- Runtime Console framing remains intact.
- No backend/API/domain changes are introduced.
- Build passes and targeted tests pass.
- Manual smoke checklist passes.

## 11. Stop Point

This document is the implementation plan deliverable for `TASK_220`.
Per protocol, implementation code changes must wait for explicit user approval.
