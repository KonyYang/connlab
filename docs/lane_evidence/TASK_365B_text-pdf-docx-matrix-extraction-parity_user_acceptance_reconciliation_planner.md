# TASK_365B User Acceptance And Package Reconciliation Evidence

## Status

Planner reconciliation complete on 2026-07-19. Developer implementation, Reviewer
pass, focused QA pass, and explicit user acceptance are recorded. TASK_365B is now
`user accepted / pending Integrator packaging/readiness`.

## Gate Evidence

- Reviewer evidence is `Pass` with no blocking finding.
- QA evidence is `Pass`; the combined TASK_365A/TASK_365B regression recorded
  `214 passed` with py_compile and scoped whitespace checks passing.
- The later accepted TASK_365C combined parser/Fee/PDF parity regression recorded
  `276 passed` without changing the TASK_365B package boundary.
- Read-only smoke recorded all four TASK_352 PDFs as supported. The user-provided
  GS-12-2268 PDF and DOCX each returned `28` supported rows with matching 8.3/8.5/8.6
  outcomes; no source, live Matrix, database, or generated output was mutated.
- The user explicitly accepted TASK_365B and requested Integrator packaging.

## Accepted Baselines

- TASK_365A is complete/accepted at local commit `13079a37`.
- TASK_365C is complete/accepted at local commit `71203210`.

Neither accepted baseline may be replayed, restaged, or attributed to TASK_365B.

## Exact Candidate Whitelist

Whole-file candidates:

- `backend/infrastructure/files/pdf_section_paragraph_rebuilder.py`
- `tests/unit/test_pdf_section_paragraph_rebuilder.py`

Exact current-diff candidates:

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`: rebuilder imports,
  per-page original-text collection, one final `rebuild_pdf_paragraphs` delegation,
  tuple assignment, and removal of the superseded local split/clean/inline helper
  implementations. Existing table, locator, raw-text, and blocker behavior remains.
- `tests/unit/test_pdf_matrix_source_gateway.py`: cross-page MFG gateway regression
  and its generated temporary PDF helper only.
- `tests/unit/test_product_spec_matrix_parser.py`: rebuilder import and the neutral
  PDF/DOCX structured parity test only.
- `tests/integration/test_project_test_plan_preview_api.py`: generated cross-page
  PDF preview regression and its temporary PDF helper only.
- TASK_365B task, plan, Planner/Developer/Reviewer/QA evidence, this reconciliation
  evidence, and exact TASK_365B board hunks.

## Exclusions

- All accepted TASK_365A MFG helper/dispatch/tests and TASK_365C thermal/surge code.
- `backend/modules/test_plan/spec_section_text_extractor.py`, all family extractors,
  shared parser production, and all Fee production/tests.
- Current Rating business-rule implementation; TASK_365B only transports neutral
  page text so accepted shared behavior can consume it.
- TASK_363C/D, TASK_364B/C, API route/DTO/application changes, schema/frontend/
  seed/authority writes, real PDFs/DOCX/databases/files, release output, and every
  unrelated dirty residual.

Mixed files require exact hunk-level staging; wholesale staging is forbidden. No
product/test modification, source-file access, staging, commit, or push occurred in
this Planner action.

## Next Legal Role

Integrator packaging/readiness. Integrator must reproduce this exact whitelist,
run contained validation, and either create the controlled local commit or report
the smallest package-boundary blocker. Remote push remains unauthorized.
