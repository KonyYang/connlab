# TASK_350C Matrix Import Remove Native Confirm Guard - Planner Evidence

Task: `TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD`
Lane: `matrix-import-remove-native-confirm-guard`
Role: Planner
Status: developer planning-first authorized - implementation not authorized
Date: 2026-07-05

## Gate

Planner Discovery Gate / formal planned lane creation.

No product code, frontend runtime code, backend code, tests, API client, parser, preview service, `.agents/**`, or `docs/project_management/**` files were modified by this Planner pass.

## Sources Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` context from `PRODUCT.md` / `DESIGN.md`, register: product
- `.agents/skills/impeccable/reference/product.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Current `git status --short`

## Current Facts / Root Cause

- TASK_350A is complete/accepted and Matrix import accepts `.doc,.docx`.
- TASK_350B is complete/accepted and stale Replace auto-Reparses before commit.
- `MatrixEditorWorkspace.tsx` still contains a native `window.confirm(...)` guard in `onChangeSourceMatrix()`.
- The confirm appears before the existing file picker / import modal flow.
- `onChangeSourceMatrix()` already preserves lifecycle readonly blocking before that confirm.
- `openChooseDocx()` is the existing path into the import file picker.
- A separate `window.confirm(...)` exists in `onCancelEditing()` for discard behavior. It is not part of TASK_350C.

## Planner Decision

Create formal planned lane:

- Task: `TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD`
- Lane: `matrix-import-remove-native-confirm-guard`
- Status: `developer planning-first authorized`
- Next role: Developer planning-first

This is a formal lightweight frontend follow-up, not a quick fix, because it changes the Matrix import entry guard and must preserve accepted TASK_350A/TASK_350B behavior.

## May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_350C task/plan/evidence/board through normal lane flow

## Must Not Touch / Locked

- `backend/**`
- `frontend/src/api/client.ts`
- Matrix parser rules and backend preview service/routes
- TASK_350A `.doc` conversion backend flow
- TASK_350B stale Replace auto-Reparse semantics, except regression tests proving preservation
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, lifecycle semantics
- Folder Actions / public folder workflow
- Intake / LTR workflow
- Projects registry/list
- Release/settings/basic-information cleanup and unrelated residuals
- `.agents/**`
- `docs/project_management/**`

## Acceptance Summary

- Clicking `Import Matrix` in editable state does not call `window.confirm`.
- Clicking `Import Matrix` still starts the existing import file input / modal flow.
- `.doc,.docx` accept remains unchanged.
- Lifecycle readonly still blocks Import Matrix through existing readonly message/disabled behavior.
- TASK_350B stale Replace/Reparse behavior remains unchanged.
- No unrelated native confirm is removed.

## External Residuals Excluded

Current `git status --short` shows external release/settings/desktop/New Project residuals and release task files. No product code is changed by this Planner pass. Future TASK_350C implementation must keep those residuals excluded.

## Files Created / Updated

- `tasks/TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD.md`
- `docs/task_350c_matrix_import_remove_native_confirm_guard_plan.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_planner.md`
- `docs/task_board.md`

## Source-Of-Truth Reconciliation

Date: 2026-07-05

Reconciled facts:

- Reviewer plan gate passed.
- User approved TASK_350C Developer planning-first.
- Developer stopped before planning-first because board/task/plan/Planner evidence still showed ready for Reviewer plan gate only.
- Planner reconciled source-of-truth so Developer planning-first is authorized.
- Implementation remains not authorized.

Scope locks remain unchanged: no product code during this reconciliation, no backend/API client/parser/preview route/service, no TASK_350A `.doc` conversion change, no TASK_350B stale Replace/Reparse semantic change, no unrelated native confirm removal, no `.agents/**`, and no `docs/project_management/**`.

## Validation

- `git diff --check -- docs/task_board.md tasks/TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD.md docs/task_350c_matrix_import_remove_native_confirm_guard_plan.md docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_planner.md`: passed with Git LF/CRLF warning for `docs/task_board.md` only.
- Trailing whitespace scan on touched TASK_350C docs/board/evidence: no matches.
- Targeted status shows modified `docs/task_board.md` plus new TASK_350C task/plan/planner evidence files.
- Targeted status also shows external backend/settings/desktop/New Project residuals; this Planner pass did not edit product code and does not approve or package those residuals.
- Targeted status shows no TASK_350C product implementation file changes to `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, `frontend/src/api/client.ts`, backend parser/preview service/routes, `.agents/**`, or `docs/project_management/**`.

## Next Role

Developer planning-first.

## Stop Point

Do not route Developer implementation until Developer planning-first, Reviewer implementation-readiness, explicit user approval, and source-of-truth reconciliation complete.
