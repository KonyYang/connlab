# TASK_MATRIX_IMPORT_SOURCE_PICKER_TARGET_FOLDER_FILE_LIST_CORRECTED_PLAN

Status: `planned` / `ready_for_user_approval`

## Correction authority

The prior product task was production-cancelled solely because its frozen Windows validation manifest used `npm` while the authoritative `shell=False` runner requires `npm.cmd`. Product behavior, exact 12 implementation/test paths, API-contract risk, model routing, browser smoke, acceptance criteria and non-goals are unchanged.

## Retained implementation

- Base: `900c26a78009264ab0fc06f2c038e50d6d280869`.
- Branch: `codex/task-matrix-import-source-picker-target-folder-file-list`.
- Worktree: `D:\PythonProject\connlab-worktrees\task-matrix-import-source-picker-target-folder-file-list`.
- Clean subject/HEAD: `163e31d455eb4af12e606288fa36d387c81f1476`.
- The subject changes exactly the 12 approved implementation/test paths.
- Historical focused results: backend 12 passed, frontend 54 passed, `git diff --check` passed. Fresh corrected-task validation and evidence remain mandatory.

## Required behavior

1. The ordinary-browser Matrix Import chooser requests the existing endpoints' bounded `resolved_directory` view; registered-asset defaults remain unchanged.
2. List only direct regular `.doc`, `.docx`, `.pdf` files from the resolved `Submitted Material` or parsed-email attachment directory.
3. Bind each opaque ID to project, source kind, canonical resolved-directory identity and exact filename; never expose or accept a path. Re-resolve on selection and reject stale, moved, foreign, escaped or same-name-in-another-directory IDs.
4. Show only a source-kind title and filename selection rows. Remove recommendation, type/source, reason, availability, subtitle and `Use this file:` copy.
5. Keep explicit selection, Cancel, Upload other file, empty/error/loading states, standard ConnLab buttons, read-only blocking, cancel zero mutation and desktop native picker behavior.
6. Preserve Matrix authority, preview/parser capability, database, persistence and project attachment storage.

## Exact implementation/test scope (12)

- `backend/application/project_test_plan_source_candidate_service.py`
- `backend/api/routes_project_test_plan_source_candidates.py`
- `frontend/src/api/client.ts`
- `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.tsx`
- `frontend/src/features/matrix-editor/MatrixImportSourceCandidatePicker.test.tsx`
- `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.ts`
- `frontend/src/features/matrix-editor/useMatrixImportSourcePicker.test.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/workbench.css`
- `tests/unit/test_matrix_source_candidate_service.py`
- `tests/integration/test_project_test_plan_source_candidates_api.py`

The eight governance paths are the Task, Plan, fixed Planner/Developer/Reviewer/QA/Integrator evidence paths and `docs/task_board.md`, for exactly 20 approved paths total.

## Non-goals

No new endpoint, database/schema/persistence, registry, attachment copy, recursive scan, parser/conversion change, Matrix authority change, desktop bridge change, upload refactor, external-file mutation, push, cleanup, reset, restore, stash, rebase, cherry-pick or ref movement.

## Execution after approval

Reuse the retained branch/worktree without moving it. A fresh Developer revalidates the unchanged subject and creates fresh evidence; then fresh Reviewer, mandatory QA and Integrator complete the normal local integration chain. Stop at `implemented_pending_human_review`.
