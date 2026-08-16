# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH

Status: `planned` / `ready_for_user_approval`

## Goal

Complete the ordinary-browser Matrix Import source picker so it lists only direct regular `.doc`,
`.docx`, and `.pdf` files from the existing resolved email-attachment or `Submitted Material`
directory. Show only a concise source-location title and filenames, preserve explicit selection,
Cancel, Upload other file, loading/empty/error/read-only states and desktop native picker behavior,
and reject stale in-place same-name replacements without exposing paths or adding persistence.

## Confirmed retained starting point

- Retained branch: `codex/task-matrix-import-source-picker-target-folder-file-list`.
- Retained worktree:
  `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list`.
- Clean retained subject: `163e31d455eb4af12e606288fa36d387c81f1476`.
- Retained parent/base: `900c26a78009264ab0fc06f2c038e50d6d280869`.
- The base-to-subject diff contains exactly the 12 product implementation/test paths in this Task.
- Historical focused results were 12 backend and 54 frontend tests passed.
- The corrected authoritative backend/API/preview manifest check exited 1, but its failed pytest node
  and trace were not captured.
- Static inspection confirms the retained opaque ID binds project, source kind, canonical directory
  and filename, but does not bind the current file instance/content. An in-place same-name replacement
  can therefore retain the old ID.

## Required behavior

1. The ordinary browser Matrix Editor alone requests the existing GET/POST source-candidate endpoints'
   bounded `resolved_directory` view. Existing registered-asset callers remain unchanged.
2. Resolve the existing preferred source directory: existing `Submitted Material` first, otherwise the
   deterministic parsed email-attachment directory, otherwise unavailable.
3. Enumerate direct regular children only, case-insensitively limited to `.doc`, `.docx`, and `.pdf`;
   do not recurse, follow escaped links, copy, register, convert or persist candidates.
4. Sort deterministically by filename.
5. Keep opaque IDs path-free and directory-bound. Bind them to the project, source kind, canonical
   resolved-directory identity, exact filename and current file-instance/content fingerprint.
6. POST selection must re-resolve and re-enumerate the directory. Reject stale, foreign, renamed,
   deleted, moved, same-name-in-another-directory, in-place same-name-replaced, escaped, unsupported
   and nested targets before Matrix preview.
7. Title the picker `Submitted Material files`, `Email attachment files`, or
   `Project source files`. Candidate rows show filenames only.
8. Preserve explicit selection, Cancel, Upload other file, loading, empty, error, busy/focus,
   read-only zero-call behavior, cancel zero-state-change and the desktop native picker path.
9. Preserve existing preview/parser capability, including the existing `.doc` deferred/conversion
   behavior. Matrix authority and persisted provenance remain unchanged.

## Exact approved scope (20 paths)

1. `backend/application/project_test_plan_source_candidate_service.py`
2. `backend/api/routes_project_test_plan_source_candidates.py`
3. `frontend/src/api/client.ts`
4. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx`
5. `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx`
6. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
7. `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
8. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
9. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
10. `frontend/src/workbench.css`
11. `tests/unit/test_matrix_source_candidate_service.py`
12. `tests/integration/test_project_test_plan_source_candidates_api.py`
13. `tasks/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH.md`
14. `docs/task_matrix_import_source_picker_target_folder_file_list_fresh_plan.md`
15. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_planner.md`
16. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_developer.md`
17. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_reviewer.md`
18. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_qa.md`
19. `docs/lane_evidence/TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_FRESH_integrator.md`
20. `docs/task_board.md`

No governance writer/runtime path is approved.

## Developer contract

After approval, reuse the retained branch/worktree at its exact clean subject without checkout, reset,
rebase, cherry-pick, force-ref movement, restoration or recreation. First run the focused backend
candidate/API/preview command with `-x -vv` to capture the exact existing failure. Add the missing
in-place same-name replacement regression and establish a tight RED result. Implement one bounded
product-scope fix and, if required, add one child implementation commit to the retained subject.
Do not modify a frontend path unless an approved focused regression or browser check proves it is
needed.

## Required regressions

- canonical resolved-directory identity participates in opaque identity but is never exposed;
- same filename in another canonical directory rejects the old ID;
- equal-length in-place same-name content replacement rejects the old ID even if timestamp is restored;
- deleted, renamed, stale and foreign IDs reject;
- escaped/link, unsupported and nested targets cannot be listed or selected;
- list and selection resolution preserve source bytes and metadata;
- registered-asset default GET/POST behavior remains unchanged;
- source titles and filename-only rows contain no recommendation/type/reason/path metadata;
- loading, empty, error, explicit selection, Upload other file and Cancel behavior remain intact;
- read-only Matrix Editor makes zero picker/preview/upload calls;
- desktop keeps the existing native picker and initial-directory projection.

## Non-goals

No new endpoint, database, schema, migration, persistence, token registry, candidate registration,
attachment copy, recursive scan, parser/conversion change, Matrix authority change, desktop bridge
change, upload refactor, public-drive write, external-file mutation, governance-runtime change, push,
cleanup, archive, retirement, reset, restore, stash, rebase, cherry-pick or force-ref operation.

## Acceptance

- The complete initial validation manifest in the approved Plan passes on the final exact clean subject.
- Backend candidate/API/preview tests capture and close the retained failure.
- Opaque identity rejects stale in-place same-name replacements and remains path-free.
- Targeted picker/hook/Workspace tests, frontend build and Python compilation pass.
- Exact 12-product-path diff, retained subject ancestry/host identity and clean primary/task worktrees
  are proven.
- Deterministic browser smoke passes at desktop and 514 px with no horizontal overflow, runtime
  exception or forbidden console output.
- Tests prove source files remain unchanged and no prohibited external mutation occurs.
