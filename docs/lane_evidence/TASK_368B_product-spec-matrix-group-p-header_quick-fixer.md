# TASK_368B Quick Fixer Evidence

Date: 2026-07-31
Task: `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Role: permanent Quick Fixer
Status: `ready_for_review`

## Authorization And Scope

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled
  foundation.
- User request: fix the missing final `Group P` from
  `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`.
- The original parser-only dispatch reached a real-PDF scoring blocker and preserved its WIP
  without bypassing the score.
- Planner then approved scope reconciliation under the existing user authorization. Primary
  governance HEAD: `d3314a047f69dffd497927dc0e95802e04f17259`.
- The amendment authorized only the existing parser WIP plus the support comparison that decides
  whether raw `header.group_columns` labels receive the existing complete-token `+12`.
- `_MIN_MATRIX_SCORE`, the `+12` value, all other weights, scoring control flow, selection,
  locator, extraction, API, application, persistence, frontend, and authority behavior were not
  changed.

May Touch:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`
- this evidence file

## Worktree And Checkpoints

- Branch: `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`
- Governance base: `b671bb493a683529cfe64ab320df4f90914406c8`.
- Preserved blocked WIP:
  `b36c95d3aababe5421c09b2e3532d67317331f82`.
- Required continuation HEAD was verified exactly:
  `fb6d102d54d72d252a1f7415fb8cffd648c1ea42`.
- Branch, HEAD, worktree, and index were clean before the reconciled implementation started.
- Implementation checkpoint:
  `1e0e8b4d16ee0f922cf1947653b8614fcdde6538`.

## TDD And Implementation

Original bounded RED:

- The fourteen-column GS-12-1941-shaped fixture selected the correct table but omitted its final
  `Group P`; result: `1 failed, 1 passed`.
- The parser-only checkpoint recognized explicit `Group` plus a single-letter token, preserved
  `_clean(row[index])` as the raw label, and reached `2 passed`.
- The required real-PDF smoke then exposed the missing support score and correctly stopped the
  lane for scope reconciliation.

Reconciled scoring RED:

- Added a bounded score fixture whose base score is `41`, below the existing minimum `45`.
- Complete raw tokens `Group P`, `Group 1`, and `Group 6a` were expected to receive the existing
  `+12`; `Group Purpose` was expected to remain at `41`.
- Before the support change, both candidates scored `41`; bounded result:
  `1 failed, 2 passed`.

Minimal GREEN:

- The support complete-token comparison now accepts an optional explicit `Group` prefix followed
  by the existing controlled token domain.
- `Group P`, `Group 1`, and `Group 6a` receive the same existing `+12`; `Group Purpose` still
  fails the full-token comparison and cannot promote an otherwise invalid candidate.
- The stored group label remains the raw source label.
- The synthetic Matrix returns all twelve groups, `group_key == "group_p"`, final-column steps
  `1, 2, 10`, sample expression `3`, and sample size `3`.
- Bounded GREEN: `3 passed`.

## Read-Only Real-PDF Smoke

- Attachment path remained readable at its original external location. It was not copied,
  modified, rendered, or added to the repository.
- `ProjectTestPlanMatrixPreviewService.preview_from_path(...)` was run against page `11`,
  table-on-page `2`.
- Result: capability `supported`, selected table `16`, selected page `11`, selected
  table-on-page `2`.
- Returned raw group labels:
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10, Group P`.
- Final group key: `group_p`; final-column step tokens:
  `1, 2, 3, 4, 5, 6, 7, 8, 9, 10`; sample expression: `3(a)`.
- Warnings: none. Blockers: none.
- No Replace, Confirm Matrix, persistence, project write, restart, push, or publication occurred.

## Validation

- `py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q`:
  `3 passed`.
- `py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py tests\unit\test_product_spec_matrix_parser.py -q`:
  `27 passed`.
- `py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py`:
  passed.
- `git diff --check`: passed.
- Exact changed-path and staged-path checks remained within the four-path allowlist.

## Residual And Handoff

- Remote state: not pushed.
- No unknown or out-of-scope residual was absorbed or discarded.
- Final evidence-only checkpoint records the final lane HEAD in the Orchestrator callback.
- Final worktree/index cleanliness and `git show --check` are verified after that checkpoint.
- Next role: mandatory Reviewer, followed by mandatory QA.
