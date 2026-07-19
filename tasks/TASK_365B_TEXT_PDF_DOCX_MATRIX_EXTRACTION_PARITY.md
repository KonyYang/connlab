# TASK_365B Text PDF / DOCX Matrix Extraction Parity

## Status

Complete/accepted by Integrator on 2026-07-19 after Developer implementation,
Reviewer/QA passes, user acceptance, and controlled package isolation. Product
changes remain restricted to the reviewed TASK_365B plan and the exact package
boundary below. The accepted package is local only; no remote push was performed.

## Phase / Lane

- Phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`.
- Lane: `text-pdf-docx-matrix-extraction-parity`.
- TASK_365A is complete/accepted at `13079a37`; TASK_365C is complete/accepted at
  `71203210`. Both are read-only package baselines and must not be replayed.
- TASK_365B is a separate backend infrastructure lane and must not absorb other
  dirty-worktree changes or reopen accepted Matrix/Fee rules.

## Goal

Make every supported text PDF reconstruct the same logical specification sections
that the existing DOCX path supplies to `ProductSpecMatrixParser`. All current and
future shared DOCX Matrix rules should then apply to PDF without family-specific PDF
copies, including Method, Condition, Requirement, notes, and section-derived duration
facts.

## Confirmed Business Contract

- Scope covers all text PDFs supported by the existing `pdfplumber` gateway.
- PDF import keeps the same operator workflow as DOCX: Import Matrix, preview,
  locator/Reparse, Replace/Append, group selection, and commit.
- Cross-page section bodies must remain attached to their originating section.
- Section-like references such as `Clause 4.8 Industrial Mixed Gas` must not become
  false specification headings.
- Existing shared extraction rules remain the only business-rule authority; PDF
  receives a Word-like neutral paragraph snapshot before those rules run.
- Scanned PDFs, OCR, AI parsing, password/protected PDF handling, and historical
  confirmed-Matrix rewrites remain out of scope.

## May Touch After Explicit Implementation Approval

- `backend/infrastructure/files/pdf_section_paragraph_rebuilder.py` (new)
- `backend/infrastructure/files/pdf_matrix_source_gateway.py` (narrow delegation)
- `tests/unit/test_pdf_section_paragraph_rebuilder.py` (new)
- `tests/unit/test_pdf_matrix_source_gateway.py`
- `tests/unit/test_product_spec_matrix_parser.py` only for neutral-snapshot parity tests
- `tests/integration/test_project_test_plan_preview_api.py` only for generated
  text-PDF preview regression
- TASK_365B task, plan, evidence, and narrow board status entries

## Must Not Touch / Locked Paths

- `backend/modules/test_plan/spec_section_text_extractor.py`, family extractors,
  Method Library, MCR normalizers, and `product_spec_matrix_parser.py` production logic
- `backend/modules/fee_evaluation/**`, Fee seeds/rules/defaults, workbook/export logic
- frontend, API DTO/routes, application-service behavior, database/repositories,
  schema/migrations, Matrix confirmation/authority semantics, and lifecycle state
- DOCX/Word gateway behavior, Office COM, `.doc` conversion, source candidate logic
- OCR/scanned-PDF engines, AI parsing, new PDF dependencies, PyMuPDF/MuPDF/fitz
- real user PDFs, real project/SQLite/public-drive data, generated output,
  `dist_release/**`, `packaging/**`, `.agents/**`, and `docs/project_management/**`

## Acceptance Criteria

1. Page-aware PDF paragraph reconstruction carries text before the first valid
   heading on a new page into the previous logical section.
2. Lower/backward section-like references and explicit `Clause/Section/paragraph`
   references remain body text rather than opening false sections.
3. A generated DOCX-equivalent and text-PDF-equivalent neutral snapshot produce the
   same Matrix row Method, Condition, Requirement, and extraction status.
4. Read-only `GS-12-2268` PDF smoke remains supported at Matrix page 11/table 2 with
   15 groups and 28 rows.
5. Its Current Rating section 6.4 receives `EIA-364-70` from the continuation page.
6. Its MFG section 8.2 produces `Class IIA; unmated 224 hours; mated 112 hours` while
   retaining Method `EIA-364-65` and current Requirement behavior.
7. Later 8.x rows do not inherit Requirement/Condition fragments from neighboring
   sections; 8.9 retains its own 85C/85%RH/1000h condition.
8. Existing PDF table extraction, continuation-table merge, locator metadata,
   sample notes, DOCX import, and no-text PDF blocker remain unchanged.

## Validation Gate

- Pure page/section reconstruction red-green tests
- PDF gateway unit tests with generated multi-page fixtures
- shared parser parity tests covering representative electrical, MFG, environmental,
  duration, and Method/Condition/Requirement cases
- generated PDF preview API regression plus existing DOCX/PDF regression suites
- read-only real-sample smoke for all four TASK_352 PDFs, with detailed assertions on
  `GS-12-2268`; no source or project mutation
- py_compile, line-count, diff/trailing-whitespace, forbidden-scope, and no-real-file
  mutation checks

## Completion Boundary

Developer implementation, Reviewer/QA gates, and user acceptance are complete.
Integrator must package only this exact boundary:

- whole files: `backend/infrastructure/files/pdf_section_paragraph_rebuilder.py`
  and `tests/unit/test_pdf_section_paragraph_rebuilder.py`;
- exact current diff in `backend/infrastructure/files/pdf_matrix_source_gateway.py`
  for rebuilder imports, page-text collection/delegation, and removal of superseded
  local paragraph/text helper implementations;
- exact TASK_365B test hunks in `tests/unit/test_pdf_matrix_source_gateway.py`,
  `tests/unit/test_product_spec_matrix_parser.py`, and
  `tests/integration/test_project_test_plan_preview_api.py`;
- TASK_365B task, plan, Planner/Developer/Reviewer/QA evidence, user-acceptance
  reconciliation evidence, and exact board hunks.

Accepted TASK_365A/C code and tests, shared parser/Fee production, Current Rating
business rules, API route/DTO/application changes, schema/frontend/seed/authority
writes, source PDF/DOCX files, real data/files, and all other dirty residuals are
excluded. Mixed files require hunk-level staging; wholesale staging is forbidden.
No live Matrix import/confirmation, commit-time source mutation, or remote push is
authorized.
