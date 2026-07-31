# TASK_368D Quick Fixer Evidence

Date: 2026-08-01
Task: `TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX`
Lane: `task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`
Role: permanent Quick Fixer
Status: `ready_for_review`
Risk route: `QF-3 / Quick Fixer -> Reviewer -> QA -> Integrator`

## Authorization And Lane

- Current phase:
  `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- User explicitly authorized continuation. The Orchestrator dispatched the compact capsule after
  execution gate `ALLOW_DISPATCH`, snapshot
  `d6dd520fb83f0cdc6a32bde275f17094c2d0a421061a5ed05113f339befeab81`.
- Primary dispatch HEAD:
  `78e3d1dd8e31d1b9c415e56122da985260f5958d`.
- Branch: `lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`.
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`.
- Required start/base HEAD:
  `c49f437b6e7f109a6c99ce9f622987a11b0a85d7`.
- Exact branch/HEAD matched and worktree/index were clean before implementation.
- Implementation checkpoint:
  `4b7965202b8cd0632790a0c7b9383a0d532ce987`.

## Scope

Changed implementation/test paths:

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `tests/unit/test_task_368d_pdf_qualification_matrix_alignment.py`

This evidence file is the only governance path changed in the lane. Parser, application preview,
locator, scoring, API, frontend, persistence, database, method authority, packaging, and release
paths remained unchanged.

## Root Cause

- The supplied GS-12-2299 PDF page 9/table-on-page 2 is visually eight logical columns:
  `TEST | PARA | 1 | 2 | 3 | 4 | 5 | 6`.
- Read-only `pdfplumber` reproduction returned an `18 x 22` raw table. Header values occupied raw
  indices `1,4,7,10,13,16,19,21`; body values occupied left-edge indices
  `0,3,6,9,12,15,18,21`.
- Global empty-column removal produced an `18 x 15` table with seven alternating empty/value pairs
  plus the shared last column. Existing parser header/body indices therefore differed and no
  Matrix candidate was found.
- Every paired span in the real table had at most one populated side per row. A controlled pair
  collapse before the existing downstream repairs restores logical alignment without changing
  cell text or parser semantics.

## TDD

The bounded synthetic uses the observed twenty-two-column positions, six complete group tokens,
compatible section body rows, and both `VT Header` / `VT Rec.` sample subrows.

RED:

- After correcting an over-specific negative-fixture width assertion, the current gateway result
  was `1 failed, 1 passed`.
- The positive failure showed the alternating fifteen-column header beginning with an empty cell
  instead of the expected eight-column logical header.
- The unrelated sparse/merged negative already stayed uncollapsed.

Minimal GREEN:

- Added one gateway-local repair requiring all of:
  - exact fifteen-column seven-pair-plus-tail shape;
  - no row with both sides of a pair populated;
  - exact `TEST` + `PARA` header;
  - six complete controlled group tokens;
  - at least four compatible textual-body/numeric-section rows;
  - consecutive, populated two-row sample evidence with numeric group quantities.
- Only under that signature, each pair is collapsed in logical order using its populated side;
  the existing cleaned cell text is retained unchanged.
- The bounded result is exactly eight columns, Groups `1..6`, established sorted step sequences,
  sample size `5` for all groups, and no blocker/warning.
- Negative sparse/merged input remains wider than eight columns and is not rewritten.
- Result: `2 passed`.

## Validation

- `py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py -q`:
  `2 passed`.
- `py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py tests\unit\test_pdf_matrix_source_gateway.py tests\unit\test_product_spec_matrix_parser.py -q`:
  `35 passed`.
- `py -m py_compile backend\infrastructure\files\pdf_matrix_source_gateway.py`:
  passed.
- Changed gateway physical line count: `482`, below the hard limit `500`.
- `git diff --check`: passed.
- Exact changed-path and staged-path checks remained inside the three-path allowlist.

## Read-Only Real-PDF Smoke

Source:
`C:\Users\White\Desktop\GS-12-2299_Customized Power BTB Connector with14P Product Specification_Rev04.pdf`.

- Automatic preview: capability `supported`, global table `15`, page `9`, table-on-page `2`,
  Groups `1,2,3,4,5,6`, sample sizes `5,5,5,5,5,5`, no blockers, no warnings.
- Explicit page `9` / table-on-page `2`: the same global table, groups, sample sizes, and empty
  blocker/warning results.
- The PDF was read in place only and was not copied, rendered, modified, or committed.

## Self-Check And Handoff

- No second production file, broad arbitrary-table collapse, parser/application/API/frontend/
  persistence/authority change, third real specification, hardcoded real file path, TODO, or
  swallowed exception was introduced.
- The packaged Standard record Excel warning and both real databases/Excel resources were not
  read for mutation, configured, copied, or changed.
- No push, merge, restart, release build, publication, destructive action, or unknown residual
  discard occurred. Remote state: not pushed.
- Final evidence checkpoint, final HEAD, `git show --check`, and clean worktree/index proof are
  reported in the Orchestrator callback.
- Next role: mandatory Reviewer, then mandatory QA.
