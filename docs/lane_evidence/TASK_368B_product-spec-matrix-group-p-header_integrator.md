# TASK_368B Integrator Evidence

Date: 2026-07-31
Task: `TASK_368B_PRODUCT_SPEC_MATRIX_GROUP_P_HEADER_QUICK_FIX`
Lane: `task-368b-product-spec-matrix-group-p-header-quick-fix`
Role: ConnLab｜集成负责人 Integrator
Status: `integrator_accepted`
Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

## Authorized Gate

The permanent Orchestrator dispatched a controlled local merge gate after permanent Reviewer
status `reviewer_pass` and permanent QA status `qa_pass`. Remote push, publication, current-service
restart, real-PDF access, product-scope expansion, destructive cleanup, and worktree retirement
remained forbidden.

## Fresh Pre-Merge Facts

- Primary worktree: `D:\PythonProject\connlab`
- Primary branch: `master`
- Primary pre-merge HEAD:
  `d3314a047f69dffd497927dc0e95802e04f17259`
- Primary worktree/index: clean; no merge in progress
- Lane worktree:
  `D:\PythonProject\connlab-worktrees\task-368b-product-spec-matrix-group-p-header-quick-fix`
- Lane branch:
  `lane/task-368b-product-spec-matrix-group-p-header-quick-fix`
- Original base and exact merge-base:
  `b671bb493a683529cfe64ab320df4f90914406c8`
- Quick Fixer ready HEAD:
  `59ea8455d2283bce3411a1031a3867331783a8d7`
- Reviewer evidence HEAD:
  `1b41bd5f71679e7cd1188d1da5a6502eb2292e8c`
- QA/lane HEAD:
  `5cac86b60c728bcbb6a1b72a9e3d340fc976d21b`
- Lane worktree/index: clean
- Remote branches containing lane HEAD: none

Ancestry checks proved the base is an ancestor of primary and lane, and both the Quick Fixer ready
HEAD and Reviewer evidence HEAD are ancestors of the QA/lane HEAD. The latest primary governance
commit changed exactly the TASK_368B task, plan, and board.

## Integrated Package

The complete `base..lane HEAD` package contains exactly six authorized paths:

1. `backend/modules/test_plan/product_spec_matrix_parser.py`
2. `backend/modules/test_plan/product_spec_matrix_parser_support.py`
3. `tests/unit/test_task_368b_product_spec_matrix_group_p_header.py`
4. `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_quick-fixer.md`
5. `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_reviewer.md`
6. `docs/lane_evidence/TASK_368B_product-spec-matrix-group-p-header_qa.md`

No application, API/DTO, domain, infrastructure, frontend, persistence, schema, Office/PDF
extraction, locator, authority, release, real-file, board, project-management, TASK_368A, or
browser-release path entered the lane package.

## Local Merge

Integrator performed a conflict-free local non-fast-forward merge.

- Merge commit:
  `acceeb04241e57d77634f8dbb7f4f9cdef6bba55`
- First parent:
  `d3314a047f69dffd497927dc0e95802e04f17259`
- Second parent:
  `5cac86b60c728bcbb6a1b72a9e3d340fc976d21b`
- First-parent delta: exactly the six authorized paths
- Missing paths: zero
- Unexpected paths: zero
- Primary amended task/plan/board blobs: unchanged by the merge
- Merge `diff --check`: passed

No cherry-pick, partial integration, conflict resolution, push, publication, or service restart
occurred.

## Merged-Tree Validation

Integrator ran on merged primary:

```text
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py -q
```

Result: `3 passed`.

```text
py -m pytest tests\unit\test_task_368b_product_spec_matrix_group_p_header.py tests\unit\test_product_spec_matrix_parser.py -q
```

Result: `27 passed`.

```text
py -m py_compile backend\modules\test_plan\product_spec_matrix_parser.py backend\modules\test_plan\product_spec_matrix_parser_support.py
```

Result: passed.

Additional checks:

- exact six-path first-parent allowlist: passed;
- forbidden-path count: zero;
- merge `git show --check`: passed;
- base-to-merge `git diff --check`: passed;
- lane, Quick Fixer ready, and Reviewer evidence commits are primary ancestors;
- primary and lane worktrees/indexes remained clean after validation;
- physical lines: parser `500`, support `469`, bounded test `139`.

## Frozen Behavior Boundary

The zero-context product diff changes only:

- the ordinary parser header comparison to full-match explicit `Group` plus one alphabetic
  token while preserving `_clean(row[index])` as the stored raw label; and
- `GROUP_TOKEN_HEADER_RE` to accept an optional explicit `Group` prefix followed by the existing
  controlled token domain.

Merged behavior checks returned:

- `Group P`: accepted;
- `Group 1`: accepted;
- `Group 6a`: accepted;
- `Group Purpose`: rejected;
- `_MIN_MATRIX_SCORE`: `45`.

The complete-token `+12` value, all other score weights, `table_score()` control flow, parser
selection, and tie-breaking are unchanged.

## Real-PDF QA Provenance

Integrator did not access or write the real PDF. QA evidence records a read-only smoke against the
external user-provided PDF with SHA-256
`674400E7E00370E76727F273D9F6B1F0C5E4985C5ADDAB2D0488773A60105B7F`.
The lane service selected document table `16`, page `11`, table-on-page `2`, returned the exact
twelve raw groups ending in `Group P`, and reported no warnings or blockers. QA created no PDF/PNG
intermediate and performed no Replace, Confirm Matrix, persistence, project write, upload
mutation, localhost request, restart, push, or publication.

This provenance validates the reviewed lane behavior only. Local Git integration does not refresh
an already-running localhost process.

## Remote And Runtime State

- Remote push: not performed.
- No locally known remote branch contains the integrated lane HEAD.
- Publication/deployment: not performed.
- Localhost start/stop/restart: not performed.
- An already-running localhost may still use old process code until a separately authorized
  future restart.

## Residual Ledger

| Class | Item | Owner | Disposition |
|---|---|---|---|
| `integrated` | Complete six-path TASK_368B product/test/evidence package | none | Integrated by local merge `acceeb04241e57d77634f8dbb7f4f9cdef6bba55`; no package residual remains |
| `stale/superseded` | Parser-only blocked WIP `b36c95d3aababe5421c09b2e3532d67317331f82` and evidence checkpoint `fb6d102d54d72d252a1f7415fb8cffd648c1ea42` as active stop states | closed within integrated TASK_368B ancestry | Historical evidence remains in the accepted commit chain; no discard or separate implementation is required |
| `retain` | Clean integrated TASK_368B lane branch/worktree at `5cac86b60c728bcbb6a1b72a9e3d340fc976d21b` | permanent Orchestrator governance | Retain until a future separately authorized safe maintenance retirement; no removal attempted in this gate |
| `retain` (independent existing item) | TASK_368A merged branch plus unregistered non-worktree residual directory | permanent Orchestrator governance / User decision | Unchanged and not touched by TASK_368B |
| `retain` (independent existing item) | Cancelled browser-release checkpoint `0bf56ea09ba1a1baedd5ce982d0b47d73d1889df` | permanent Orchestrator governance / User decision | Unchanged, unintegrated, and not touched by TASK_368B |

There are no `duplicate`, `format-only`, `conflict`, or unknown discard candidates.

## Stop Point

Status: `integrator_accepted`.

TASK_368B is complete/accepted and locally integrated. It was not pushed, published, deployed, or
applied to the running localhost. Next: Archive/Standby. No replacement or follow-up task is
created.
