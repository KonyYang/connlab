# TASK_MATRIX_IMPORT_DEFAULT_SOURCE_DIRECTORY

Status: `planned` / `bounded_scope_amendment_pending_user_approval`

Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Goal

Make the Matrix Editor `Import Matrix` action open the native desktop file picker at the most
useful project-owned directory:

1. use `<official project folder>/Submitted Material` when that directory exists;
2. otherwise use the directory containing the project's stored intake attachments;
3. otherwise keep the operating system's normal picker location.

The browser-only development path must remain usable through the existing upload input because a
web page cannot set an arbitrary native file-picker starting directory.

## Confirmed Root Cause

- `MatrixEditorWorkspace` currently clicks a hidden HTML `input[type=file]`.
- Browser security does not let JavaScript assign an arbitrary initial directory to that picker.
- ConnLab's PyWebView bridge can open a native dialog with a `directory` argument, but its current
  contract only exposes Settings resource selection and has no project-scoped Matrix source action.
- Existing project data already records both official workspace paths and controlled intake asset
  paths, so no new persistence or schema is needed.

## Approved Behavior To Review

- The preferred directory is resolved read-only from existing project records.
- An existing `Submitted Material` directory has priority over intake attachment storage.
- Only an existing project-owned attachment parent may be used as the pre-folder fallback.
- Missing or inaccessible preferred directories do not block import; the native picker falls back
  to its normal location.
- In the packaged/PyWebView desktop, a selected local path uses the existing path-preview API.
- In an ordinary browser, ConnLab retains the current upload picker and upload-preview flow.
- Supported source formats remain `.pdf`, `.doc`, and `.docx`.
- Cancel writes nothing and leaves the current Matrix editor state unchanged.

## May Touch

1. `backend/application/project_test_plan_source_candidate_service.py`
2. `backend/api/routes_project_test_plan_source_candidates.py`
3. `backend/api/dependencies.py`
4. `backend/desktop/path_picker_api.py`
5. `backend/desktop/shell.py`
6. `frontend/src/api/client.ts`
7. `frontend/src/desktop/pathPickerBridge.ts`
8. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
9. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
10. `tests/unit/test_matrix_source_candidate_service.py`
11. `tests/integration/test_project_test_plan_source_candidates_api.py`
12. `tests/unit/test_desktop_path_picker_api.py`
13. `tests/unit/test_frontend_shell_files.py`
14. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
15. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
16. `backend/api/routes_project_test_plan.py`
17. `tests/integration/test_project_test_plan_preview_api.py`
18. `docs/task_board.md`

Role evidence uses the fixed task-derived Developer, Reviewer, QA, and Integrator evidence paths.

## Must Not Touch

- Database models, schema, migrations, repositories, or intake storage layout.
- Matrix parsing, Matrix authority, commit/confirm behavior, standard-version synchronization, or
  public-drive workflows.
- Project-folder creation, request-material copying, product/backend business rules, or settings
  resource semantics.
- Any new endpoint unrelated to the existing source-candidate/path-preview boundary.
- Real project files, public-drive files, retained branches/worktrees/evidence, or other tasks.
- Push, cleanup, archive, retire, reset, restore, stash, rebase, or destructive actions.

## Acceptance

1. Desktop import starts in existing `Submitted Material` after official folder creation.
2. Before official folder creation, desktop import starts in the existing stored-attachment parent.
3. Official folder priority is deterministic even when intake attachments still exist.
4. Missing project, missing attachment, missing directory, or unavailable desktop bridge fails safe
   to existing browser/OS behavior without mutating Matrix state.
5. Desktop selection previews by exact local path; browser selection preserves the current upload
   preview and locator/replacement behavior.
6. Cancel, unsupported source, and read-only lifecycle behavior do not regress.
7. Existing source-candidate ranking and project ownership checks remain intact.
8. The existing `matrix-preview-from-path` request accepts the already-supported locator page,
   table-on-page index, and table-text query values and passes them unchanged into
   `MatrixPreviewFromPathCommand`.
9. Local-path reparse and upload reparse preserve the same locator behavior, and executable
   Workspace regressions cover desktop selection, browser fallback, read-only state, and cancel
   with no Matrix-state mutation.

## Bounded Scope Amendment

Reviewer R1 proved that the original frontend/API-client allowlist could not truthfully preserve
locator inputs on the local-path flow: `MatrixPreviewFromPathCommand` already supports the values,
but the existing FastAPI request schema and route omit them. The User therefore authorized exactly
two additional paths:

- `backend/api/routes_project_test_plan.py`
- `tests/integration/test_project_test_plan_preview_api.py`

This amendment does not authorize a new endpoint, parser change, persistence change, Matrix
authority change, or any additional path. The current `DEVELOPER_BLOCKED` state and all candidate
evidence remain frozen until the amended committed Plan is explicitly approved.

## Required Route

After explicit approval: `Developer -> Reviewer -> QA -> Integrator`, using
`gpt-5.6-sol / medium / risk:cross_frontend_backend`. Stop at
`implemented_pending_human_review`; do not auto-close or push.
