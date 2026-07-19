# TASK_365B Text PDF / DOCX Matrix Extraction Parity Plan

## Discovery Gate

### Current Context

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active lane: TASK_365B is user accepted after Developer implementation
  and focused Reviewer/QA passes; Integrator packaging/readiness is authorized.
- Current role: Integrator controlled package isolation and closeout.
- Why implementation was allowed: the user explicitly approved this reviewed plan
  on 2026-07-19. Product changes remained confined to its May Touch boundaries.

### User Goal Restatement

Import Matrix already produces acceptable Method, Condition, Requirement, and
downstream defaults from DOCX. Text PDFs must follow the same operation and rules,
including all test families discussed previously. The product should not maintain a
second PDF-specific business-rule library; it should reconstruct PDF pages into the
same logical section shape consumed by the established DOCX parser path.

### Evidence Read

- `AGENTS.md`, `docs/task_board.md`, Planner Discovery and architecture rules
- accepted TASK_352 task/plan/QA evidence
- `project_test_plan_matrix_preview_service.py`
- `pdf_matrix_source_gateway.py` and its unit tests
- `word_document_gateway.py`
- `product_spec_matrix_parser.py` and shared section extractor
- read-only local `PRODSPEC GS-12-2268 ...pdf` smoke

### Confirmed By User

- Scope is all text PDFs, not an MFG-only patch.
- Every rule that applies to DOCX Matrix import should apply identically to PDF.
- The existing PDF Import Matrix operation should remain the user workflow.

### Confirmed By Repository Evidence

- PDF and DOCX already converge in `_preview_from_snapshot(...)` and use the same
  `ProductSpecMatrixParser`; API/frontend/import commit changes are unnecessary.
- The PDF gateway currently calls `_split_paragraphs` independently for each page,
  so it loses the identity of text that continues before the first heading on the
  next page.
- `_inline_section_paragraphs` accepts any decimal-number/title fragment. In the
  real sample it treats page-leading `4.8 Industrial Mixed Gas` as a heading even
  though it is a Clause reference inside section 8.2.
- Real-sample baseline is supported at page 11/table 2 with 15 groups and 28 rows,
  but Current Rating has no Method and MFG has no Condition.
- The 8.2 body ends on one page after `CLASS IIA`; the next page begins with the
  explicit 224h unmated and 112h mated phases before section 8.3.
- Later rows show cross-section leakage, proving this is a general page/section
  reconstruction defect rather than one family matcher defect.
- `pdf_matrix_source_gateway.py` is 461 lines, so adding stateful reconstruction
  logic directly would breach the 500-line hard limit.

### Planner Assumptions

- Product specifications use a forward-moving numeric section sequence within the
  main document body. A backward numeric token while a later section is active is
  body/reference text unless a separately testable document reset is recognized.
- Exact raw paragraph equality is unnecessary; parity is defined by the structured
  Matrix row output supplied to the operator.
- Repeated header/footer artifacts may remain in raw text but must not create section
  boundaries or contaminate extracted structured values.

### Not Yet Confirmed / Explicitly Out Of Scope

- OCR and scanned PDFs are excluded by the user's text-PDF scope and TASK_352.
- Password prompts, protected PDFs, malformed PDFs, and new extraction dependencies
  are not added.
- No historical confirmed Matrix is migrated automatically.
- PDF visual layout fidelity is not redesigned; existing preview iframe and locator
  behavior remain unchanged.

### Planning Risk And Decision

A family-by-family PDF patch would duplicate rules and drift from DOCX. A broad raw
regex rewrite could also misclassify clause references or corrupt table locators.
The safe boundary is one page-aware neutral paragraph rebuilder behind the existing
PDF infrastructure gateway, with the shared parser left untouched. Evidence and user
confirmation satisfy Definition of Ready for a planned-only lane; explicit plan
approval is still required before product code.

## Design

### Authority And Data Flow

```text
text PDF pages (page boundaries preserved)
  -> PdfMatrixSourceGateway
  -> page-aware logical section paragraph rebuilder
  -> Word-like paragraphs + existing PDF tables/locators
  -> existing ProductSpecMatrixParser
  -> existing Method / Condition / Requirement / notes rules
  -> existing Matrix preview and import workflow
```

DOCX continues to use `WordDocumentGateway` and enters the same shared parser without
any change.

### New Rebuilder Contract

Add a small infrastructure helper:

```python
def rebuild_pdf_paragraphs(page_texts: list[str]) -> tuple[str, ...]:
    """Return ordered Word-like paragraphs from page-aware text-PDF content."""
```

The helper owns only source normalization:

1. Preserve page boundaries while cleaning NUL/whitespace artifacts.
2. Detect actual numeric section headings in document order.
3. Reject inline candidates preceded by reference language such as `Clause`,
   `Section`, `paragraph`, or `per`.
4. While a section sequence is active, keep backward section-like numbers as body
   text rather than opening a new section.
5. Append next-page text before the first valid new heading to the previous logical
   section.
6. Emit each logical section as one ordered paragraph suitable for the existing
   `collect_section_text_blocks` contract.
7. Preserve non-section note paragraphs needed by current marker/sample-note logic.
8. Do not interpret test families, prices, durations, standards, or requirements.

Ambiguous content remains source text; the shared parser may leave fields Pending.
The rebuilder must not invent facts or reorder sections.

### Gateway Integration

`PdfMatrixSourceGateway.read_pdf_document` will collect cleaned text per page, then
delegate paragraph reconstruction once after all pages are read. Existing table
extraction, table normalization, continuation merge, candidate location metadata,
raw text, no-text/no-table blockers, and `pdfplumber` exception mapping remain intact.

The existing `_split_paragraphs`, `_inline_section_paragraphs`, and
`_inline_note_paragraphs` logic should move or delegate to the focused helper so the
gateway falls farther below the 500-line limit rather than growing.

### Parity Definition

Parity is measured at `MatrixRowPreview`, not at raw PDF text:

- same Test Item and source section
- same Method
- same Condition
- same Requirement
- same extraction status/notes where source facts are equivalent

This automatically covers current shared rules for Visual Examination, CR/LLCR,
IR/DWV, Current Rating, force/mating, Durability/Reseating, Salt Spray, MFG,
Temperature/Humidity/Thermal families, and future rules that consume the same
section-paragraph contract.

## TDD Sequence

1. Add a red pure-helper test for an 8.2 section ending on page N and continuing
   with Class IIA phase durations before 8.3 on page N+1.
2. Add red boundaries for `Clause 4.8`, backward references, inline reference words,
   ordered same-page headings, page header/footer artifacts, notes, and no headings.
3. Add a DOCX-equivalent/PDF-equivalent parser test asserting identical structured
   rows for representative electrical, MFG, and environmental sections.
4. Implement the focused page-aware paragraph rebuilder.
5. Delegate from `PdfMatrixSourceGateway` without changing table/locator behavior.
6. Add generated multi-page text-PDF gateway/API tests.
7. Run read-only real-sample smoke on all four TASK_352 PDFs and assert detailed
   `GS-12-2268` row outcomes.
8. Run full focused regressions, review checklist, and package-isolation checks.

## File-Level Changes

### New Production File

- `backend/infrastructure/files/pdf_section_paragraph_rebuilder.py`

### Narrow Existing Production Change

- `backend/infrastructure/files/pdf_matrix_source_gateway.py`: preserve page texts
  and delegate logical paragraph reconstruction; no business-rule changes.

### Tests

- new `tests/unit/test_pdf_section_paragraph_rebuilder.py`
- update `tests/unit/test_pdf_matrix_source_gateway.py`
- update `tests/unit/test_product_spec_matrix_parser.py` for parity fixture only
- update `tests/integration/test_project_test_plan_preview_api.py` for one generated
  cross-page PDF route regression

### Governance

- TASK_365B task, plan, Planner/Developer/Reviewer/QA evidence, and narrow board entry

## Risks And Controls

- **False headings:** reject reference-prefixed and backward section candidates;
  retain ambiguous text in the active section.
- **Lost continuation:** page-aware state explicitly carries pre-heading text into
  the active section.
- **Rule duplication:** shared parser production files are locked.
- **Gateway growth:** reconstruction lives in a new small module and existing helper
  logic moves/delegates out of the 461-line gateway.
- **Table regression:** current table normalization/merge/location tests remain green.
- **Real-data risk:** external PDFs are read-only smoke inputs; live import/confirm is
  not executed by automated validation.
- **Overclaiming parity:** generated equivalent fixtures plus representative real-row
  assertions define evidence; unsupported/ambiguous source remains Pending.

## Validation

```powershell
py -m pytest tests\unit\test_pdf_section_paragraph_rebuilder.py tests\unit\test_pdf_matrix_source_gateway.py -q
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\unit\test_spec_section_text_extractor.py -q
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
py -m py_compile backend\infrastructure\files\pdf_section_paragraph_rebuilder.py backend\infrastructure\files\pdf_matrix_source_gateway.py
git diff --check
```

Read-only real-sample gate:

- all four TASK_352 PDFs remain supported with their accepted locators/counts
- `GS-12-2268`: page 11/table 2, 15 groups, 28 rows
- Current Rating 6.4 Method `EIA-364-70`
- MFG 8.2 Method `EIA-364-65`, canonical Class IIA 224h/112h Condition
- later environmental rows do not inherit neighboring Requirement/Condition values

## Review Checklist / Completion Standard

- No UI/API/schema/persistence/authority/Office/Word/Fee change
- No OCR, AI, new dependency, or real-file mutation
- New files remain below 300 lines; PDF gateway remains below 500 and preferably
  shrinks after delegation
- Focused tests, compile, diff, trailing whitespace, locked-scope, and read-only
  sample checks pass
- Developer stops after evidence and Reviewer/QA handoff; no next task begins

## Approval Boundary

The user accepted TASK_365B on 2026-07-19. Integrator may package only the exact
rebuilder, gateway delegation/removal, focused test, and governance boundary listed
in the task Completion Boundary. TASK_365A at `13079a37` and TASK_365C at `71203210`
are read-only accepted baselines. Shared parser/Fee production, Current Rating rules,
API/schema/frontend/seed/authority writes, source PDFs/DOCX, real data/files, and
external residuals remain excluded. No new implementation or remote push is
authorized by this reconciliation.
