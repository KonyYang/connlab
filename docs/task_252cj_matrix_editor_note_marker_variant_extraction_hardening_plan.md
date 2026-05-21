# TASK_252CJ Plan - Matrix Editor Note Marker Variant Extraction Hardening

## 0. Protocol Snapshot

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CJ_MATRIX_EDITOR_NOTE_MARKER_VARIANT_EXTRACTION_HARDENING` (planned, awaiting approval)
- Why allowed now: user explicitly approved opening a controlled note-extraction hardening task while board active task is none.

## 1. Task Understanding (from TASK_EXECUTION_SKILL Step 1)

1. Task goal:
   - Improve deterministic extraction of marker-prefixed note paragraphs and keep exact step/sample marker mapping in Matrix preview.
2. Input data:
   - Parsed document paragraphs (`list[str]`) near matrix table.
   - Matrix cell tokens (`3(a)`, `6#`, `5*`, etc.).
3. Output data:
   - `marker_notes` dictionary used to populate `source_note` and `sample_note`.
   - Unchanged preview payload contracts (`raw_token`, `source_note`, `source_note_origin`, `source_item_section_note`, `sample_note`).
4. Involved modules:
   - `backend/modules/test_plan/product_spec_matrix_parser.py`
   - parser/API tests for matrix preview note mapping
5. Not allowed:
   - No AI parsing, no new document format support, no persistence/domain redesign, no unrelated UI redesign.

## 2. Real Architecture Summary and Coupling Hotspots

- Real flow:
  - `product_spec_matrix_parser.py` builds `marker_notes` from paragraphs via `_collect_marker_notes`.
  - Step/sample cell tokens extract marker via `_extract_marker`.
  - Marker key lookup injects `source_note` (step card) and `sample_note` (samples card).
- Coupling hotspot:
  - Marker-note recall quality fully depends on `_collect_marker_notes` regex coverage.
  - If note prefix is not matched, downstream mapping appears as "missing note" even when token marker exists.

## 3. Design (from TASK_EXECUTION_SKILL Step 2)

### 3.1 Data/Behavior Design

- Keep current marker map shape: `dict[str, str]` where keys are `a-z`, `*`, `#`.
- Expand deterministic note line recognition with additional line-start patterns:
  - ASCII/Unicode parentheses: `(a)` / `（a）`
  - Letter + delimiter: `a)` / `a.`
  - Note wrapper: `Note (a): ...` (case-insensitive)
- Keep note body as raw normalized text; do not parse path/document IDs specially.
- Preserve current marker extraction priority in tokens:
  - parenthesis letter marker first (`(a)`), then symbol marker (`*`/`#`).

### 3.2 Planned File-Level Changes

1. `backend/modules/test_plan/product_spec_matrix_parser.py`
   - Add/adjust regex constants for marker-note line variants.
   - Update `_collect_marker_notes` to parse variant prefixes and normalize marker key.
   - Keep existing `_extract_marker` behavior unless a targeted bug is found during tests.
2. `tests/unit/test_product_spec_matrix_parser.py`
   - Add unit cases for each new marker-note variant.
   - Add case where note body includes path-like text and document-number-like tokens.
   - Add negative cases to avoid false-positive capture from normal sentences.
3. `tests/integration/test_project_test_plan_preview_api.py`
   - Add/extend integration assertion showing marker notes from variant prefixes reach preview payload.

### 3.3 API/Function Signature Impact

- No public API schema changes.
- Internal function signatures unchanged.

### 3.4 Dependency and Layering Impact

- Backend parser-only change; layering remains unchanged.
- No new external dependency.

## 4. Risks and Mitigations

1. Risk: over-broad regex causing false positives.
   - Mitigation: anchor at line start, require explicit marker prefix structure, add negative tests.
2. Risk: duplicate marker definitions in paragraphs causing non-deterministic override.
   - Mitigation: preserve current deterministic last-write-wins behavior; add explicit test if needed.
3. Risk: regression for existing `(a)`/`*`/`#` formats.
   - Mitigation: retain existing tests and add compatibility assertions.

## 5. Validation Plan

1. Parser + API targeted tests:

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

2. Frontend shell safety check:

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor and notes"
```

3. Optional manual smoke (if sample docs available in local environment):
   - Import a doc where note uses `a) ...` or `Note (a): ...`.
   - Verify Step preview `Step Notes` shows mapped text and path-like note body is intact.

## 6. First Implementation Batch (after approval)

1. Parser regex enhancement in `_collect_marker_notes`.
2. Unit tests for variant coverage and non-regression.
3. Integration assertion for preview note mapping path.
4. Execute targeted tests and report results.

## 7. Acceptance Gate

Do not start implementation until user explicitly approves this plan document.
