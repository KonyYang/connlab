# TASK_350C Matrix Import Remove Native Confirm Guard Plan

Status: complete - Integrator accepted
Task: `TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD`
Lane: `matrix-import-remove-native-confirm-guard`
Created: 2026-07-05

## 1. Discovery Gate

Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.

Current active task/lane: `TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD` / `matrix-import-remove-native-confirm-guard`, Planner Discovery / formal planned lane creation only.

Current role: ConnLab Planner.

Why allowed: Orchestrator routed a new Planner Discovery / lane creation request after TASK_350A and TASK_350B were accepted, and explicitly prohibited product-code changes or Developer routing.

## 2. User Goal

The user sees a browser-native confirmation dialog when clicking `Import Matrix` on the Matrix Editor page. The user does not want this browser confirm before the existing import flow. `Import Matrix` should directly enter the existing file input / import modal path, while lifecycle readonly blocking, TASK_350A `.doc,.docx` compatibility, and TASK_350B stale Replace auto-Reparse behavior remain intact.

## 3. Evidence Read

- `AGENTS.md`
- `docs/task_board.md`
- `.agents/skills/connlab-planner/SKILL.md`
- `.agents/skills/impeccable/SKILL.md`
- `$impeccable` `PRODUCT.md` / `DESIGN.md` context, register: product
- `.agents/skills/impeccable/reference/product.md`
- `docs/project_management/PLANNER_DISCOVERY_PROTOCOL.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- Current `git status --short`

## 4. Confirmed By User

- The observed page is `http://localhost:5173/projects/1ee3f8389c2243b0b324247ae5555bd3/matrix-editor`.
- The browser-native confirm text appears when clicking `Import Matrix`.
- The user says the frontend does not need this confirm.
- The desired behavior is to remove the native confirm and proceed to the existing import flow.
- TASK_350A `.doc,.docx` behavior and TASK_350B stale Replace auto-Reparse behavior must remain.
- Backend/API/parser/Matrix authority semantics must not change.

## 5. Confirmed By Repository Evidence

- `docs/task_board.md` records TASK_350A complete/accepted.
- `docs/task_board.md` records TASK_350B complete/accepted after Reviewer, QA, and Integrator.
- `MatrixEditorWorkspace.tsx` contains `window.confirm(...)` in `onChangeSourceMatrix()`.
- The confirm has two message variants:
  - `Import Matrix will replace the current source session. Unsaved edits will be lost. Continue?`
  - `Import Matrix will replace the current source session. Continue?`
- `onChangeSourceMatrix()` checks `isLifecycleReadonly` first and sets `importError(lifecycleReadonlyView.message)` before the confirm.
- `openChooseDocx()` is the existing path into the file input/import flow.
- `onCancelEditing()` has a separate discard confirmation. That is a different action and should remain locked out of TASK_350C.
- Current tests already spy on `window.confirm` globally and cover Import Matrix, `.doc,.docx` accept, Replace, Reparse, and lifecycle readonly behavior.

## 6. Planner Inferences

- This lane can be frontend-only and localized to `MatrixEditorWorkspace.tsx` plus focused tests.
- No backend/API/client/parser changes are needed.
- Removing only the `onChangeSourceMatrix()` confirm should not affect TASK_350A or TASK_350B if tests cover import accept and stale Replace/Reparse regressions.
- Because `MatrixEditorWorkspace.tsx` has recent accepted TASK_350A/B history, implementation should isolate a small hunk and avoid mixing external residuals.

## 7. Not Yet Confirmed

None blocking for a planned lane. The request is narrow enough to proceed to Reviewer plan gate.

## 8. Definition Of Ready

DoR is satisfied for a planned lane and Reviewer plan gate:

- User scenario is clear.
- Current code location is verified.
- Dependencies are complete: TASK_350A and TASK_350B are accepted.
- Scope is narrow and testable.
- May Touch / Must Not Touch / Locked Paths are concrete.
- Acceptance criteria are explicit.
- At least one non-goal prevents scope creep: do not remove unrelated native confirms.

This is not implementation approval.

## 9. Implementation Design Recommendation

Target behavior:

- `onChangeSourceMatrix()` should keep the lifecycle readonly guard:
  - if readonly, set the existing readonly import error and return.
- If not readonly, call `openChooseDocx()` directly.
- Remove the `warning` variable and the `window.confirm(warning)` branch from `onChangeSourceMatrix()`.
- Do not remove or alter `onCancelEditing()` discard confirmation.

Test design:

- Spy on `window.confirm`.
- Click `Import Matrix`.
- Assert `window.confirm` was not called.
- Assert the file input exists and remains the existing import path.
- Assert file input `accept` remains `.doc,.docx`.
- Add or preserve lifecycle readonly test coverage showing Import Matrix stays blocked and does not open the file picker.
- Keep TASK_350B stale Replace/Reparse tests green.

## 10. May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `tasks/TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD.md`
- `docs/task_350c_matrix_import_remove_native_confirm_guard_plan.md`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_*.md`
- `docs/task_board.md` through normal lane flow.

## 11. Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts`
- Matrix parser rules.
- Backend preview service and routes.
- TASK_350A `.doc` conversion backend flow.
- TASK_350B stale Replace auto-Reparse semantics, except regression tests proving preservation.
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, lifecycle semantics.
- Folder Actions / public folder workflow.
- Intake / LTR workflow.
- Projects registry/list.
- Release/settings/basic-information cleanup and unrelated residuals.
- `.agents/**`
- `docs/project_management/**`

## 12. Locked Paths

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

## 13. Acceptance Criteria

- Clicking `Import Matrix` in an editable Matrix Editor does not call `window.confirm`.
- Clicking `Import Matrix` still opens the existing file input / import flow.
- File input `accept` remains `.doc,.docx`.
- Lifecycle readonly state still blocks Import Matrix and surfaces the existing readonly message/disabled behavior.
- TASK_350B stale Replace auto-Reparse behavior remains green.
- Unrelated native confirms, including Cancel/discard editing confirmation, are not changed.

## 14. Validation Plan

Focused frontend tests:

- `Import Matrix` click does not call `window.confirm`.
- `Import Matrix` still reaches the existing file input / import flow.
- `.doc,.docx` accept regression remains green.
- Lifecycle readonly regression remains green.
- TASK_350B stale Replace auto-Reparse tests remain green.

Suggested commands:

- `npm test -- MatrixEditorWorkspace --run`
- `npm run build`
- `git diff --check` on TASK_350C package files
- trailing whitespace scan on TASK_350C package files
- forbidden-scope status proving no backend/API-client/parser/preview service/Workbench/Projects/Intake-LTR/release/governance changes

Manual smoke:

- Browser smoke at the reported Matrix Editor route if local data/server are available: click `Import Matrix`, confirm no browser-native confirm appears, and verify the existing import flow starts.

## 15. Source / Package Isolation Risks

- `MatrixEditorWorkspace.tsx` is a large file with recent TASK_350A/B history; Developer must isolate only the `onChangeSourceMatrix()` confirm-removal hunk and focused tests.
- Current status shows external release/settings/basic-information/New Project residuals outside this lane. They must remain excluded.
- If `MatrixEditorWorkspace.tsx` is dirty before implementation, stop and record package-isolation risk before editing.

## 16. Blockers

None for planned lane creation.

Next legal role: Developer planning-first.

## 17. Planner Source-Of-Truth Reconciliation

Date: 2026-07-05

Reconciliation facts:

- Reviewer plan gate passed for TASK_350C.
- Reviewer confirmed TASK_350C is a frontend-only planned lane that removes only the Matrix Editor `Import Matrix` entry `window.confirm` guard.
- Reviewer confirmed lifecycle readonly, existing file input/import flow, TASK_350A `.doc,.docx`, TASK_350B stale Replace auto-Reparse, backend/API/parser/Matrix authority locks, and unrelated confirm behavior remain protected.
- User approved TASK_350C for Developer planning-first.
- Developer blocked before planning-first because local source-of-truth still recorded TASK_350C as planned / ready for Reviewer plan gate.

Reconciled status:

- TASK_350C is now Developer planning-first authorized.
- Product implementation remains not authorized.
- Developer planning-first must remain docs/evidence/planning only.

Scope locks remain:

- No product code implementation during planning-first.
- No `backend/**`.
- No `frontend/src/api/client.ts`.
- No Matrix parser, backend preview service, or preview route changes.
- No TASK_350A `.doc` conversion backend flow changes.
- No TASK_350B stale Replace auto-Reparse semantic changes.
- No Confirmed Matrix, Fee Evaluation, Test Record generation, lifecycle semantics, Folder Actions / public folder workflow, Intake / LTR workflow, Projects registry/list, release/settings/basic-information cleanup, `.agents/**`, or `docs/project_management/**`.

## 18. Developer Planning-First Refinement

Date: 2026-07-05

Developer planning-first status:

- Developer planning-first is complete.
- Product implementation remains not authorized.
- Next gate should be Reviewer implementation-readiness.

Implementation strategy for the later approved implementation pass:

1. Work only in `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx` and focused tests.
2. In `onChangeSourceMatrix()`, preserve the existing lifecycle readonly guard:
   - if `isLifecycleReadonly`, keep `setImportError(lifecycleReadonlyView.message)` and return.
3. Remove only the `warning` constant and `window.confirm(warning)` branch from `onChangeSourceMatrix()`.
4. Let editable `Import Matrix` clicks call `openChooseDocx()` directly.
5. Do not change `openChooseDocx()`, file input wiring, import preview modal, Reparse, Replace, Append, commit, or stale-preview behavior.
6. Do not change the separate `onCancelEditing()` discard `window.confirm(...)`.

Focused test strategy:

- Add a regression test that clicks `Import Matrix`, verifies `window.confirm` is not called, and verifies the existing hidden file input remains available.
- Keep or update the `.doc,.docx` accept regression.
- Keep TASK_350B stale Replace auto-Reparse tests green:
  - stale Replace auto-Reparses current locator before commit
  - auto-Reparse failure does not commit
  - invalid locator does not reparse or commit
  - manual Reparse refreshes locator snapshot
  - busy state disables locator/actions during stale Replace Reparse
- Keep lifecycle readonly coverage green; readonly Import Matrix should remain disabled or blocked by the existing readonly state and must not start the import flow.
- Keep any existing test that relies on `window.confirm` for Cancel/discard editing unchanged.

Exact implementation May Touch for the later implementation pass:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`

Docs/board through later normal gate flow only:

- `docs/task_350c_matrix_import_remove_native_confirm_guard_plan.md`
- `tasks/TASK_350C_MATRIX_IMPORT_REMOVE_NATIVE_CONFIRM_GUARD.md`
- `docs/task_board.md`

Locked paths remain unchanged:

- `backend/**`
- `frontend/src/api/client.ts`
- Matrix parser rules and backend preview service/routes
- TASK_350A `.doc` conversion backend flow
- TASK_350B stale preview auto-Reparse semantics except regression coverage
- Confirmed Matrix authority, Fee Evaluation, Test Record generation, lifecycle semantics
- Folder Actions / public folder workflow
- Intake / LTR workflow
- Projects registry/list
- Release/settings/basic-information cleanup and unrelated residuals
- `.agents/**`
- `docs/project_management/**`

Implementation validation commands for the later pass:

- Red/green focused frontend test cycle for the new no-native-confirm test.
- `npm test -- MatrixEditorWorkspace --run`
- `npm run build`
- `git diff --check -- frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`
- trailing whitespace scan on the same package files
- targeted forbidden-scope status proving no backend/API-client/parser/preview service/Workbench/Projects/Intake-LTR/release/governance changes

Browser smoke expectation:

- If browser tooling and a safe local Matrix Editor route are available during implementation or QA, click `Import Matrix` and verify no browser-native confirm appears before the existing file input/import flow.
- If browser tooling is unavailable, record the tooling blocker for QA.

Package isolation note:

- Current workspace status includes external board, New Project, Settings/LTR, desktop/release, packaging, and TASK_350C Planner residuals. They remain outside TASK_350C implementation packaging.
- Current `MatrixEditorWorkspace.tsx` and `MatrixEditorWorkspace.test.tsx` showed no TASK_350C product diff during Developer planning-first inspection.

## 19. Planner Implementation Authorization Reconciliation

Date: 2026-07-05

Reconciliation facts:

- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed and recorded evidence in `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`.
- Reviewer implementation-readiness passed.
- User approved TASK_350C reconciliation and Developer implementation.

Reconciled status:

- TASK_350C is now implementation authorized / pending Developer implementation.
- This is not completion and does not bypass Reviewer implementation gate, QA gate, or Integrator packaging.

Authorized implementation boundary:

- Remove only the `window.confirm(...)` branch from `onChangeSourceMatrix()` in `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`.
- Keep lifecycle readonly guard and readonly message behavior.
- Editable `Import Matrix` clicks should proceed directly to `openChooseDocx()` / existing file input and import flow.
- Preserve TASK_350A `.doc,.docx` compatibility.
- Preserve TASK_350B stale Replace auto-Reparse behavior.
- Preserve unrelated `onCancelEditing()` / discard current Matrix edits confirm.

Authorized future implementation May Touch:

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `docs/lane_evidence/TASK_350C_matrix-import-remove-native-confirm-guard_developer.md`
- TASK_350C task/plan/evidence/board through normal lane flow

Scope locks remain:

- No `backend/**`.
- No `frontend/src/api/client.ts`.
- No Matrix parser, backend preview service, or preview route changes.
- No TASK_350A Word COM / `.doc` conversion backend flow changes.
- No Confirmed Matrix, Fee Evaluation, Test Record generation, lifecycle business semantics, Folder Actions / public folder workflow, Intake / LTR workflow, Projects registry/list, release/settings/basic-information cleanup, `.agents/**`, or `docs/project_management/**`.

Next legal role: Developer implementation pass.

## 20. Integrator Closeout

Date: 2026-07-05

Outcome:

- Integrator gate: accepted.
- Reviewer implementation gate: pass.
- QA gate: pass.
- Package readiness validated with focused MatrixEditorWorkspace tests (`36 passed`), frontend build, staged diff check, staged whitelist/forbidden-path checks, trailing whitespace scan, and static scope scans.
- The accepted package is frontend-only and removes only the Matrix Editor `Import Matrix` entry native confirm branch.
- Editable `Import Matrix` now proceeds directly to `openChooseDocx()` / existing file input flow after lifecycle readonly guard.
- The separate `Discard current Matrix edits and return to Workbench?` confirm remains outside this lane and is preserved.
- No backend/API client/parser/preview route/service changes, no TASK_350A conversion backend changes, no TASK_350B stale Reparse semantic changes, no Workbench/Projects/New Project/Intake scope, no release/settings/basic-information cleanup, no `.agents/**`, and no `docs/project_management/**` were packaged.
- Browser smoke remains a non-blocking QA residual because direct browser automation was unavailable; focused tests and source/static checks cover no-native-confirm behavior.
- Remote push was intentionally not performed.
