# TASK_350B_MATRIX_IMPORT_STALE_PREVIEW_REPARSE_GUARD

Status: complete - Integrator accepted
Lane: matrix-import-stale-preview-reparse-guard
Owner: Planner / Reviewer
Created: 2026-07-04

## Goal

Prevent Matrix Editor `Import Matrix` from committing a stale preview when the operator changes the import locator inputs after a successful parse. If `Replace` is clicked while the current Page / Table on page / Table Title Keyword inputs differ from the locator snapshot that produced the current `importPreview`, the UI must automatically run Reparse with the current locator first. Only a successful auto-Reparse with usable Matrix groups may continue into the original Replace/commit path.

## Why This Is A Formal Follow-Up Lane

This is a narrow frontend follow-up, but it protects Matrix authority import correctness. It changes commit readiness for Matrix import and must be reviewed through the normal lane gates instead of being folded into the already accepted TASK_350A package.

## Current Facts

- TASK_350A is complete/accepted and added `.doc,.docx` compatibility to Matrix import.
- `MatrixEditorWorkspace.tsx` currently stores `locatorPage`, `locatorTableOnPage`, `locatorKeyword`, `importPreview`, `importingPreview`, and `committingImport`.
- Initial file preview success sets locator fields from preview metadata and opens the import dialog.
- Reparse already validates positive Page / Table on page values and calls `previewProjectTestPlanMatrixFromUpload` with current locator inputs.
- Current `Replace` disabled condition is `isLifecycleReadonly || importingPreview || !importPreview || importPreview.groups.length === 0`.
- Current locator inputs are disabled only by lifecycle readonly state.
- There is no `lastParsedLocator` snapshot and no stale-preview guard before `commitMatrixImport`.

## Scope

In scope:

- Add `lastParsedLocator: { page, tableOnPage, keyword }` state or equivalent local model.
- Update `lastParsedLocator` after initial file preview succeeds and after Reparse succeeds.
- Compute `isPreviewStale` by comparing current locator fields against `lastParsedLocator`.
- Keep `Replace` available for a stale preview when a current preview with groups exists, then make stale Replace auto-Reparse before commit.
- On stale Replace, validate the current locator, call the same preview flow as Reparse, update `importPreview` and `lastParsedLocator` on success, then continue the original Replace/commit with the refreshed preview.
- On stale Replace auto-Reparse failure, invalid input, page/table mismatch, or no usable Matrix groups, keep the dialog open, show the in-dialog error/result, and do not commit.
- Disable locator inputs, Reparse, Replace, and Append while Reparse or Replace/commit work is running.
- Keep manual Reparse as an explicit preview refresh path.
- Keep existing Reparse validation and in-dialog error behavior.
- Add focused frontend tests.

Out of scope:

- Backend changes.
- API client changes.
- Matrix parser or preview service changes.
- TASK_350A `.doc` conversion behavior.
- Confirmed Matrix, Fee, Test Record, lifecycle, Folder Actions, Intake/LTR, Projects, release/settings cleanup, or unrelated UI polish.

## May Touch

- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- TASK_350B task, plan, evidence, and `docs/task_board.md` through normal lane flow.

## Must Not Touch

- `backend/**`
- `frontend/src/api/client.ts`
- Matrix parser rules and backend preview service.
- Confirmed Matrix, Fee Evaluation, Test Record generation, lifecycle semantics.
- TASK_350A `.doc` conversion backend flow.
- Folder Actions / public folder workflow.
- Intake / LTR workflow.
- Projects registry/list.
- Release/settings cleanup and unrelated residuals.
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

- Initial file preview success records the parsed locator snapshot.
- Reparse success records the parsed locator snapshot that matches the current inputs.
- Editing Page, Table on page, or Table Title / Content Keyword after a successful preview marks the preview stale.
- `Replace` remains clickable for a stale preview when a current preview with groups exists and the modal is not readonly/busy.
- Clicking `Replace` while stale automatically runs Reparse with the current locator fields before any commit.
- Stale Replace auto-Reparse success with usable Matrix groups updates `importPreview`, updates `lastParsedLocator`, then continues the original Replace/commit path.
- Stale Replace auto-Reparse failure, invalid Page/Table input, page/table mismatch, or no usable Matrix groups keeps the dialog open, displays the in-dialog error/lookup result, and does not call commit.
- Non-stale `Replace` commits the current `importPreview` directly without calling preview/reparse.
- `Replace` is disabled while Reparse or commit is running.
- Locator inputs and Reparse are disabled while Reparse or commit is running.
- Manual Reparse remains available as an explicit refresh path and preserves existing in-dialog validation behavior.
- Existing positive integer and page/table mismatch validation remains visible in the dialog.

## Validation Gate

Developer must update evidence and run focused validation proving:

- Stale locator edits mark the preview stale without making `Replace` a dead end.
- Stale `Replace` auto-Reparse success refreshes `importPreview`, updates `lastParsedLocator`, and then commits the refreshed preview.
- Stale `Replace` auto-Reparse failure, invalid Page/Table input, page/table mismatch, or no usable Matrix groups does not call commit and shows the error/result in the dialog.
- Non-stale `Replace` commits directly without another preview call.
- Manual Reparse still refreshes `importPreview` and `lastParsedLocator`.
- Reparse/commit busy state disables locator inputs, Reparse, Replace, and Append.
- Existing import modal, `.doc,.docx` accept behavior, Replace commit, and Append-disabled tests remain green.
- `npm test -- MatrixEditorWorkspace --run` passes.
- `npm run build` passes, or unrelated pre-existing build blockers are documented.

## Merge Gate

- Reviewer plan re-gate passed on the updated auto-Reparse-on-Replace behavior before Developer planning-first.
- User approved Developer planning-first; Developer planning-first completed.
- Reviewer implementation-readiness passed.
- User approved source-of-truth reconciliation and Developer implementation.
- Developer implementation is authorized for the TASK_350B frontend-only MatrixEditorWorkspace behavior/tests scope; implementation is not complete.
- Reviewer implementation gate must verify no backend/API/parser/Matrix authority semantic change.
- QA should run focused frontend tests and, if available, browser smoke on the reported Matrix Editor import modal path.
- Integrator may package only TASK_350B-scoped files and must exclude release/settings/New Project residuals.

## Integrator Closeout

Closed on 2026-07-05:

- Reviewer implementation gate passed.
- QA gate passed with no blocking findings.
- Integrator accepted the package after focused MatrixEditorWorkspace tests, frontend build, staged diff check, staged whitelist/forbidden-path checks, trailing whitespace scan, and static scope scans.
- Package includes only `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`, `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`, TASK_350B task/plan/evidence/reconciliation docs, and `docs/task_board.md` closeout.
- Backend, API client, parser/preview route/service, TASK_350A conversion backend, Workbench/Projects/New Project, Settings/LTR, desktop/release/packaging, temp-stash, `.agents/**`, and `docs/project_management/**` residuals were excluded.
- Browser smoke remains a non-blocking QA residual because no direct browser control and no prepared safe Matrix import fixture were available in the QA thread; focused component/source coverage passed.
- Remote push was intentionally not performed.
