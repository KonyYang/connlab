# TASK_368B Quick Fixer Evidence

Date: 2026-07-31
Task: `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Role: permanent Quick Fixer
Status: `blocked_scope_expansion`

## Authorization

- User request: fix the missing final `Group P` from
  `PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`.
- The user requested formal Quick Fixer dispatch after read-only diagnosis.
- Orchestrator/Planner Discovery determined that AGENTS.md section 19.1 applies.

## Read-Only Discovery

- Current localhost: status `200`, selected table `16`, page `11`, table-on-page `2`.
- Returned groups:
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10`.
- Missing: final `Group P`, without blocker or warning.
- PDF page 11 and `pdfplumber` extraction show a separate final `Group P` column with populated
  step and sample values.
- Parser reproduction with a synthetic fourteen-column table omits the same final group.
- Root cause is the ordinary parser header comparison accepting numeric groups only.

## Frozen Scope

May Touch:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`
- this evidence file

Everything else is read-only or forbidden by the task.

## Worktree

- Branch: `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`
- Base commit: `b671bb493a683529cfe64ab320df4f90914406c8`.
- Dispatch verification: branch and HEAD matched the exact base; worktree and index were clean.

## TDD And Scope Blocker

RED:

- Added bounded synthetic coverage for the fourteen-column Matrix, raw `Group P`, key,
  independent steps/sample values, `Group Purpose` rejection, and established group forms.
- After correcting the small compatibility fixture to include its real qualification-table
  context, `py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q`
  produced `1 failed, 1 passed`; the only failure was the missing final `Group P`.

Parser-only attempt:

- Added a full-match comparison rule for an explicit `Group` prefix plus one letter while
  preserving `_clean(row[index])` as the raw stored label.
- The bounded synthetic module reached `2 passed`.

Required real-PDF smoke then blocked the lane:

- The external attachment remained readable at its original path and was not copied or changed.
- `ProjectTestPlanMatrixPreviewService.preview_from_path(...)` with page `11`,
  table-on-page `2` retained that location but returned no groups and blocker
  `Selected table 16 is not a valid Matrix table.`
- Root cause: once raw `Group P` enters `header.group_columns`, the existing
  `GROUP_TOKEN_HEADER_RE` check in
  `backend/modules/test_plan/product_spec_matrix_parser_support.py` no longer awards the
  complete-group-token score. The real table falls below `_MIN_MATRIX_SCORE`.
- Correct repair therefore requires a second existing production file and a bounded scoring
  token update. Both are explicitly outside this dispatch.
- A parser-local shadow header or selected-table score bypass would alter scoring semantics
  indirectly and was not attempted.

## Residual And Handoff

- Modified but uncommitted allowed paths:
  `backend/modules/test_plan/product_spec_matrix_parser.py`,
  `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`, and this evidence file.
- No implementation checkpoint was created because the required real-PDF smoke failed.
- No PDF/PNG/table artifact, project persistence, Replace, Confirm Matrix, push, publication,
  restart, reset, restore, clean, or destructive action was performed.
- Next role: Orchestrator / Planner to decide whether to authorize the support-parser scoring
  boundary, then return to Quick Fixer under a revised May Touch list.
