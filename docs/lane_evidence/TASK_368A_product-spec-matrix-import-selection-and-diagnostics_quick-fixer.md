# TASK_368A Quick Fixer Evidence

Date: 2026-07-31
Task: `TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX`
Lane: `task-368a-product-spec-matrix-import-quick-fix`
Role: permanent Quick Fixer
Status: `approved_ready_for_quick_fixer_dispatch`

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
- Governance/base commit: `6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7`.
- Worktree inspection: branch matches, HEAD matches the governance/base commit, and
  worktree/index are clean.
- Quick Fixer checkpoint: pending.

## Required Quick Fixer Record

Before callback, replace the pending status and record:

- RED tests and observed failures;
- changed paths;
- GREEN validation commands/results;
- full checkpoint commit;
- clean worktree/index proof;
- residuals or blockers;
- next role recommendation.

Stop status must be one of:

- `ready_for_review`;
- `blocked_scope_expansion`;
- `blocked_unexplained_test_failure`;
- `blocked_ownership_conflict`.
