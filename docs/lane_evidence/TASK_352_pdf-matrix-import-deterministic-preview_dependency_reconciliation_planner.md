# TASK_352 Dependency Decision Reconciliation Planner Evidence

Task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`
Lane: `pdf-matrix-import-deterministic-preview`
Role: Planner
Status: dependency_decision_reconciled - pending Developer planning update, implementation not authorized
Date: 2026-07-06

## Scope

Planner source-of-truth reconciliation after User/Orchestrator selected dependency option 1. This pass updates TASK_352 task/plan/evidence/board only. It does not write product code, add dependencies, update `pyproject.toml`, route Developer implementation, or modify frontend/backend/test implementation files.

## User Decision Recorded

User/Orchestrator approved option 1:

- Use the recommended permissive-license path with `pdfplumber` / `pdfminer.six`.
- PyMuPDF / MuPDF is not approved as the default TASK_352 product dependency.
- Product implementation remains not authorized until source-of-truth update, Developer planning update, Reviewer implementation-readiness re-gate, explicit user implementation approval, and implementation authorization reconciliation.

## License / Packaging Facts Reconfirmed

Planner rechecked current public package metadata on 2026-07-06:

- `pdfplumber` on PyPI lists MIT License, supports Python 3.10-3.14, is built on `pdfminer.six`, and is described as best for machine-generated rather than scanned PDFs.
- `pdfminer.six` on PyPI lists MIT license expression, supports Python 3.10+, and focuses on PDF text/layout extraction.
- `pymupdf` on PyPI lists dual licensing under GNU AGPL 3.0 or Artifex Commercial License. It remains locked out under the user's option 1 decision.

Reference URLs:

- `https://pypi.org/project/pdfplumber/`
- `https://pypi.org/project/pdfminer.six/`
- `https://pypi.org/project/pymupdf/`

## Source-Of-Truth Updates

- `tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md`
  - Status updated to planned with dependency decision resolved for permissive path.
  - Records that PyMuPDF/MuPDF is not approved as the default product dependency.
  - Records next legal role as Developer planning update.
- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md`
  - Adds section 20 recording the option 1 decision, updated dependency strategy, required Developer planning update topics, and updated next role.
- `docs/task_board.md`
  - Top status and active lane row now record dependency decision resolved and next route as Developer planning update, not implementation.
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_decision_planner.md`
  - Appended user option 1 reconciliation note.

## Updated Developer Planning Requirements

Developer planning update must replace the PyMuPDF-first plan with `pdfplumber` / `pdfminer.six` strategy and document:

- exact dependency/version pins;
- whether `pdfplumber` alone is enough or whether direct `pdfminer.six` use is needed;
- Windows offline packaging and transitive dependency impact;
- generated fixture strategy for text tables, multi-page/page-table locators, no-text/scanned-style blockers, and no-Matrix-table blockers;
- table extraction output mapping into the existing Word-like neutral `tables`, `paragraphs`, and table-location metadata;
- failure mapping that remains business-readable and does not add OCR, AI, Excel import, or parser-rule expansion.

## Scope Locks Preserved

- No product code changes.
- No dependency added.
- No `pyproject.toml` change.
- No Developer implementation authorization.
- PyMuPDF / MuPDF remains locked under option 1.
- No OCR, scanned-PDF support, AI parsing, Excel Matrix import, parser-rule expansion, schema/migration, Confirmed Matrix/Fee/Test Record/lifecycle, Folder Actions, Intake/LTR, Projects, release/settings/basic-information residual cleanup, `.agents/**`, or `docs/project_management/**` changes.

## Next Role

Recommended next role: Developer planning update.

Stop point: Developer should update TASK_352 plan/evidence only, then return to Reviewer implementation-readiness re-gate. Do not route Developer implementation.

## Validation Checkpoint

- `git diff --check -- docs/task_board.md tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md docs/task_352_pdf_matrix_import_deterministic_preview_plan.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_decision_planner.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_reconciliation_planner.md`: passed; PowerShell reported only the existing LF-to-CRLF warning for `docs/task_board.md`.
- Trailing whitespace scan on touched docs/board/task/plan/evidence: passed.
- Targeted status confirms this Planner pass touched TASK_352 docs/board/task/plan/evidence only. Existing unrelated backend/frontend/tests residuals remain visible and excluded from TASK_352.
