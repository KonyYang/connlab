# TASK_352 Dependency Decision Planner Evidence

Task: `TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW`
Lane: `pdf-matrix-import-deterministic-preview`
Role: Planner
Status: planned_blocked - dependency/license decision required, implementation not authorized
Date: 2026-07-06

## Scope

Planner dependency/prototype decision pass after Reviewer B1. This pass only updates TASK_352 task/plan/evidence/board source-of-truth and does not add dependencies, write product code, route Developer implementation, or change frontend/backend/test implementation files.

## Reviewer B1 Summary

Reviewer implementation-readiness blocked TASK_352 because Developer planning-first proposed `pymupdf>=1.24,<2.0` as the deterministic PDF extraction dependency without a project/user decision for:

- PyMuPDF/MuPDF AGPL compliance;
- Artifex commercial licensing;
- permissive-license alternative; or
- prototype-only dependency evaluation.

Because ConnLab has offline Windows packaging/distribution context, product implementation must not add PyMuPDF until this decision is explicit.

## Sources Read / Checked

Repository:

- `AGENTS.md`
- `docs/task_board.md`
- `docs/project_management/LANE_ORCHESTRATION_PROTOCOL.md`
- `docs/project_management/ROLE_THREAD_REGISTRY.md`
- `tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md`
- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_planner.md`
- `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_developer.md`

Official/public dependency facts checked on 2026-07-06:

- PyPI `pymupdf`: `https://pypi.org/project/pymupdf/`
- PyMuPDF product/licensing comparison: `https://pymupdf.io/`
- PyPI `pdfplumber`: `https://pypi.org/project/pdfplumber/`
- PyPI `pdfminer.six`: `https://pypi.org/project/pdfminer.six/`
- PyPI `pypdf`: `https://pypi.org/project/pypdf/`

## Dependency Facts

- PyPI lists `pymupdf` as dual licensed under GNU AGPL 3.0 or Artifex Commercial License.
- PyMuPDF's product comparison describes AGPL use as requiring open-sourcing the application when distributed, while commercial licensing is for proprietary/commercial use without AGPL obligations.
- PyMuPDF/MuPDF is a technically strong candidate for local PDF text/table extraction, but the license choice is a product/distribution decision, not a Developer-only implementation detail.
- PyPI lists `pdfplumber` as MIT License and describes it as working best on machine-generated PDFs, with table extraction and visual debugging.
- PyPI lists `pdfminer.six` as MIT license expression and describes it as a PDF parser/analyzer focused on extracting text and layout data.
- PyPI lists `pypdf` as BSD-3-Clause; its package description emphasizes split/merge/crop/transform plus text/metadata retrieval, so it is not the first table-extraction candidate but may be useful as a support library if later justified.

## Planner Decision

Do not approve PyMuPDF as the default TASK_352 product dependency.

TASK_352 remains valid as a planned PDF Matrix Import lane, but it is not implementation-ready. Keep `TASK_352` as `planned_blocked` until a dependency/license route is chosen.

## Decision Options For User / Orchestrator

1. Recommended: choose the permissive-license path.
   - Route Developer back to planning-first to replace PyMuPDF with `pdfplumber` / `pdfminer.six` as the primary implementation candidate.
   - After Developer updates the plan/evidence, route Reviewer implementation-readiness re-gate.

2. Choose PyMuPDF only with explicit license approval.
   - User/project must approve either AGPL compliance obligations for ConnLab distribution/source obligations or a commercial Artifex license.
   - Only then may `pymupdf` return to `pyproject.toml` May Touch.

3. Create a prototype-only dependency evaluation lane.
   - No product dependency and no TASK_352 implementation yet.
   - Prototype compares candidate libraries against generated fixtures and read-only local samples, then returns extraction quality, packaging, and license findings to Planner/Reviewer.

Planner recommendation: option 1, unless the user explicitly wants a commercial PyMuPDF path or a prototype bake-off first.

## Source-Of-Truth Updates

- `tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md` now records `planned_blocked` dependency/license decision required.
- `docs/task_352_pdf_matrix_import_deterministic_preview_plan.md` now records the B1 blocker, dependency facts, decision options, and updated stop point.
- `docs/task_board.md` now records TASK_352 as `planned_blocked`, with next route as User dependency/license decision.
- This evidence file records the Planner decision checkpoint.

## Scope Locks Preserved

- No product code changes.
- No dependency added.
- No `pyproject.toml` change.
- No Developer implementation authorization.
- No OCR, scanned-PDF, AI parsing, Excel Matrix import, parser-rule expansion, schema/migration, Confirmed Matrix/Fee/Test Record/lifecycle, Folder Actions, Intake/LTR, Projects, release/settings/basic-information residual cleanup, `.agents/**`, or `docs/project_management/**` changes.

## Next Role

2026-07-06 update: User/Orchestrator chose option 1, the permissive-license path using `pdfplumber` / `pdfminer.six`. See `docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_reconciliation_planner.md`.

Recommended next role: Developer planning update, then Reviewer implementation-readiness re-gate. Do not route Developer implementation.

## Validation Checkpoint

- `git diff --check -- docs/task_board.md tasks/TASK_352_PDF_MATRIX_IMPORT_DETERMINISTIC_PREVIEW.md docs/task_352_pdf_matrix_import_deterministic_preview_plan.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_planner.md docs/lane_evidence/TASK_352_pdf-matrix-import-deterministic-preview_dependency_decision_planner.md`: passed; PowerShell reported only the existing LF-to-CRLF warning for `docs/task_board.md`.
- Trailing whitespace scan on touched docs/board/task/plan/evidence: passed.
- Targeted status confirms this Planner pass touched TASK_352 docs/board/task/plan/evidence only. Existing unrelated backend/frontend/tests residuals remain visible in status and remain excluded from TASK_352.
