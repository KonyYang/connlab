# TASK_282 Matrix Editor Spec MCR Autofill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` and `superpowers:test-driven-development`. Implement serially. Do not parallelize broad Matrix Editor changes.

**Goal:** During engineering specification import, automatically prefill Matrix Editor `Method`, `Condition`, and `Requirement` columns from the matching specification sections, while keeping all values editable and user-confirmed through the existing `Confirm Matrix` flow.

**Architecture:** Keep the flow inside existing boundaries:

```text
Office parsing -> backend/modules/test_plan parser
preview orchestration -> backend/application
API response -> frontend/src/api/client.ts
Matrix Editor display/edit -> frontend/src/features/matrix-editor
Confirm Matrix -> existing Matrix authority/session path
```

No frontend Office parsing. No API route business logic. No StepInstance/report/fee/AI expansion.

---

## Current Phase And Task Gate

- Current phase: Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation.
- Current active task before planning: none.
- Proposed task: `TASK_282_MATRIX_EDITOR_SPEC_MCR_AUTOFILL`.
- Allowed reason: TASK_281 is complete and the user approved planning the next Matrix Editor automation task.
- Implementation gate: do not write implementation code until the user explicitly approves TASK_282 execution and `docs/task_board.md` marks TASK_282 as the active implementation task.

## Task Understanding

Input:

- An imported engineering specification `.docx`.
- Parsed Matrix table rows containing `Test Items` and `Section`.
- Specification section body text in the same document.

Output:

- Matrix preview/session rows where `method`, `condition`, and `requirement` are prefilled when deterministically extracted.
- Editable Matrix Editor cells containing those values.
- Confirmed Matrix snapshots preserving the values after user confirmation.

Non-output:

- No generated report content.
- No execution data.
- No AI inference.
- No method-library UI.

## Reference Observation

The user-provided reference folder contains a useful older pattern:

- `matrix_test_method_manager.py` combines specification method extraction with template filling.
- `template_data.py` maps common Test Items to Condition/Requirement templates.
- `template_filler.py` matches Test Item aliases to templates.
- `spec_extractor.py` finds method text from Word specification sections.

TASK_282 should reuse the concept, not the architecture. ConnLab should implement a deterministic parser/application flow that preserves source lineage and lets users edit values before confirmation.

## Design Decisions

### Decision 1: Direct Prefill, Not Separate Apply Preview

Because Matrix Editor already works as an imported editable draft/session, extracted values should appear directly in the editable table. The user confirms by editing and clicking `Confirm Matrix`.

### Decision 2: Specification Section First

Use `Section` as the primary join key. Do not guess from Test Item when a section body is available.

### Decision 3: Partial Fill Is Allowed

If only Method is confidently extracted, fill Method and leave Condition/Requirement blank. Do not invent missing content.

### Decision 4: Preserve Existing Flow

Group selection, sample guard, source lineage, notes, selected-only filtering, and confirm behavior must remain unchanged.

## Data Shape

Extend the internal/response row shape with optional detail extraction metadata.

Suggested backend row payload fields:

```python
method: str | None
condition: str | None
requirement: str | None
detail_extraction_status: str | None
detail_extraction_source_section: str | None
detail_extraction_notes: list[str] | None
```

Allowed status values:

```text
matched
partial
missing
ambiguous
```

The frontend does not need to render all metadata in TASK_282. It must at least receive and preserve Method/Condition/Requirement.

## Existing Compatibility Gaps

The implementation must close these current gaps before relying on the extracted values:

1. `MatrixRowPreview` currently does not carry row-level `method`, `condition`, `requirement`, or extraction status fields.
2. `SourceMatrixRowSnapshot` currently does not carry `method`, `condition`, or `requirement`; persisted source snapshots can lose extracted values.
3. `matrix_editor_session_service._build_source_preview_payload()` currently rebuilds preview rows without MCR fields.
4. Cached `source_preview_payload` and rebuilt `source_preview_payload` must expose the same row-level MCR fields.

## Row-Level vs Step-Level Fields

Keep existing `MatrixStepPreview` fields unchanged:

```text
condition_summary
method_summary
reference_standard
judgement_criteria
```

These are step/token preview metadata. TASK_282 adds row-level fields to `MatrixRowPreview`:

```text
method
condition
requirement
detail_extraction_status
detail_extraction_source_section
detail_extraction_notes
```

Do not map row-level `method` into `MatrixStepPreview.method_summary`, and do not use step-level summaries as the source of authority for Matrix Editor row cells.

## Parser Split Requirement

`backend/modules/test_plan/product_spec_matrix_parser.py` is already above the AGENTS.md hard limit. TASK_282 must not add section collection or MCR extraction logic directly into that file.

Add:

```text
backend/modules/test_plan/spec_section_text_extractor.py
```

Responsibilities:

- collect specification section text blocks by section number.
- detect numbered section headings.
- extract deterministic Method/Condition/Requirement values.
- return extraction status and notes.

`product_spec_matrix_parser.py` should remain the Matrix table parser and call this helper. If feasible within TASK_282, reduce `product_spec_matrix_parser.py` under 500 lines by moving related section/detail extraction helpers only; do not do unrelated parser refactors.

## Implementation Tasks

### Task 1: Add Parser Fixture Tests First

Files:

- Modify: `tests/unit/test_product_spec_matrix_parser.py`
- Add: `tests/unit/test_spec_section_text_extractor.py` if extractor behavior is easier to test independently.

Steps:

- [ ] Add a `.docx` fixture builder with:
  - a Matrix table containing `Test Items`, `Section`, and group token columns.
  - section paragraphs for at least `5.4`, `6.1`, and one missing/partial case.
- [ ] Assert parser preview row for `6.1` includes:
  - Method like `EIA-364-23D`
  - Condition like `20mV max, 100mA max`
  - Requirement limit text from the section.
- [ ] Assert missing section leaves Method/Condition/Requirement blank and does not fail parsing.
- [ ] Include the fixture builder implementation work in this task; no existing shared fixture helper is assumed.
- [ ] Run the test and confirm it fails before implementation.

Command:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py -q
```

### Task 2: Split Section Extraction Out Of ProductSpecMatrixParser

Files:

- Add: `backend/modules/test_plan/spec_section_text_extractor.py`
- Modify: `backend/modules/test_plan/product_spec_matrix_parser.py`

Steps:

- [ ] Add a small helper to collect paragraphs by numbered section heading.
- [ ] Match headings such as:
  - `6.1 Contact Resistance`
  - `6.3.1 Temperature rise`
  - `8.6 Mixed Flowing Gas`
- [ ] Capture text until the next section heading at the same or higher outline level.
- [ ] Keep helper deterministic and covered by tests.
- [ ] Keep section extraction and MCR extraction outside `product_spec_matrix_parser.py`.
- [ ] Make `product_spec_matrix_parser.py` call the extractor and attach row-level output to `MatrixRowPreview`.

Guard:

- Do not use Word COM here unless already required by the parser path.
- Do not add broad fuzzy document interpretation.

### Task 3: Extract Method/Condition/Requirement From Section Text

Files:

- Modify: `backend/modules/test_plan/spec_section_text_extractor.py`
- Modify: `tests/unit/test_spec_section_text_extractor.py` if added.

Steps:

- [ ] Add a helper that accepts `(test_item, section, section_text)` and returns detail extraction fields.
- [ ] Extract Method using deterministic standard patterns:
  - `EIA[- ]364[- ]\d+[A-Z]?`
  - `EIA[- ]364[- ]\d+-\d+` where needed.
  - project-specific references only when explicitly present in the section.
- [ ] Extract Condition from deterministic condition phrases in the same section, for example voltage/current/speed/duration/cycles/dwell/time/temperature text.
- [ ] Extract Requirement from deterministic acceptance/limit phrases, for example `shall not exceed`, `No damage`, resistance limits, force limits, temperature-rise limits.
- [ ] Return `matched`, `partial`, `missing`, or `ambiguous`.

Guard:

- If multiple conflicting methods/limits are found and no rule can choose safely, mark `ambiguous` and leave the conflicting field blank.

### Task 4: Wire Extracted Details Into Preview Rows

Files:

- Modify: `backend/modules/test_plan/product_spec_matrix_parser.py`
- Modify: `backend/application/project_test_plan_matrix_preview_service.py` only if DTO/schema mapping requires it.
- Modify: `tests/integration/test_project_test_plan_preview_api.py`

Steps:

- [ ] Include extracted values in the parser preview payload row.
- [ ] Add row-level fields to `MatrixRowPreview`.
- [ ] Keep existing `MatrixStepPreview` fields unchanged.
- [ ] Ensure API preview response exposes or preserves `method`, `condition`, and `requirement`.
- [ ] Add integration coverage for a preview response containing extracted values.

Command:

```powershell
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
```

### Task 5: Preserve Details Through Source Snapshot And Matrix Editor Session

Files:

- Modify: `backend/domain/source_matrix_models.py`
- Modify: `backend/infrastructure/storage/models_matrix_source.py`
- Modify: `backend/infrastructure/storage/repositories/source_matrix_import.py`
- Modify: `backend/application/source_matrix_import_persistence_service.py`
- Modify: `backend/application/matrix_editor_session_service.py`
- Modify: `backend/application/matrix_import_commit_service.py` only if the source-replacement commit path loses fields.
- Modify: `tests/unit/test_source_matrix_persistence_service.py`
- Modify: `tests/unit/test_matrix_editor_session_service.py`
- Modify: `tests/unit/test_matrix_import_commit_service.py` only if touched.

Steps:

- [ ] Add `method`, `condition`, and `requirement` to `SourceMatrixRowSnapshot`.
- [ ] Add persistence columns/mapping for those fields if the storage model does not already have them.
- [ ] Ensure source matrix import persistence writes parser row MCR into the snapshot.
- [ ] Update repository read/write mapping to round-trip row MCR fields.
- [ ] Update `_build_source_preview_payload()` to output `method`, `condition`, and `requirement` when reconstructing source preview payload from a persisted snapshot.
- [ ] Ensure cached preview payload and rebuilt preview payload have equivalent row-level MCR shape.
- [ ] Confirm session seed uses preview row `method`, `condition`, `requirement`.
- [ ] Confirm source-replacement and same-source confirm paths preserve the fields.
- [ ] Add a regression test: imported source row with extracted M/C/R confirms to active authority with the same values.

Commands:

```powershell
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\unit\test_source_matrix_persistence_service.py -q
py -m pytest tests\unit\test_matrix_import_commit_service.py -q
```

### Task 6: Frontend API And Matrix Editor Display

Files:

- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/features/matrix-editor/matrixImportSessionModel.ts`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
- Modify: `frontend/src/features/matrix-editor/MatrixEditorWorkspace.test.tsx`

Steps:

- [ ] Extend TypeScript response/session types for optional extraction metadata if needed.
- [ ] Ensure existing row conversion reads `method`, `condition`, `requirement` from parsed preview/session data.
- [ ] Keep cells editable.
- [ ] Add a frontend test proving imported rows display prefilled Method/Condition/Requirement.
- [ ] Add a frontend test proving users can still edit a prefilled field.

Commands:

```powershell
cd frontend
npm test -- --run MatrixEditorWorkspace --watch=false
npm run build
```

### Task 7: Static Guard And Scope Validation

Files:

- Modify: `tests/unit/test_frontend_shell_files.py`

Steps:

- [ ] Add or update TASK_282 static guard to ensure:
  - no frontend direct Office parsing.
  - no StepInstance/report/fee/evidence/AI UI expansion.
  - Matrix Editor remains the only edited UI surface.
- [ ] Run static guard.

Command:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task282 or matrix_editor"
```

### Task 8: Documentation And Board Sync

Files:

- Modify: `tasks/TASK_282_MATRIX_EDITOR_SPEC_MCR_AUTOFILL.md`
- Modify: `docs/task_board.md`
- Modify: `docs/task_plan_index.md`

Steps:

- [ ] Mark TASK_282 complete only after tests pass.
- [ ] Update validation summary.
- [ ] Set current active task back to none.
- [ ] Record next recommended task as TASK_283 review/filter affordances or TASK_284 method-library fallback, depending on user priority.

## Validation Plan

Run at minimum:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py -q
py -m pytest tests\integration\test_project_test_plan_preview_api.py -q
py -m pytest tests\unit\test_matrix_editor_session_service.py -q
py -m pytest tests\unit\test_matrix_import_commit_service.py -q
cd frontend; npm test -- --run MatrixEditorWorkspace --watch=false
cd frontend; npm run build
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "task282 or matrix_editor"
py -m pytest tests\integration\test_matrix_to_test_record_smoke_flow_api.py -q
git diff --check
```

## Risk Controls

- **Extraction may be imperfect:** fill only deterministic fields; leave uncertain values blank.
- **Wrong overwrite risk:** TASK_282 fills import/session data before user confirmation; do not add automatic post-load overwrites.
- **Parser fragility:** fixture tests must include exact, partial, and missing section cases.
- **Parser size risk:** keep new extraction logic in `spec_section_text_extractor.py`; do not grow `product_spec_matrix_parser.py`.
- **Data-loss risk:** source snapshot, cached preview payload, rebuilt preview payload, session seed, and confirm must all round-trip row MCR fields.
- **Naming confusion risk:** keep row-level `method/condition/requirement` separate from step-level `method_summary/condition_summary/judgement_criteria`.
- **UI clutter risk:** do not add a separate review page in TASK_282.
- **Scope creep risk:** no method library UI, no AI, no StepInstance/report/fee/evidence scope.

## Review Checklist

Before closing TASK_282, verify:

- [ ] Domain/application/infrastructure boundaries are respected.
- [ ] API routes remain thin.
- [ ] Frontend calls only `frontend/src/api/client.ts`.
- [ ] Matrix Editor cells remain editable.
- [ ] Source snapshot round-trips Method/Condition/Requirement.
- [ ] `_build_source_preview_payload()` includes Method/Condition/Requirement.
- [ ] Step-level legacy fields remain unchanged.
- [ ] Existing group selection and sample guard tests still pass.
- [ ] Confirmed Matrix preserves prefilled values.
- [ ] No future-scope objects are introduced.

## Stop Rule

Stop after TASK_282. Do not implement TASK_283 or TASK_284 without a separate task file, plan, and explicit user approval.
