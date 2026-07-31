# TASK_368B QA Evidence

Date: 2026-07-31
Task: `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Role: permanent QA / Smoke Owner
Status: `qa_pass`

## Authorization And Gate

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary `docs/task_board.md` records TASK_368B as the active task after Planner-approved scope
  reconciliation.
- Primary governance HEAD:
  `d3314a047f69dffd497927dc0e95802e04f17259`.
- Quick Fixer evidence status is `ready_for_review`.
- Reviewer evidence status is `reviewer_pass`, with no blocking or non-blocking finding.
- QA is mandatory because the amended support predicate participates in the global complete-token
  Matrix table-score boundary.
- QA changed no product, test, task, plan, board, Quick Fixer evidence, or Reviewer evidence.

## Reviewed Input

- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`
- Branch: `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`
- Original base: `b671bb493a683529cfe64ab320df4f90914406c8`
- Reviewed product / Quick Fixer HEAD:
  `59ea8455d2283bce3411a1031a3867331783a8d7`
- Reviewer evidence commit / QA starting HEAD:
  `1b41bd5f71679e7cd1188d1da5a6502eb2292e8c`
- Git ancestry checks proved:
  `b671bb49..59ea8455..1b41bd5f`.
- `59ea8455..1b41bd5f` adds only the Reviewer evidence file.
- At QA start, branch and HEAD matched the dispatch; the linked worktree and index were clean.

## Environment

- OS: `Microsoft Windows NT 10.0.26200.0`
- Windows PowerShell: `5.1.26100.8875`
- Python: `3.13.3`
- Git: `2.51.0.windows.1`

## Fresh Clean-Commit Validation

From the lane worktree:

```powershell
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q
```

Result: `3 passed in 0.06s`.

```powershell
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py tests\unit\test_product_spec_matrix_parser.py -q
```

Result: `27 passed in 0.12s`.

```powershell
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py
```

Result: exit code `0`.

```powershell
git diff --check b671bb493a683529cfe64ab320df4f90914406c8..1b41bd5f71679e7cd1188d1da5a6502eb2292e8c
```

Result: exit code `0`.

`git show --check --format=fuller --stat
1b41bd5f71679e7cd1188d1da5a6502eb2292e8c` also passed.

## Independent Behavior Verification

A direct production-parser/score check, separate from the Quick Fixer evidence, returned:

- exact Groups:
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10, Group P`;
- Group count: `12`;
- final raw label: `Group P`;
- stable key: `group_p`;
- final synthetic step tokens: `1, 2, 10`;
- final synthetic sample expression: `3`;
- final synthetic sample size: `3`;
- support full-match results:
  - `Group P`: accepted;
  - `Group 1`: accepted;
  - `Group 6a`: accepted;
  - `Group Purpose`: rejected;
- complete-token candidate score: `53`;
- broad-phrase candidate score: `41`;
- unchanged `_MIN_MATRIX_SCORE`: `45`;
- score delta: `12`.

The broad `Group Purpose` candidate therefore receives no complete-token bonus and remains below
the unchanged acceptance threshold.

A base-versus-reviewed comparison additionally proved:

- the `table_score()` function body is byte-for-byte unchanged;
- base and reviewed code both contain `_MIN_MATRIX_SCORE = 45`;
- the committed implementation diff changes only the ordinary parser comparison and
  `GROUP_TOKEN_HEADER_RE`;
- the `+12` value, all other weights, score control flow, selection, and tie-breaking remain
  unchanged.

## Required Real-PDF Read-Only Smoke

Exact user-provided source:

`C:\Users\White\Desktop\AI information\Spec\PRODSPEC GS-12-1941 CoolPowerHD_Rev4.pdf`

Read-only provenance:

- file size: `3336726` bytes;
- SHA-256:
  `674400E7E00370E76727F273D9F6B1F0C5E4985C5ADDAB2D0488773A60105B7F`;
- last-write UTC:
  `2026-04-26T04:29:26.6928978Z`;
- attributes: `Archive`.

QA invoked the lane's
`ProjectTestPlanMatrixPreviewService.preview_from_path(...)` directly with page `11` and
table-on-page `2`. This was not a current-localhost, integrated, persisted, or published-runtime
claim.

Observed result:

- capability: `supported`;
- selected document table: `16`;
- selected page: `11`;
- selected table-on-page: `2`;
- exact raw Groups:
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10, Group P`;
- Group count: `12`;
- final raw label/key: `Group P` / `group_p`;
- final step tokens:
  `1, 2, 3, 4, 5, 6, 7, 8, 9, 10`;
- final sample expression: `3(a)`;
- final numeric sample size: `null` because the source value retains its footnote expression;
- warnings: none;
- blockers: none.

The task prohibits PDF rendering/copying/writing, so QA used only the existing read-only source
gateway and did not create PDF/PNG intermediates. The PDF was not copied, rendered, modified,
staged, or committed. QA performed no Replace, Confirm Matrix, submit, persistence, project write,
upload mutation, service restart, or localhost request.

## Scope And Repository Hygiene

- `base..QA-starting-HEAD` contains exactly five authorized product/test/Quick Fixer/Reviewer
  evidence paths.
- Exact allowlist comparison reported `ActualCount: 5`, with no unexpected or missing path.
- Forbidden-path scan reported `ForbiddenCount: 0`.
- No application, API/DTO, domain, infrastructure, Office/PDF extraction, locator, persistence,
  schema, frontend, authority, release, board, project-management, or real-file path entered the
  candidate.
- `product_spec_matrix_parser.py` is `500` physical lines, at but not above the hard limit;
  `product_spec_matrix_parser_support.py` is `469`; the bounded test is `139`.
- After tests, compilation, direct behavior checks, and real-PDF smoke, worktree and index each
  reported zero entries.

## Conclusion And Handoff

- QA gate: `qa_pass`
- Blocking findings: none
- Product/test changes by QA: none
- Remote push: not performed; no locally known remote branch contains the QA starting HEAD.
- No merge, cherry-pick, reset, restore, clean, restart, publication, destructive action, or
  residual discard was performed.
- Next legal role: permanent Integrator.
- Stop point: after exact-path committing this QA evidence and confirming the lane worktree/index
  clean, QA returns control to the permanent Orchestrator and does not integrate.
