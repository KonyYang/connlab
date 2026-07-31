# TASK_368B Reviewer Evidence

Date: 2026-07-31
Task: `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Role: permanent Reviewer
Status: `reviewer_pass`

## Authorization And Governance

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary `docs/task_board.md` authorizes TASK_368B after Planner-approved scope reconciliation.
- The authoritative task and plan amendments were read from the primary worktree at governance
  HEAD `d3314a047f69dffd497927dc0e95802e04f17259`.
- Primary governance changes were treated as read-only authority and were not included in the
  lane product diff.
- Reviewer changed no product/test file and performed no merge, push, cherry-pick, restart, real
  attachment access, or destructive action.

## Inspected Commits And Worktree

- Governance base: `b671bb493a683529cfe64ab320df4f90914406c8`
- Required review HEAD: `59ea8455d2283bce3411a1031a3867331783a8d7`
- Branch: `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`

The base is an ancestor of the review HEAD. Branch and HEAD matched the dispatch. The linked
worktree and index were clean before review.

## Scope Review

The committed range
`b671bb493a683529cfe64ab320df4f90914406c8..59ea8455d2283bce3411a1031a3867331783a8d7`
contains exactly:

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`
- `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_quick-fixer.md`

No application, API/DTO, domain, infrastructure, Office/PDF extraction, locator, persistence,
schema, frontend, authority, release, or real-file path changed. No hidden or untracked artifact
was present.

The implementation checkpoint-to-review-HEAD range changes only Quick Fixer evidence. Primary
governance task/plan/board amendments are not part of the product package.

## Findings

### Blocking

- None.

### Non-Blocking

- None.

## Detailed Review

### Parser Header Boundary

- The ordinary Matrix header path adds a full-match comparison for literal `Group` plus one
  controlled alphabetic token.
- `Group P` is accepted; `Group Purpose` is rejected.
- The stored label still comes from `_clean(row[index])`, so raw `Group P` is preserved and its
  stable key remains `group_p`.
- Existing numeric and numeric-suffix paths are unchanged.

### Complete-Token Score Boundary

- `GROUP_TOKEN_HEADER_RE` adds only an optional literal `Group` prefix around the previous
  controlled token domain.
- It accepts `Group P`, `Group 1`, and `Group 6a`.
- It rejects `Group Purpose` and other broad phrases.
- `_MIN_MATRIX_SCORE` remains `45`.
- The complete-token bonus remains `+12`.
- No other weight, `table_score()` branch, parser selection flow, or tie-breaking code changed.

Reviewer independently observed:

```text
parser Group P: true
parser Group Purpose: false
support Group P / Group 1 / Group 6a: true
support Group Purpose: false
valid complete-token score: 53
broad-phrase score: 41
```

The negative fixture therefore proves the broad phrase receives no `+12` and cannot promote the
otherwise 41-point candidate across the unchanged threshold of 45.

### Regression Quality

- The bounded fourteen-column fixture returns exact raw labels:
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10, Group P`.
- Final-column steps, sample expression, sample size, raw label, and stable key are asserted.
- Compatibility coverage retains `Group 1`, bare numeric, and numeric-suffix behavior.
- The score fixture isolates the existing token bonus without changing production scoring or
  duplicating the implementation regex.
- The test is bounded at 139 physical lines and does not modify the oversized mixed parser test.

### Real-PDF Evidence Boundary

Reviewer inspected the Quick Fixer evidence but did not access the real attachment. The recorded
read-only lane smoke retains document table `16`, page `11`, table-on-page `2`, returns all twelve
raw groups ending in `Group P`, and reports no blocker or warning. The evidence records no file
write, Replace, Confirm Matrix, persistence, push, publication, or restart. This is lane evidence,
not a claim that current localhost or a published runtime has integrated the fix.

### Line Limits

- `product_spec_matrix_parser.py`: 500 physical lines, at but not above the AGENTS.md hard limit.
- `product_spec_matrix_parser_support.py`: 469 physical lines.
- bounded TASK_368B test: 139 physical lines.

The parser has no remaining line-count headroom. This does not block the bounded gate, but any
future addition to that file must first preserve the hard limit through a separately authorized
extraction or equivalent bounded change.

## Independent Validation

Reviewer ran:

```powershell
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q
```

Result: `3 passed`.

```powershell
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py tests\unit\test_product_spec_matrix_parser.py -q
```

Result: `27 passed`.

```powershell
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py
```

Result: exit code `0`.

Additional checks:

- `git diff --check` on base through required review HEAD: passed.
- `git show --check` on required review HEAD: passed.
- exact allowlist comparison: no unexpected path.
- `git diff --cached --check`: passed.
- pre-evidence `git status --porcelain=v1 --untracked-files=all`: clean.

## Conclusion And Handoff

- Conclusion: `reviewer_pass`
- Blocking findings: none
- Non-blocking findings: none
- Next role: permanent QA
- QA remains mandatory because the support predicate participates in global Matrix table scoring.
