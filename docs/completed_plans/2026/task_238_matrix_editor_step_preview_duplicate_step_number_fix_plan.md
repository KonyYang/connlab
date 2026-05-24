# TASK_238 Matrix Editor Step Preview Duplicate Step Number Fix Plan

## Phase / Gate

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Active task: `TASK_238_MATRIX_EDITOR_STEP_PREVIEW_DUPLICATE_STEP_NUMBER_FIX`
- Allowed now: user-reported smoke-test defect needs controlled fix.

## Goal

Eliminate unexpected duplicate step entries in Step preview after group add/edit operations.

## Investigation Direction

Check `buildSelectedGroupStepPreviewRows` for duplicate-producing paths:

1. token parsing (`parseStepTokens`) output consumption
2. row-level flatten logic (same step number emitted multiple times per row unexpectedly)
3. state interaction between group add and step preview derivation
4. family post-processing loop mutating/duplicating rows

## Minimal Fix Strategy

Apply the smallest safe fix after root cause confirmation:

- if duplication is accidental repeated emission of identical `(groupId, stepNo, rowId)` tuple, dedupe by stable key before rendering.
- preserve legitimate cases where same step number exists across different rows (different `rowId` should remain valid).
- keep ordering deterministic (`stepNo`, then source row order).

## File-Level Changes

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- patch derivation pipeline with root-cause fix
- keep existing special-rule behavior unchanged

2. `tests/unit/test_frontend_shell_files.py`
- add TASK_238 static guard for dedupe/key integrity if applicable

## Risks

- Over-deduping could hide legitimate rows; dedupe key must include `rowId`.

## Validation

```powershell
cd frontend
npm run build
```

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task238 or task237 or matrix_editor"
```

## Out Of Scope

- redesign of Step preview UI
- backend-side validation or persistence changes
