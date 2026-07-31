# TASK_368D PDF Qualification Matrix Merged-Cell Alignment — Reviewer Evidence

Date: 2026-08-01
Task: `TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX`
Role: permanent Reviewer
Status: `reviewer_pass`
Risk route: `QF-3 / Reviewer -> QA -> Integrator`
Next: permanent QA

## Authority And Review Boundary

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary governance HEAD: `ebcadd5d121108580f7e8a0ccbe1a63ce1373127`.
- Review base: `c49f437b6e7f109a6c99ce9f622987a11b0a85d7`.
- Implementation checkpoint: `4b7965202b8cd0632790a0c7b9383a0d532ce987`.
- Reviewed evidence HEAD: `d2906b3dfdcf66148edc1313d72b80cda5fce6f0`.
- Branch: `lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`.
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`.

Primary authority records `gate_running`, TASK_368D as the sole WIP=1 token owner, permanent
Reviewer as the current read-only gate, an empty queue, and no parallel exception. Read-only
execution-gate `Inspect` returned `ALLOW_INSPECT`, primary authority root
`D:\PythonProject\connlab`, and `zero_write: true`.

Review covered only committed
`c49f437b6e7f109a6c99ce9f622987a11b0a85d7..d2906b3dfdcf66148edc1313d72b80cda5fce6f0`.
The exact package contains:

1. `backend/infrastructure/files/pdf_matrix_source_gateway.py`
2. `tests/unit/test_task_368d_pdf_qualification_matrix_alignment.py`
3. `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_quick-fixer.md`

No parser, application, API, frontend, persistence, authority, release, database, real-data, or
other governance path changed.

## Findings

### Blocking

- None.

### Non-Blocking

- None.

## Implementation Review

### Root Cause And Shape Signature

The committed real-PDF provenance and bounded fixture agree:

- GS-12-2299 Matrix is page `9`, table-on-page `2`, global table `15`;
- raw extraction is `18 x 22`;
- centered header values occupy raw columns `1,4,7,10,13,16,19,21`;
- left-edge body values occupy `0,3,6,9,12,15,18,21`;
- removing globally empty columns therefore produces exactly fifteen columns: seven exclusive
  left/right pairs plus one shared tail.

The repair handles exactly that fifteen-column shape. It collapses pairs in logical order and
selects the sole populated side, so cell text and row order are preserved unchanged. Exact-width
checks avoid off-by-one and odd-width indexing; empty, fourteen-column, and sixteen-column inputs
were independently confirmed unchanged.

### Narrow Fail-Closed Gating

The repair runs only when every guard succeeds:

- every row is exactly fifteen columns;
- no row populates both sides of any of the seven pairs;
- the collapsed header starts with exact case-insensitive `TEST` and `PARA`;
- exactly six complete Group header tokens match the same controlled token domain already used by
  ProductSpec parser support, including numeric, numeric-suffix, single-letter, and optional
  `Group` prefix forms;
- at least four body rows combine a textual test item with a numeric/compound section token;
- a `Sample size` row is immediately followed by a populated second sample subrow;
- both sample rows contain numeric quantities for all six Groups.

Reviewer-owned in-memory negatives independently changed one gate at a time. Bad header,
`Group Purpose`, a populated pair collision, insufficient body evidence, non-consecutive sample
rows, and a missing sample quantity all remained at the original fifteen-column shape. The
committed unrelated sparse/merged negative also remains uncollapsed. No broad sparse-table or
merged-table fallback was introduced.

### Compatibility And Maintainability

- Normalization still performs the existing revision-record rejection before this repair and the
  existing fragmented-header and sample-tail repairs afterward.
- Parser scoring, selection/tie-breaking, locator behavior, revision guards, continuation merge,
  sample-tail behavior, and ProductSpec parser code are unchanged.
- The bounded parser assertion follows the established sorted-step contract
  `(sequence, source_row_index, test_item)` and proves raw step tokens, Groups `1..6`, and sample
  size `5` without blocker or warning.
- Existing Group token formats remain supported because the gateway signature regex is identical
  in domain to `GROUP_TOKEN_HEADER_RE`; the repair does not rewrite labels.
- The gateway-local helper is deterministic and single-purpose. The gateway is `482` physical
  lines, below the hard limit `500`; the bounded test module is `110` lines.

## Independent Validation

```powershell
py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py -q
```

Result: `2 passed in 0.09s`.

```powershell
py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py tests\unit\test_pdf_matrix_source_gateway.py tests\unit\test_product_spec_matrix_parser.py -q
```

Result: `35 passed in 0.49s`.

```powershell
py -m py_compile backend\infrastructure\files\pdf_matrix_source_gateway.py
```

Result: passed.

Additional checks:

- `git diff --check` for base through reviewed HEAD: passed;
- `git show --check` for implementation and Quick Fixer evidence commits: passed;
- exact three-path allowlist: passed;
- forbidden parser/application/API/frontend/persistence/authority/release/database diff: empty;
- pre-evidence lane worktree/index, including untracked files: clean;
- no real PDF was reopened by Reviewer; the committed Quick Fixer read-only provenance was
  inspected and matched against the exact synthetic column positions and expected output;
- no merge, push, restart, build, real file mutation, or destructive action was performed.

The missing packaged Standard-record Excel operator setting remains outside this task. The
supplemental `ConfirmedMatrixFeeDraftNotFoundError` ASGI path is a separate confirmed-fee/API
contract concern requiring Planner/QF-4 authority and was not absorbed.

## Conclusion And Handoff

- Conclusion: `reviewer_pass`
- Blocking findings: none
- Non-blocking findings: none
- Next role: permanent QA
- Because TASK_368D is QF-3, QA remains mandatory before Integrator.
