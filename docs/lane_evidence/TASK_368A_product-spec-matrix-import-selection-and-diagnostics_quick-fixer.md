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

## Reviewer Blocking Fix Pass

- Reviewer blocker evidence:
  `docs/lane_evidence/TASK_368A_product-spec-matrix-import-selection-and-diagnostics_reviewer.md`.
- Fix-pass starting HEAD:
  `016c2ebc55df577dd1640663a2e2198ae29ce0f3`; branch, worktree, and index matched
  the Orchestrator dispatch and were clean.
- Blocking cause: the strict same-row marker predicate was followed by broad legacy branches
  that did not require `Page`/`Pages`, plus an aggregation of marker words across the first
  three rows.
- Bounded repair: Revision Record rejection now requires one inspected row to contain all three
  marker groups: `Rev`/`Revision`, `Page`/`Pages`, and `Description`/`Date`. The two broad
  legacy branches and cross-row aggregation were removed without changing other parser,
  locator, service, or frontend behavior.

Fix-pass RED:

- `py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py -q`
  -> `2 failed, 5 passed`.
- The failing negatives proved that `Revision` + `Date` without `Page(s)` was rejected and
  that revision-like words split across header/body rows were aggregated. Positive complete
  same-row singular/plural header variants passed.

Fix-pass GREEN and validation:

- `py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py -q`
  -> `7 passed`.
- Fresh required combined validation:
  `py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py tests\unit\test_product_spec_matrix_parser.py -q`
  -> `31 passed`.
- `py -m py_compile backend\modules\test_plan\product_spec_matrix_parser_support.py`
  -> passed with exit code `0`.
- Fix implementation checkpoint:
  `903b1d314fe7b3743a270c4d13001e61fbbf1864`.
- The final lane HEAD is the evidence-only descendant reported in the Orchestrator callback.

Real-attachment smoke explicitly authorized by the user:

- Current localhost upload API reproduced the reported deployed/runtime issue:
  automatic import selected table `7`, page `11`, table-on-page `1`, with false Group `03`.
- Current localhost Page `10` + Keyword `TEST GROUP` located table `6` but returned
  `Selected table 6 is not a valid Matrix table.` This confirms the running primary application
  has not yet integrated the lane implementation.
- The same real DOCX parsed by the lane selected table `6` with Groups
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10` and no blocker.
- The lane application-service boundary with the real DOCX tables and Office-derived locator
  data for Page `10` + Keyword `TEST GROUP` returned table `6`, page `10`,
  table-on-page `1`, the same eleven Groups, and no blocker.
- No Replace, Confirm Matrix, persistence, user-file write, push, merge, or destructive action
  was performed.
