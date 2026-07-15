# TASK_361L Integrator Packaging Evidence

Date: 2026-07-15

Role: Integrator

Status: `integrator_blocked`

## Gate Basis

- Reviewer implementation re-gate is `reviewer_pass`.
- QA disposable SQLite/API/export/frontend gate is `qa_pass`.
- The package is limited to the TASK_361L V2 pricing-draft corrective contract.

## Isolation

`backend/api/dependencies.py` is isolated to the TASK_361L V2 pricing-draft
composition and Required Forms guard hunks. Existing LTR helper code is not changed or
staged. `docs/task_board.md` is entirely unstaged after the Git-owner isolation
repair, so neither its external TASK_361K status hunk nor any TASK_361L closeout text
is part of this package.

TASK_361F operational evidence, TASK_361H artifacts, Point Profile/Measurement Plan
authority changes, Fee rules/pricing/UI redesign, workbook layout, generic outputs,
parser/import, LTR/public drive, real data/files, `.agents/**`,
`docs/project_management/**`, and all other worktree residuals are excluded.

## Validation

- Core backend pricing/consumer/export/rebase suite: `87 passed`.
- Required Forms, Confirmed Fee, and API suite: `50 passed`.
- Fee review page suite: `28 passed` with established React `act(...)` warnings only.
- `py_compile` and frontend production build: passed; build retains only the
  established Vite chunk-size warning.
- Staged diff-check, trailing-whitespace, whitelist, forbidden-path/content, and
  no-real-mutation scans: passed.
- Line-count gate: blocked. The staged
  `backend/api/routes_confirmed_matrix_fee_evaluation_export.py` grows from 472 lines
  at `HEAD` to 507 lines (+35), exceeding the `AGENTS.md` 500-line Python hard limit.
  The staged `tests/integration/test_fee_evaluation_pricing_draft_api.py` also grows
  from an already oversized 557 lines to 596 lines (+39). The QA/Reviewer statement
  that all candidate Python files are below 500 therefore does not match the current
  staged package.

The live browser path was intentionally not run because localhost has no disposable
Fee fixture; QA coverage uses disposable SQLite/temp roots only. No remote push was
performed.

## Decision

`integrator_blocked`

Blocker owner: Developer. Split the new export-route guard into a bounded route/helper
module and move the new API coverage out of the already oversized test module, then
repeat Reviewer and Integrator package validation. No product code was modified by
Integrator, no commit was created, and no remote push was performed.
