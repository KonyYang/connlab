# TASK_368D_PDF_QUALIFICATION_MATRIX_MERGED_CELL_ALIGNMENT_QUICK_FIX

Status: `complete` / `accepted` / `locally_integrated`
Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`

Current gate owner: none; permanent Integrator closeout accepted. QA pass / integration input HEAD
`45f345f49c43eece139245b00048c74e8c83f73b` was locally integrated by merge
`8c79ea1c0caa7e688df8b1a346032bc6dd33d5e1`.

## Goal

Make text-PDF Matrix import correctly normalize a qualification table whose merged-cell headers are
centered within wider PDF extraction spans while body values occupy the left edge of those spans.
For the supplied GS-12-2299 PDF, automatic preview must select page 9, table-on-page 2 and return
Groups 1 through 6 without a Matrix parser blocker.

## Why Safe

- The supplied PDF reproduces deterministically: its page-9 Matrix is extracted as 15 misaligned
  columns even though the visual table has 8 logical columns (`TEST`, `PARA`, and Groups 1-6).
- A minimal in-memory span collapse yields the exact 8 logical columns, six Groups, their existing
  step tokens, and sample size 5 without changing parser scoring or business semantics.
- The repair is confined to PDF table-shape normalization and a bounded regression module.
- The separate packaged-runtime message about an unconfigured Standard record Excel resource is
  an external authority setting, not a parser defect, and is explicitly excluded from this fix.
- No active implementation owns the WIP=1 token or the locked paths.

## May Touch

1. `backend/infrastructure/files/pdf_matrix_source_gateway.py`
2. `tests/unit/test_task_368d_pdf_qualification_matrix_alignment.py`
3. `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_quick-fixer.md`

Role-specific Reviewer, QA, and Integrator evidence may be added at their gates. Primary
governance may update this task file and `docs/task_board.md` only for dispatch and closeout.

## Must Not Touch

- `backend/modules/test_plan/product_spec_matrix_parser.py`
- `backend/modules/test_plan/product_spec_matrix_parser_support.py`
- `backend/application/project_test_plan_matrix_preview_service.py`
- Matrix API/DTO, persistence, schema, database, method-authority, external-resource, Settings, or
  frontend behavior
- `scripts/build_windows_browser_release.ps1`, packaging files, dependencies, lockfiles, or release
  output
- the supplied PDF/screenshots or any real DOCX/Excel/data file
- the packaged `%LOCALAPPDATA%\ConnLab` database or the repository database
- existing retained/cancelled/frozen branches, worktrees, residuals, or Controlled Lane V2
- push, publication, runtime restart, real release build, destructive cleanup, or unknown discard

## Locked Paths

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`
- `tests/unit/test_task_368d_pdf_qualification_matrix_alignment.py`

## Targeted Validation

- Add a bounded synthetic RED/GREEN regression using the observed centered-header/left-body span
  shape, including the two sample subrows.
- Prove normalization produces exactly `TEST`, `PARA`, `1`, `2`, `3`, `4`, `5`, `6`, preserves
  row values, and does not broadly collapse unrelated tables.
- Prove the parser returns Groups 1-6, source step tokens, and sample size 5 with no blocker.
- Run the existing PDF gateway and ProductSpec Matrix parser regressions.
- Run `py_compile` for the changed gateway.
- Read-only real-PDF smoke must auto-select global table 15 / page 9 / table-on-page 2 and return
  Groups 1-6 with no blocker or repair-attributable warning; explicit page 9/table 2 must match.
- Run `git diff --check`, exact allowlist, cached-diff, and clean worktree/index checks.

## Risk Gate

Risk is `QF-3` because this changes PDF/runtime extraction behavior. Required route:

```text
Quick Fixer -> Reviewer -> QA -> Integrator
```

Planner and a full plan are not required. Stop and return to Planner/User if the repair requires a
second production file, parser/application/frontend/API/persistence/authority changes, broad
table-shape heuristics, a third real specification, unexplained regressions, destructive action,
or any scope expansion.

## Branch / Worktree / Base

- Branch: `lane/task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`
- Worktree:
  `D:\PythonProject\connlab-worktrees\task-368d-pdf-qualification-matrix-merged-cell-alignment-quick-fix`
- Implementation base: `c49f437b6e7f109a6c99ce9f622987a11b0a85d7`
- The primary dispatch commit is governance-only and is not the lane implementation base.

## Evidence Path

- Quick Fixer:
  `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_quick-fixer.md`
- Reviewer:
  `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_reviewer.md`
- QA:
  `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_qa.md`
- Integrator:
  `docs/lane_evidence/TASK_368D_pdf-qualification-matrix-merged-cell-alignment_integrator.md`

## Integrator Acceptance Closeout

- Primary premerge: `42cf99ec7b5a75f3d8685d40caa104108416d992`.
- Conflict-free local non-fast-forward merge:
  `8c79ea1c0caa7e688df8b1a346032bc6dd33d5e1`, with QA HEAD as the exact second parent.
- The first-parent merge delta is exactly the authorized five-path gateway/test/Quick Fixer/
  Reviewer/QA package. No parser, application, API, frontend, persistence, authority, packaging,
  release, database, or real-source path was added.
- Merged-primary validation passed bounded `2`, combined PDF/parser `35`, gateway pycompile, the
  482-line ceiling, exact package/ancestry/diff/protected-state checks, and the read-only real-PDF
  auto/explicit/table-1 smoke.
- GS-12-2299 SHA-256 `125D696447B7B58F73A8F5E2AB018DC73EDB1CDEA2DC41F53D5F094DE70290BC`,
  size `624218`, and UTC mtime `2026-07-31T08:20:39.1445408Z` were unchanged.
- Terminal authority is `complete` with token owner and active task null, queue empty, paused/
  Quick Fix/parallel exception null, and no next task.
- The clean integrated lane branch/worktree is retained under permanent Orchestrator governance
  until separately authorized safe maintenance retirement; no removal was attempted.
- No push, publication, release build, service restart, real DB/Excel/source mutation, real
  Create/Retire, or destructive cleanup occurred. The packaged Standard Excel configuration gap
  and supplemental ConfirmedMatrixFeeDraftNotFoundError remain explicitly outside this task.
