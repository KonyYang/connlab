# TASK_368D Integrator Evidence

## Result

- Task: `TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX`
- Role: Integrator
- Status: `integrator_accepted`
- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Integration is local only. No remote push, release build, publication, or service restart was performed.

## Gate Inputs

- Primary worktree: `D:\PythonProject\connlab`
- Primary branch: `master`
- Primary premerge HEAD: `42cf99ec7b5a75f3d8685d40caa104108416d992`
- Lane worktree: `D:\PythonProject\connlab-worktrees\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`
- Lane branch: `lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`
- Approved base / merge-base: `c49f437b6e7f109a6c99ce9f622987a11b0a85d7`
- Implementation evidence HEAD: `d2906b3dfdcf66148edc1313d72b80cda5fce6f0`
- Reviewer pass HEAD: `47fd755bd8ab362366a3e25e4a192abd959e7a0d`
- QA pass HEAD / merge input: `45f345f49c43eece139245b00048c74e8c83f73b`
- Preflight confirmed both worktrees and indexes clean, the full base-to-QA ancestry, the exact
  merge-base, no remote branch containing the QA HEAD, and an exact five-path lane package.

## Controlled Integration

- Merge mode: normal local `--no-ff` merge; no cherry-pick, rebase, or history rewrite.
- Merge SHA: `8c79ea1c0caa7e688df8b1a346032bc6dd33d5e1`.
- First parent: `42cf99ec7b5a75f3d8685d40caa104108416d992`.
- Second parent: `45f345f49c43eece139245b00048c74e8c83f73b`.
- Merge was conflict-free. Primary TASK_368D governance and all existing retained, cancelled,
  residual, and frozen facts were preserved.
- The first-parent merge delta is exactly:
  - `backend/infrastructure/files/pdf_matrix_source_gateway.py`
  - `tests/unit/test_task_368d_pdf_qualification_matrix_alignment.py`
  - `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_quick-fixer.md`
  - `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_reviewer.md`
  - `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_qa.md`
- No parser, application, API, persistence, authority, frontend, packaging, release, database, or
  real-source path entered the integration package.

## Merged-Tree Validation

- `py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py -q`:
  `2 passed`.
- `py -m pytest tests\unit\test_task_368d_pdf_qualification_matrix_alignment.py tests\unit\test_pdf_matrix_source_gateway.py tests\unit\test_product_spec_matrix_parser.py -q`:
  `35 passed`.
- `py -m py_compile backend\infrastructure\files\pdf_matrix_source_gateway.py`: passed.
- Gateway line count: `482`, within the `<=500` gate.
- Diff/show/check, exact package, forbidden-path, Reviewer/QA/lane ancestry, protected worktree,
  protected hash, and clean-status checks passed.
- The merged change remains limited to the PDF gateway's controlled centered merged-cell span
  alignment and its bounded regression. External-resource and method-authority behavior was not
  changed.

## Read-Only Real-PDF Provenance

- Source: `C:\Users\White\Desktop\GS-12-2299_Customized Power BTB Connector with14P Product Specification_Rev04.pdf`.
- Before and after SHA-256:
  `125D696447B7B58F73A8F5E2AB018DC73EDB1CDEA2DC41F53D5F094DE70290BC`.
- Before and after size: `624218` bytes.
- Before and after UTC mtime: `2026-07-31T08:20:39.1445408Z`.
- Auto selection and explicit page 9 / table 2 selection both resolved global table `15`, page
  `9`, table-on-page `2`, Groups `1..6`, sample size `5` for every group, continuous sorted token
  sequences, and no blocker or warning.
- Explicit page 9 / table 1 remained fail-closed as a title block with no groups and blocker:
  `Selected table 14 is not a valid Matrix table.`
- The PDF was accessed read-only. No copy, render, export, or source mutation was performed.

## Terminal Governance And Residual Ledger

- TASK_368D is `complete` / `accepted` / `locally_integrated`.
- Execution authority is terminal: `execution_state=complete`, token owner null, active null,
  queue empty, paused null, Quick Fix null, and parallel exception null.
- No next task was created or activated. Next routing is `Archive/Standby`.
- The five-path TASK_368D lane package is classified `integrated`.
- Residual classification: `retain` for the clean integrated branch
  `lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix` and worktree
  `D:\PythonProject\connlab-worktrees\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`.
- Residual owner: permanent Orchestrator governance. Retirement requires separately authorized safe
  maintenance; this gate did not remove or retire the branch/worktree.
- All prior residual records, owners, protected worktrees, cancelled browser-release state, and
  frozen V2 state remain unchanged.

## Explicit Exclusions

- No push, publication, release build, localhost/service restart, real DB/Excel/source mutation,
  real Create/Retire, reset, restore, clean, force removal, or destructive cleanup occurred.
- The packaged Standard record Excel error remains an operator Settings/configuration condition and
  was not treated as a parser defect.
- The supplemental `ConfirmedMatrixFeeDraftNotFoundError` ASGI trace remains outside this task and
  was not absorbed.
- Existing built or running releases do not contain this source integration merely because master
  accepted it; observing the fix there requires a separately authorized future rebuild/restart.

## Callback

```text
TASK_ID: TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX
ROLE: Integrator
STATUS: integrator_accepted
EVIDENCE: docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_integrator.md
NEXT: Archive/Standby
BLOCKER: none
MERGE_SHA: 8c79ea1c0caa7e688df8b1a346032bc6dd33d5e1
REMOTE_SCOPE: no push/release/restart
```
