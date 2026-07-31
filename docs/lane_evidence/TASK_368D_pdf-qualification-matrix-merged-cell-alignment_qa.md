# TASK_368D PDF Qualification Matrix Merged-Cell Alignment — QA Evidence

Date: 2026-08-01
Task: `TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX`
Role: permanent QA / Smoke Owner
Status: `qa_pass`
Risk route: `QF-3 / Quick Fixer -> Reviewer -> QA -> Integrator`
Next: permanent Integrator

## Authority And Validation Boundary

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Primary governance HEAD: `c3fbccc805ea93ded880fd81497fafa6412aa1ab`.
- Primary execution record: `gate_running`; TASK_368D is the sole WIP=1 token owner; permanent QA
  is the read-only gate owner; queue is empty and no parallel exception exists.
- Review base: `c49f437b6e7f109a6c99ce9f622987a11b0a85d7`.
- Reviewed implementation/evidence HEAD: `d2906b3dfdcf66148edc1313d72b80cda5fce6f0`.
- Reviewer pass / QA input HEAD: `47fd755bd8ab362366a3e25e4a192abd959e7a0d`.
- Branch: `lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`.
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`.

QA read `AGENTS.md`, the current primary board and compact capsule, Quick Fixer and Reviewer
evidence, the execution/WIP policy, lane protocol, parallel operations guide, role registry, and
review checklist. Validation used only the clean reviewed lane. Initial branch, HEAD, worktree,
index, and ancestry matched the dispatch contract.

## Environment

- OS: `Microsoft Windows NT 10.0.26200.0`
- Windows PowerShell: `5.1.26100.8875`
- Python: `3.13.3`
- Git: `2.51.0.windows.1`

## Fresh Regression

```text
py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py -q
2 passed in 0.07s

py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py tests\unit\test_pdf_matrix_source_gateway.py tests\unit\test_product_spec_matrix_parser.py -q
35 passed in 0.47s

py -m py_compile backend\infrastructure\files\pdf_matrix_source_gateway.py
passed
```

Independent in-memory fail-closed probes also passed. Broad `Group Purpose`, a populated pair
collision, insufficient body evidence, a missing sample record, a missing sample quantity, and
14-/16-column widths all remained uncollapsed. The positive controlled shape still collapsed to
eight logical columns.

## Read-Only Real-PDF Smoke

Exact user-provided source:

`C:\Users\White\Desktop\GS-12-2299_Customized Power BTB Connector with14P Product Specification_Rev04.pdf`

Integrity was captured immediately before and after the fresh lane-only service smoke:

- SHA-256: `125D696447B7B58F73A8F5E2AB018DC73EDB1CDEA2DC41F53D5F094DE70290BC`
- Size: `624218` bytes
- UTC mtime: `2026-07-31T08:20:39.1445408Z`
- Before/after values: identical

Both `ProjectTestPlanMatrixPreviewService` calls passed:

| Mode | Capability | Global table | Page | Table on page | Groups | Sample sizes | Blockers | Warnings |
|---|---|---:|---:|---:|---|---|---|---|
| Automatic | supported | 15 | 9 | 2 | 1, 2, 3, 4, 5, 6 | 5, 5, 5, 5, 5, 5 | none | none |
| Explicit `page_number=9`, `page_table_index=2` | supported | 15 | 9 | 2 | 1, 2, 3, 4, 5, 6 | 5, 5, 5, 5, 5, 5 | none | none |

The automatic and explicit previews returned identical raw token and sorted-step summaries:

- Group 1: tokens `1..12`
- Group 2: tokens `1..10`
- Group 3: tokens `1..12`
- Group 4: tokens `1..5`
- Group 5: tokens `1..2`
- Group 6: tokens `1..5`

For every Group, `(sequence, source_row_index, test_item)` order equals the established sorted
step contract. The names/order include the expected source items such as Examination, LLCR,
CR at rated current, Insulation Resistance, Dielectric Withstanding Voltage, and the applicable
group-specific environmental/mechanical items.

An initial QA assertion incorrectly reused the deliberately shortened synthetic fixture's token
subset as the full real-PDF oracle. It failed only on that harness expectation while the candidate
already returned the complete continuous sequences above. QA corrected the oracle to the real
source contract and reran the full before/after smoke successfully; no product/test file was
changed.

## Title-Block And Locator Check

Page 9/table-on-page 1 remains the four-row, four-column document title block:

```text
global table 14
NUMBER GS-12-2299 | TYPE GENERAL PRODUCT SPECIFICATION
TITLE Customized Power BTB Connector with14P | PAGE 9 of 9
```

It is distinct from page 9/table-on-page 2/global table 15. An explicit user selection of table 1
returned `unsupported`, no groups, and blocker
`Selected table 14 is not a valid Matrix table.` It was not misclassified, and QA did not change
locator or application logic.

## Package, Scope, And Repository Integrity

- `c49f437b..47fd755b` contains exactly four paths: the PDF gateway, bounded TASK_368D test,
  Quick Fixer evidence, and Reviewer evidence.
- `d2906b3d..47fd755b` changes only Reviewer evidence.
- Base -> reviewed implementation/evidence -> Reviewer pass ancestry: passed.
- `git diff --check` for the reviewed range: passed.
- `git show --check` for all three lane commits after base: passed.
- Parser, application, API, frontend, persistence/storage, authority, release, packaging, data,
  and real-file paths are absent from the diff.
- Gateway physical line count: `482`; bounded test: `110`; both are within the 500-line hard
  limit.
- Primary remained clean at `c3fbccc805ea93ded880fd81497fafa6412aa1ab`; the working board blob
  matched `HEAD` (`73558c6b0513c9cfe22dd0914b7f902d6f05f1d1`).
- Lane worktree/index remained clean after all read-only validation.
- Reviewer pass HEAD was not contained by any remote branch; QA did not push.

Neither the packaged database nor repository database was opened or inspected by this QA smoke;
the preview service was instantiated without a Basic Information reader. Therefore neither DB
required mutation/hash reconciliation. The packaged Standard-record Excel warning remains the
expected operator-configuration limitation until saved through the authorized Settings flow.

QA did not use current localhost as candidate proof, inspect supplemental ASGI logs as a Matrix
preview stack, or absorb the independent `ConfirmedMatrixFeeDraftNotFoundError`. No service was
started/stopped/restarted; no release was built; no Excel/Word/DB or real source was mutated; and
no merge, push, reset, restore, clean, destructive action, or product edit occurred.

## Conclusion

- Result: `qa_pass`
- Blocker: none
- Next role: `Integrator`
