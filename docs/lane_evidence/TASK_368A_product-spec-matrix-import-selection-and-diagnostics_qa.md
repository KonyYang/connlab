# TASK_368A QA Evidence

Date: 2026-07-31
Task: `TASK_368A_PRODUCT_SPEC_MATRIX_IMPORT_SELECTION_AND_DIAGNOSTICS_QUICK_FIX`
Lane: `task-368a-product-spec-matrix-import-quick-fix`
Role: permanent QA / Smoke Owner
Status: `qa_pass`

## Authorization And Gate

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary `docs/task_board.md` records TASK_368A as the sole active task.
- Reviewer evidence status is `reviewer_pass`; its only blocking finding was closed before QA.
- QA validated only the clean reviewed lane commit chain. QA did not modify product code, tests,
  task, plan, board, Quick Fixer evidence, or Reviewer evidence.
- QA did not merge, push, cherry-pick, reset, restore, clean, discard residuals, publish, or
  restart the currently running service.

## Reviewed Input

- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368a-product-spec-matrix-import-quick-fix`
- Branch: `lane/task-368a-product-spec-matrix-import-quick-fix`
- Original base: `6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7`
- Reviewed product and Quick Fixer evidence HEAD:
  `78dcce7d50d09dd396a6dc5d15b2c24e743bdd1f`
- Reviewer evidence commit / QA starting HEAD:
  `3c5e4a91373f882c7178b3a0e071e3778be1fd0a`
- Git ancestry checks proved
  `6c16cbcb..78dcce7d..3c5e4a91`.
- `78dcce7d..3c5e4a91` changes only the Reviewer evidence file.
- At QA start, branch and HEAD matched the dispatch; worktree and index were clean.

## Environment

- OS: `Microsoft Windows NT 10.0.26200.0`
- Windows PowerShell: `5.1.26100.8875`
- Python: `3.13.3`
- Node.js: `v24.14.1`
- npm: `11.11.0`
- Git: `2.51.0.windows.1`

## Fresh Clean-Commit Regression

From the lane worktree:

```powershell
py -m pytest tests\unit\test_task_368a_product_spec_matrix_import_selection.py tests\unit\test_product_spec_matrix_parser.py -q
```

Result: `31 passed in 0.91s`.

```powershell
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py backend\application\project_test_plan_matrix_preview_service.py
```

Result: exit code `0`.

From `frontend/`:

```powershell
npm test -- MatrixEditorWorkspace.test.tsx
```

Result: `1` test file passed; `45 passed`.

```powershell
npm run build
```

Result: passed; TypeScript build and Vite production build completed. Vite emitted the existing
non-blocking chunk-size warning for a minified chunk larger than 500 kB.

From the lane worktree:

```powershell
git diff --check 6c16cbcb7d10e6f88829ff823c05dd4ee36f92a7..3c5e4a91373f882c7178b3a0e071e3778be1fd0a
```

Result: exit code `0`.

## Behavior Verification

The fresh backend regression and inspected assertions prove:

- comparison-only header canonicalization recognizes split `SECTIO N` without changing stored
  body text;
- the synthetic qualification Matrix auto-selects table `1` in the two-table snapshot, matching
  the real-document table-6 shape, and returns exactly eleven Groups:
  `1, 2, 3, 4, 5, 6a, 6b, 7, 8, 9, 10`;
- complete same-row singular and plural Revision Record headers
  (`Rev + Page + Description` and `Revision + Pages + Date`) fail closed;
- `Revision + Date` without `Page(s)` is not rejected as a Revision Record;
- revision-like markers distributed across body rows are not aggregated into a false rejection;
- Page + Keyword filters candidates to the requested page;
- an explicit locator miss returns `No table matched the requested Matrix locator.` with no
  automatic-scoring fallback;
- a located invalid table retains requested page/table diagnostics.

The fresh Matrix Editor test includes the focused regression proving an authoritative backend
blocker is displayed before the synthetic locator-mismatch fallback, and no import commit occurs.

## Scope And Repository Hygiene

- `base..QA-starting-HEAD` contains exactly eight authorized product/test/Quick Fixer/Reviewer
  evidence paths.
- Exact allowlist comparison reported `ActualCount: 8`, with no unexpected or missing paths.
- Forbidden-path scan reported `ForbiddenCount: 0`; no API/client, Office, persistence, schema,
  data, release, board, project-management, or `.agents` path entered the candidate.
- Before authoring this evidence, `git status --porcelain=v1 --untracked-files=all` and
  `git diff --cached --name-only` each reported zero entries.
- The frontend build produced no tracked or untracked non-ignored residual.

## Real DOCX Provenance And Limitation

- Quick Fixer evidence records a user-authorized read-only smoke against the real attachment:
  current localhost reproduced the old unintegrated behavior, while the lane selected document
  table `6`, page `10`, table-on-page `1`, returned the eleven expected Groups, and had no
  blocker.
- The QA delegation did not provide the attachment's direct local path. QA therefore did not
  search user directories or rerun the real-DOCX smoke.
- Attachment inaccessibility is non-blocking under the approved contract; the synthetic
  regression is the formal QA gate.
- Current localhost is not recorded as fixed, integrated, or representative of the lane.
- QA did not write, copy, stage, or commit any external attachment.

## Conclusion And Handoff

- QA gate: `qa_pass`
- Blocking findings: none
- Product/test changes by QA: none
- Remote push: not performed; no remote branch contains the QA starting HEAD in locally available
  remote refs.
- Next legal role: permanent Integrator
- Stop point: after committing this evidence and confirming the lane worktree/index clean, QA
  returns control to the permanent Orchestrator and does not perform integration.
