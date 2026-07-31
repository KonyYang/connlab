# TASK_368B Quick Fixer Evidence

Date: 2026-07-31
Task: `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Role: permanent Quick Fixer
Status: `approved_pending_worktree`

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

## Planned Worktree

- Branch: `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`
- Base commit: pending governance checkpoint and worktree creation.

## Required Quick Fixer Record

Before callback, replace the pending status and record:

- exact branch/worktree/base verification;
- RED result from the new bounded regression;
- implementation and changed paths;
- GREEN targeted parser results and pycompile;
- read-only real-PDF lane smoke;
- exact implementation/evidence commits;
- clean worktree/index proof;
- remote state and residuals;
- next role recommendation.

Stop status must be one of:

- `ready_for_review`;
- `blocked_scope_expansion`;
- `blocked_unexplained_test_failure`;
- `blocked_ownership_conflict`;
- `blocked_attachment_smoke`.
