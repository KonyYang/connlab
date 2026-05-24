# TASK_252CM Plan - Note Block Scoped Extraction And Mapping Fix

## 0. Protocol Snapshot

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CM_MATRIX_EDITOR_NOTE_BLOCK_SCOPED_EXTRACTION_AND_MAPPING_FIX` (planned, awaiting approval)
- Why allowed now: user supplied reproducible mismatch and explicitly approved opening fix task.

## 1. Task Understanding

1. Goal:
   - Fix wrong note origin capture by scoping marker-note extraction to the matrix-adjacent note block.
2. Input:
   - Parsed table content + paragraph stream from `.docx` snapshot.
3. Output:
   - Correct `marker -> note text` mapping for parser payload (`source_note`, `sample_note`).
4. Involved modules:
   - `product_spec_matrix_parser.py` (+ tests).
5. Not allowed:
   - no frontend redesign, no extra formats, no domain/persistence changes.

## 2. Current Root Cause Hypothesis

- `_collect_marker_notes(paragraphs)` currently scans all paragraphs and accepts marker-like lines globally.
- In A2 docs, this can pick wrong marker-like lines outside the intended bottom note block, causing incorrect `3(a)` / `10(c)` note bodies.

## 3. Design

### 3.1 Scoped Extraction Strategy

- Build a local note block collector that:
  - scans paragraphs in order,
  - forms candidate contiguous note blocks with at least 2 marker lines,
  - prefers the block nearest to the selected matrix table region (or the last valid marker block if region linkage is unavailable),
  - extracts only from that chosen block.
- Keep existing marker variant parsing rules for line-level marker syntax.

### 3.2 Backward Compatibility

- Preserve existing variant regex support:
  - `(a)`, `a)`, `（a）`, `a.`, `Note (a):`, `*`, `#`, `(5e)`
- Keep deterministic behavior when duplicate marker appears in same block: last definition wins.

### 3.3 File-level Changes

1. `backend/modules/test_plan/product_spec_matrix_parser.py`
   - add scoped note-block selection helper(s)
   - update `_collect_marker_notes` to consume chosen block only
2. `tests/unit/test_product_spec_matrix_parser.py`
   - add regression test: unrelated marker-like paragraph exists; parser must pick bottom note block
   - add A2-like `(a)..(e)` mapping assertions for steps/samples
3. `tests/integration/test_project_test_plan_preview_api.py`
   - add API-level assertion for scoped extraction behavior

## 4. Risks and Mitigations

1. Risk: too strict block detection misses valid sparse notes.
   - Mitigation: fallback to previous global behavior only when no valid block found.
2. Risk: false positives in block boundary detection.
   - Mitigation: require contiguous marker lines and minimum block size.
3. Risk: regression on prior docs.
   - Mitigation: retain old test set and run targeted parser/API regression.

## 5. Validation Plan

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

Manual smoke:

1. Import `GS-12-1880_PwrBlade Pro BTB Product Specification_A2.docx`.
2. Verify:
   - `3(a)` maps to `Precondition specimens with 20 durability cycles;`
   - `10(c)` maps to `Energize at current for 18℃ temperature rise;`
   - samples containing `(d)/(e)` show matching `(d)/(e)` note text.

## 6. Acceptance Gate

Do not implement until user explicitly approves this plan.
