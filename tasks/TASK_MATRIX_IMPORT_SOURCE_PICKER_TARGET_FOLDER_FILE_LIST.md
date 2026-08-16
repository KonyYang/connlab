# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST

Status: `planned` / `ready_for_user_approval`

## Goal

Simplify the ordinary-browser Matrix Import chooser so it lists only directly selectable `.doc`,
`.docx`, and `.pdf` files from the one resolved project source folder. Identify that folder as either
parsed email attachments or the project's `Submitted Material`, show filenames only, and retain
explicit selection, `Cancel`, and `Upload other file` using existing ConnLab controls.

## Confirmed facts

- The existing resolver already prefers an existing `Submitted Material` folder, then a deterministic
  parsed-intake attachment parent.
- The current browser list does not enumerate that folder. It ranks registered `.docx` `FileAsset`
  records and renders recommendation/type/reason metadata.
- The same default registered-asset API view is used by Project Workbench and its real asset IDs are
  persisted as source provenance, so that view must remain unchanged.
- Unregistered files in the resolved folder currently have no selectable identity.
- Existing path preview owns `.doc`, `.docx`, and `.pdf` capability behavior. This task does not change
  parsers or conversion rules; legacy `.doc` keeps its existing deferred result.

## Required behavior

1. Only the Matrix browser requests a `resolved_directory` candidate view; existing callers retain the
   registered-asset default.
2. Enumerate direct regular children only, case-insensitively restricted to `.doc`, `.docx`, `.pdf`.
3. Sort by filename and include unregistered files without copying or registering them.
4. Use an opaque deterministic identity; selection must recompute the current directory and accept only
   an exact currently enumerated identity. Never accept a client path.
5. Title the chooser `Submitted Material files`, `Email attachment files`, or `Project source files`.
6. Candidate rows show only filenames. Remove recommendation, type/source, reason, availability and
   visible `Use this file:` copy.
7. Preserve `Cancel`, `Upload other file`, loading/empty/error states, explicit selection, read-only
   blocking, cancel zero-state-change, and desktop native picker behavior.
8. Use existing ConnLab primary/secondary button styles and accessible responsive list behavior.

## Exact implementation may touch

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

Task, Plan, fixed role evidence paths, and `docs/task_board.md` are permitted only for normal Personal
Serial V2 governance persistence.

## Non-goals

No new endpoint, database/schema/persistence, candidate registry, attachment registration/copying,
recursive scan, parser/conversion change, Matrix authority change, desktop bridge change, upload
refactor, automatic selection/import, generalized modal framework, public-drive write, push, or cleanup.

## Acceptance

- Browser list contains only immediate `.doc`, `.docx`, `.pdf` files from the resolved folder.
- Source title and filename-only selection render with standard controls; removed metadata is absent.
- Stale, foreign, moved, escaped, unsupported, nested, or ambiguous identities fail closed.
- Empty/error, upload fallback, cancel zero-state-change, read-only zero-call, explicit preview selection,
  and desktop behavior pass targeted tests and deterministic browser smoke.
- Targeted backend/frontend tests, production build, Python compilation, exact scope, clean worktrees,
  and `git diff --check` pass.

