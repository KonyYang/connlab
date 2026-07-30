# TASK_368A Quick Fixer Evidence

Date: 2026-07-31
Task: `TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX`
Lane: `task-368a-product-spec-matrix-import-quick-fix`
Role: permanent Quick Fixer
Status: `ready_for_review`

## Authorization

- User instruction in permanent Quick Fixer thread:
  `综合上面的讨论，请开始解决这个问题。`
- Orchestrator decision: Quick Fixer fast path is allowed because reproduction, root cause,
  expected behavior, non-goals, ownership, and validation are explicit.
- Four existing product files are accepted as one bounded defect chain. Any fifth existing
  production file requires a stop and Orchestrator review.

## Discovery Evidence

- Correct Matrix: document table 6, page 10, table 1.
- Extracted header defect: `SECTION` becomes `SECTIO N`.
- False positive: table 7, page 11 Revision Record.
- Guard gap: singular `Page`.
- Score trigger: revision text contains `CHANGE GROUP P TEST ITEM`.
- Locator gap: Page + Keyword ignores Page.
- Diagnostic gap: frontend mismatch hides the backend blocker.
- Baseline parser suite reported by the read-only diagnosis: `24 passed`.

## Ownership

- Product/test ownership is exactly the task May Touch list.
- `docs/task_board.md` is Orchestrator-owned before dispatch and Integrator-owned at closeout.
- Browser-release and frozen V2 worktrees remain read-only.
- Real user files remain external and read-only.

## Worktree

- Branch: `lane/task-368a-product-spec-matrix-import-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368a-product-spec-matrix-import-quick-fix`
- Base commit: `6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7`
- Dispatch verification: branch and HEAD matched the recorded base; worktree and index were clean.
- Quick Fixer implementation checkpoint:
  `a3d77c789bfe21c1b90e9e36f7f78913dfea8223`.

## TDD Record

RED:

- `py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py -q`
  produced `4 failed`: the Revision Record was selected, Page + Keyword searched globally,
  an explicit locator miss fell back to parser scoring, and an invalid selected table lost its
  requested page/table metadata.
- After making the worktree's ignored `frontend\node_modules` junction point to the already
  installed primary-worktree dependencies,
  `npm test -- MatrixEditorWorkspace.test.tsx -t "shows a precise preview blocker before locator mismatch fallback"`
  produced `1 failed, 44 skipped`: the generic locator mismatch hid the backend blocker.

GREEN:

- `py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py -q`
  produced `4 passed`.
- The focused frontend RED command produced `1 passed, 44 skipped`.

## Changed Paths

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `tests/unit/test_task_368a_product_spec_matrix_import_selection.py`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- This evidence file.

No task-board, API/DTO/client, Office gateway, real document, data, persistence, schema, release,
layout, style, or label path was changed.

## Validation

- `py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py tests\unit\test_product_spec_matrix_parser.py -q`
  -> `28 passed`.
- `py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py backend\application\project_test_plan_matrix_preview_service.py`
  -> passed with exit code `0`.
- In `frontend`,
  `npm test -- MatrixEditorWorkspace.test.tsx`
  -> `45 passed`.
- In `frontend`, `npm run build`
  -> passed. Vite reported its existing non-blocking chunk-size warning.
- `git diff --check` and `git diff --cached --check`
  -> passed; only Git's Windows LF-to-CRLF working-copy notices were emitted.
- Final exact-path commits leave `git status --short` empty, proving worktree and index clean.

## Residuals And Handoff

- Product residuals/blockers: none.
- Environment note: the ignored worktree-local `frontend\node_modules` junction was used only to
  reuse already installed dependencies; it is not a tracked product change.
- Remote state: not pushed, per task boundary.
- Next role: Reviewer.
