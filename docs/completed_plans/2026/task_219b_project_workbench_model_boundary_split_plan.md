# TASK_219B Plan - Project Workbench Model Boundary Split

## 1. Task Goal

Split the current Workbench "god hook" into explicit model boundaries so Runtime Console and Matrix Editor each consume only the state/actions they actually need.

This is a frontend-only model-boundary refactor. No backend/API/DB contract change.

## 2. Inputs / Outputs

### Inputs

- Existing hook: `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
- Workbench runtime shell consumer: `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
- Matrix Editor consumer: `frontend/src/pages/ProjectMatrixEditorPage.tsx`
- Existing selectors/helpers:
  - `projectWorkbenchVersionSelectors.ts`
  - `projectWorkbenchMatrixHelpers.ts`
  - `projectFolderResourceSelectors.ts`

### Outputs (implementation stage target)

- Runtime-focused hook type + hook (read/selection/runtime projection/model view)
- Support-focused hook type + hook (folder/approval/evidence/lookup support actions)
- Adapter layer to keep Workbench page behavior stable during migration
- Matrix Editor usage narrowed to runtime/matrix authority state only

## 3. Current Hook State Inventory

Current `useProjectWorkbenchModel` mixes at least these concern sets:

1. Project baseline/state loading
   - project/ltr/resources/folder/output summary
2. Matrix authority/candidate/edit lifecycle
   - draft loading/edit/save/validate/confirm
3. Runtime projection consumption
   - snapshot request composition/loading/error/token selection
4. Approval package support workflow
   - input state/autofill/preview/execute
5. Evidence support workflow
   - preview/place
6. Folder support refresh linkage
7. Workbench UX messaging/error global state
8. Matrix starter bootstrap flow
   - source candidates/preview/create draft

Matrix Editor currently imports the full hook and therefore inherits support-action state it does not need.

## 4. Proposed Boundary Split

## 4.1 Runtime Console Boundary

Owns only:

- project identity + baseline items
- matrix authority/candidate/current draft read state
- matrix edit lifecycle needed by runtime/map consumption
- runtime projection snapshot lifecycle
- runtime selected token lifecycle
- runtime authority sync summary
- runtime-facing message/error (scoped)
- output status summary (read-only)

Not owning:

- approval package manual input/autofill execution state
- evidence placement execution state
- folder creation panel-specific operational state

## 4.2 Support Actions Boundary

Owns:

- folder creation support state/actions
- approval package support state/actions
- evidence preview/place support state/actions
- lookup support entry state if required

Runtime read-model remains source for display-level summary; support actions remain collapsible secondary surfaces.

## 4.3 Matrix Editor Boundary

Matrix Editor should consume:

- project identity
- matrix authority/candidate summary
- runtime authority sync summary

Matrix Editor should not depend on approval/evidence/folder support internals.

## 5. File-Level Change Plan (Implementation Stage)

### New files (target)

- `frontend/src/features/project-workbench/useProjectRuntimeConsoleModel.ts`
  - runtime console model type + hook
- `frontend/src/features/project-workbench/useProjectWorkbenchSupportModel.ts`
  - support-actions model type + hook

### Updated files (target)

- `frontend/src/features/project-workbench/useProjectWorkbenchModel.ts`
  - convert to compatibility adapter/composer to avoid big-bang migration
- `frontend/src/features/project-workbench/ProjectWorkbenchLayout.tsx`
  - consume runtime model as primary; support model only for advanced support section
- `frontend/src/pages/ProjectWorkbenchPage.tsx`
  - compose runtime + support models (or compatibility model if staged)
- `frontend/src/pages/ProjectMatrixEditorPage.tsx`
  - switch to runtime/matrix-only model consumption

### Optional helper extraction (only if needed)

- `frontend/src/features/project-workbench/projectWorkbenchRuntimeProjectionHelpers.ts`
  - runtime request/sync derivation isolation

## 6. Compatibility Strategy

Use staged extraction to reduce regression risk:

1. First extract runtime model logic into new hook while keeping `useProjectWorkbenchModel` shape unchanged through delegation.
2. Then extract support model logic and pass only required fields to advanced support section.
3. Keep old exported `ProjectWorkbenchModel` temporarily as compatibility surface for page-level wiring.
4. After consumers migrate, narrow Matrix Editor to runtime-only interface.

This avoids breaking Workbench during refactor and keeps rollback small.

## 7. Matrix Editor Dependency Impact

Current impact:

- `ProjectMatrixEditorPage` reads only a subset (`project`, `runtimeAuthoritySync`) from a much larger model.

After split:

- Matrix Editor imports runtime-focused hook/type directly.
- No coupling to approval/evidence/folder support-action state.

## 8. Risks and Mitigations

1. Risk: behavior drift in approval/evidence/folder panels.
   - Mitigation: keep support state wiring unchanged in first extraction; only move ownership boundary.
2. Risk: token selection clear logic regressions.
   - Mitigation: preserve runtime projection effect logic verbatim before refactor cleanup.
3. Risk: duplicate API requests after split.
   - Mitigation: centralize shared loaders and ensure each data source has one owner.
4. Risk: message/error semantics change.
   - Mitigation: keep global user-facing copy unchanged in this task.

## 9. Rollback Plan

If regression occurs:

1. Rebind `ProjectWorkbenchPage` and `ProjectMatrixEditorPage` back to `useProjectWorkbenchModel`.
2. Keep new hooks unreferenced but retained for follow-up correction.
3. Re-run frontend build and static tests, then reattempt split in smaller increments.

No backend or schema changes means rollback is frontend-only and low-risk.

## 10. Validation Commands (Implementation Stage)

Required:

```powershell
cd frontend
npm run build
```

Recommended:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q
```

Governance board-state tests only if board text is changed:

```powershell
py -m pytest tests\unit\test_phase10a_scope_activation.py tests\unit\test_phase5_ux_decision.py tests\unit\test_phase6_scope_activation.py tests\unit\test_phase7_validation_summary.py tests\unit\test_phase9_scope_activation.py -q
```

## 11. Scope Guard

Still forbidden in TASK_219B:

- backend/API/DB changes
- Matrix authority semantics change
- runtime engine/persistence work
- UI redesign beyond wiring needed for model boundary split

## 12. Stop Condition

This document is the only deliverable in the current step.
Stop here and wait for explicit user approval before implementation.
