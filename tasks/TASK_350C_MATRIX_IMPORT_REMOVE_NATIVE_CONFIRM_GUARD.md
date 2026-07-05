# TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD

Status: complete - Integrator accepted
Lane: matrix-import-remove-native-confirm-guard
Owner: Planner / Reviewer
Created: 2026-07-05

## Goal

Remove the browser-native confirmation guard from the Matrix Editor `Import Matrix` entry. Clicking `Import Matrix` should proceed directly to the existing file input / import modal flow without showing `window.confirm("Import Matrix will replace the current source session...")`.

## Why This Is A Formal Follow-Up Lane

This is a narrow frontend UI behavior follow-up after TASK_350A and TASK_350B, but it changes the operator-facing Matrix import entry path. It should be reviewed as a formal lane instead of being folded into accepted TASK_350A/TASK_350B work.

## Current Facts

- TASK_350A is complete/accepted and Matrix import accepts `.doc,.docx`.
- TASK_350B is complete/accepted and Matrix import stale Replace auto-Reparses before commit.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` still has `window.confirm(...)` inside `onChangeSourceMatrix()`.
- The native confirm appears before the existing file input / import modal flow.
- Lifecycle readonly handling already blocks `Import Matrix` via `isLifecycleReadonly` and sets the current readonly message.
- `onCancelEditing()` also has a separate discard confirmation. That is not this lane.

## Scope

In scope:

- Remove the `window.confirm(...)` call from `onChangeSourceMatrix()`.
- Preserve lifecycle readonly blocking and current readonly message behavior.
- Keep `openChooseDocx()` / existing file picker flow as the next step when not readonly.
- Add focused frontend tests proving `Import Matrix` does not call `window.confirm` and still opens the existing import flow.
- Keep existing `.doc,.docx` accept regression green.
- Keep TASK_350B stale Replace / Reparse behavior green.

Out of scope:

- Removing unrelated native confirms such as discard/cancel editing confirmation.
- Backend changes.
- API client changes.
- Matrix parser or preview service changes.
- TASK_350A `.doc` Word COM conversion behavior.
- TASK_350B stale preview/Reparse behavior changes.
- Confirmed Matrix, Fee, Test Record, lifecycle semantics, Folder Actions, Intake/LTR, Projects, release/settings cleanup, or unrelated UI polish.

## May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_350C task, plan, evidence, and `docs/task_board.md` through normal lane flow.

## Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts`
- Matrix parser rules and backend preview service/routes.
- TASK_350A `.doc` conversion backend flow.
- TASK_350B stale preview auto-Reparse semantics except regression tests proving preservation.
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, lifecycle semantics.
- Folder Actions / public folder workflow.
- Intake / LTR workflow.
- Projects registry/list.
- Release/settings/basic-information cleanup and unrelated residuals.
- `.agents/**`
- `docs/project_management/**`

## Locked Paths

- `backend/**`
- `frontend/src/api/client.ts`
- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `backend/api/routes_project_test_plan.py`
- `frontend/src/features/new-project/**`
- `frontend/src/features/project-workbench/**`
- `frontend/src/pages/ProjectListPage.tsx`
- `.agents/**`
- `docs/project_management/**`

## Acceptance Criteria

- Clicking `Import Matrix` in an editable Matrix Editor does not call `window.confirm`.
- Clicking `Import Matrix` proceeds to the existing file input / import flow.
- The file input still accepts `.doc,.docx`.
- Lifecycle readonly projects still block Import Matrix and show the existing readonly message/disabled behavior.
- TASK_350B stale Replace auto-Reparse behavior remains unchanged.
- No other `window.confirm` usage is removed unless separately approved.

## Validation Gate

Developer must update evidence and run focused validation proving:

- `window.confirm` is not called when clicking `Import Matrix`.
- The existing import file input flow still opens.
- `.doc,.docx` accept regression remains green.
- Lifecycle readonly regression remains green.
- TASK_350B stale Replace / Reparse tests remain green.
- `npm test -- MatrixEditorWorkspace --run` passes.
- `npm run build` passes, or unrelated pre-existing build blockers are documented.
- Diff/trailing whitespace/forbidden-scope checks prove no backend/API/client/parser/preview route/service changes.

## Merge Gate

- Reviewer plan gate passed before Developer planning-first.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.
- Developer implementation is authorized for the TASK_350C frontend-only Matrix Editor native confirm removal scope; implementation is not complete.
- Reviewer implementation gate must verify only the Import Matrix native confirm guard was removed.
- QA should run focused frontend tests and, if available, browser smoke on the reported Matrix Editor route.
- Integrator may package only TASK_350C-scoped files and must exclude release/settings/basic-information/New Project residuals.

## Integrator Closeout

Closed on 2026-07-05:

- Reviewer implementation gate passed.
- QA gate passed with no blocking findings.
- Integrator accepted the package after focused MatrixEditorWorkspace tests, frontend build, staged diff check, staged whitelist/forbidden-path checks, trailing whitespace scan, and static scope scans.
- Package includes only `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, TASK_350C task/plan/evidence/reconciliation docs, and `docs/task_board.md` closeout.
- The production change removes only the `Import Matrix will replace...` native confirm branch from `onChangeSourceMatrix()`; `onCancelEditing()` / `Discard current Matrix edits and return to Workbench?` remains.
- Backend, API client, parser/preview route/service, TASK_350A conversion backend, TASK_350B stale Reparse semantics, Workbench/Projects/New Project/Intake, Settings/LTR, desktop/release/packaging, temp-stash, `.agents/**`, and `docs/project_management/**` residuals were excluded.
- Browser smoke remains a non-blocking QA residual because direct browser automation was unavailable; focused regression spies on `window.confirm` and covers the user-facing behavior.
- Remote push was intentionally not performed.
