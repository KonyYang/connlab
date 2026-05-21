# TASK_252CN Plan - Matrix Editor Section Symbol Note Extraction Restore

## 0. Protocol Snapshot

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CN_MATRIX_EDITOR_SECTION_SYMBOL_NOTE_EXTRACTION_RESTORE` (planned, awaiting approval)
- Why allowed now: user supplied a concrete regression in Matrix Editor import note mapping, and the board has no active task.

## 1. Task Understanding

1. Goal:
   - Restore table-footer `*` / `#` note extraction for section markers such as `6.5*`.
2. Input:
   - Product specification paragraph stream and matrix table rows.
3. Output:
   - `source_item_section_note` includes the symbol note body for rows whose Section/Test Item has `*` or `#`.
4. Modules:
   - `backend/modules/test_plan/product_spec_matrix_parser.py`
   - parser/API regression tests
5. Not allowed:
   - no UI redesign, no new format support, no domain/persistence changes.

## 2. Root Cause

- `TASK_252CM` changed marker extraction to prefer contiguous marker-note blocks to avoid wrong `(a)..(e)` source capture.
- `GS-12-1507` has a single standalone symbol note paragraph: `*Simultaneously measure power contact resistance.`
- Because it is a single note, it is not a contiguous block; because a previous letter block exists, the sparse global fallback is not used. As a result, `marker_notes["*"]` is missing and `6.5* / 6.6*` section markers show without note body.

## 3. Design

### 3.1 Merge Standalone Symbol Notes

- Keep current contiguous/backfilled block selection for letter markers.
- Independently collect standalone symbol notes (`*`, `#`) from all paragraphs.
- Merge symbol notes into the selected marker-note map after selecting the best letter block.
- This avoids reintroducing the old global letter-marker false positives while restoring single-line table-footer symbol notes.

### 3.2 Tests

- Add unit regression:
  - paragraphs include unrelated earlier `a./b./c.` text and later `*Simultaneously...`
  - section values `6.5*`, `6.6*`
  - expected `source_item_section_note` includes note body.
- Keep existing A2 tests passing.

## 4. Risks and Mitigations

1. Risk: collecting all symbol notes could pick unrelated `*` text.
   - Mitigation: only parse lines that begin with `*` or `#`, preserving existing strict `_SYMBOL_NOTE_RE`.
2. Risk: duplicate symbol notes.
   - Mitigation: current deterministic last-write behavior is acceptable and matches marker map behavior.

## 5. Validation Plan

```powershell
py -m pytest tests\unit\test_product_spec_matrix_parser.py tests\integration\test_project_test_plan_preview_api.py -q
```

Manual smoke:

1. Import `GS-12-1507 RA Coplanar Rev7 (3).docx`.
2. Select group 9.
3. Confirm `Item/Section Notes` shows:
   - `Step 2 | Section:6.5*Simultaneously measure power contact resistance.`
   - `Step 5 | Section:6.6*Simultaneously measure power contact resistance.`

## 6. Acceptance Gate

Do not implement until user explicitly approves this plan.
