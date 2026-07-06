# TASK_352 PDF Matrix Import Deterministic Preview - Planner Implementation Reconciliation

Task ID: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`
Lane: `pdf-matrix-import-deterministic-preview`
Role: Planner
Date: 2026-07-06
Status: implementation authorized - pending Developer implementation

## Scope Of This Pass

This was a source-of-truth reconciliation pass only. No product code, backend code, frontend code, tests, dependency files, real user sample files, `.agents/**`, or `docs/project_management/**` files were intentionally modified.

## Fact Chain Recorded

- Planner Discovery / formal lane creation completed.
- Reviewer plan gate passed.
- User approved Developer planning-first.
- Developer planning-first completed.
- Reviewer B1 dependency blocker was resolved by Planner/User dependency decision.
- Dependency decision was reconciled to the permissive path.
- Developer planning update completed.
- Reviewer implementation-readiness re-gate passed.
- User approved TASK_352 reconciliation and Developer implementation.

## Implementation Authorization Scope

Developer implementation is authorized only for deterministic text-PDF Matrix import support:

- Add a backend PDF source gateway that extracts text-PDF content into Word-like tables, paragraphs, page/table locator facts, and table context metadata.
- Reuse the existing `ProductSpecMatrixParser`, Matrix preview API, PDF preview iframe, locator/Reparse, TASK_350B stale Replace behavior, Replace/Append, group selection, and commit flow.
- Preserve `.docx/.doc` regression behavior from TASK_350A and Matrix import entry behavior from TASK_350C.

## Dependency Decision

- `pdfplumber>=0.11,<1.0` is the primary approved dependency.
- Direct `pdfminer.six>=20240706,<20270000` is allowed only if implementation proves lower-level layout API usage is necessary.
- PyMuPDF / MuPDF packages (`pymupdf`, `pymupdf4llm`, `pymupdfpro`) remain locked out for TASK_352 unless a later explicit AGPL/commercial decision reopens them.

## May Touch For Future Developer Implementation

- `pyproject.toml` or lock-equivalent only for the approved `pdfplumber` / narrowly justified direct `pdfminer.six` path.
- `backend/application/project_test_plan_matrix_preview_service.py`
- Backend PDF source gateway files under `backend/infrastructure/files/`
- `backend/api/routes_project_test_plan.py`
- `backend/api/dependencies.py` only if dependency injection changes.
- `backend/modules/test_plan/product_spec_matrix_parser.py` only for adapter-facing compatibility tests, not parser rule expansion.
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`
- `frontend/src/api/client.ts` only if DTO/type changes are unavoidable.
- Focused backend/frontend tests and TASK_352 docs/evidence/board through normal lane flow.

## Must Not Touch / Locked Paths

- OCR, scanned-PDF handling, AI parsing, or Excel Matrix import.
- Matrix parser rule expansion unless a separate approved parser lane exists.
- Storage schema changes unless separately justified and approved.
- Confirmed Matrix, Fee, Test Record, lifecycle, Workbench, Folder Actions, Intake/LTR, Projects registry/list semantics.
- API-route or frontend PDF business parsing.
- Real user sample mutation, real public-drive roots, real workbook files, or real project folders.
- Workbench/Folder/Intake/Projects/release/settings cleanup.
- `.agents/**`
- `docs/project_management/**`

## Source-Of-Truth Updates

- `docs/task_board.md` now records TASK_352 as implementation authorized and pending Developer implementation.
- `tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md` now records the Reviewer/User/Developer fact chain and approved implementation readiness.
- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md` now includes the Planner implementation authorization reconciliation section.

## Validation Expectations For Developer Implementation

- Focused backend gateway/service/API tests for text-PDF success and not-text/unsupported/scanned/no-table/page-table mismatch failures.
- `.docx/.doc` regression tests from TASK_350A.
- TASK_350B stale Reparse/Replace regression.
- Focused frontend MatrixEditorWorkspace tests for `.pdf,.doc,.docx` accept and existing modal/locator behavior.
- `py_compile`, focused `pytest`, focused `npm test`, and `npm run build`.
- Dependency/license scan proving PyMuPDF packages were not introduced.
- Diff/trailing/forbidden-scope/no-real-file mutation scans.

## Stop Point

Planner reconciliation is complete. Recommended next role: Developer implementation pass. Completion still requires Developer evidence, Reviewer implementation gate, QA gate, and Integrator packaging/readiness.

## Validation Checkpoint

- `git diff --check -- docs/task_board.md tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md docs/task_352_pdf_matrix_import_deterministic_preview_plan.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_implementation_reconciliation_planner.md` passed with an existing LF/CRLF warning for `docs/task_board.md` only.
- Trailing whitespace scan on touched TASK_352 docs/board/evidence returned no matches.
- Targeted status confirms the intended TASK_352 reconciliation package is limited to source-of-truth docs/evidence/board. Existing external residuals remain excluded, including Settings/LTR backend files, desktop release files/tests, New Project test residuals, and unrelated release packaging residuals.
