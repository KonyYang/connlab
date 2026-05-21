# TASK_252CK Plan - Matrix Editor Step Notes Payload Wiring And Concise Item/Section

## 0. Protocol Snapshot

- Current phase: `Phase 11 - Project Workbench / Matrix / Approval Package controlled foundation`
- Current active task: `TASK_252CK_MATRIX_EDITOR_STEP_NOTES_PAYLOAD_WIRING_AND_CONCISE_ITEM_SECTION` (planned, awaiting approval)
- Why allowed now: user reported concrete display mismatch and requested target UI output format.

## 1. Task Understanding

1. Goal:
   - Make Step preview note cards show imported note payload content, and simplify Item/Section note line.
2. Input:
   - `MatrixPreviewResponse` from import preview API.
   - Selected group + computed step rows in editor.
3. Output:
   - Step Notes card with actual note text.
   - Item/Section Notes card with concise `Step N | Section:...` lines.
4. Modules:
   - `MatrixEditorWorkspace.tsx` (+ optional API typing and frontend shell tests).
5. Forbidden:
   - No backend parser/API redesign, no scope expansion.

## 2. Current Root Cause

- Frontend currently reconstructs notes locally from marker presence:
  - `sourceStepNote` uses `Step ${stepNo}${marker}`
  - `sourceItemSectionNote` uses `Section: ${row.section}${marker}`
- It does not consume imported payload note body text (`source_note`, `source_item_section_note`, `sample_note`), so parser-side improvements are not reflected in UI.

## 3. Design

### 3.1 Data Wiring

- Keep existing editable-step generation path.
- Add a note lookup map built from `importPreview.groups[].steps[]` for current selected group:
  - keyed by `(stepNo, marker)` with fallback to `(stepNo)` when unique.
- During Step preview card composition:
  - `Step Notes` prefer mapped payload `source_note`; fallback to local marker text only if payload missing.
  - `Item/Section Notes` prefer mapped payload `source_item_section_note`; then apply concise formatter.
- `Samples Notes` prefer imported `sample_note` for selected group; fallback to marker literal if no payload.

### 3.2 Concise Formatting Rule

- Convert verbose Item/Section text to:
  - `Step {n} | Section:{section-plus-note-text}`
- Drop `Test Item:` fragment from this card by default.

### 3.3 Files

1. `frontend/src/features/matrix-editor/MatrixEditorWorkspace.tsx`
   - add preview-note lookup helpers
   - update selected-group notes derivation
   - add concise formatter for item/section note text
2. `tests/unit/test_frontend_shell_files.py`
   - add/update static assertions for new note derivation and concise line format
3. `frontend/src/api/client.ts`
   - only if typing adjustment is required (expected minimal/no change)

## 4. Risks and Mitigations

1. Risk: step dedup/renumber in editor can break direct payload alignment.
   - Mitigation: use `(stepNo, marker)` matching first; fallback to step number only.
2. Risk: payload absent when user edits matrix manually without import.
   - Mitigation: keep existing local marker-based fallback.
3. Risk: over-trimming item/section text removes useful context.
   - Mitigation: only remove `Test Item:` segment; keep `Section:` + note text intact.

## 5. Validation Plan

```powershell
py -m pytest tests\unit\test_frontend_shell_files.py -q -k "matrix_editor and note"
```

```powershell
cd frontend
npm run build
```

Manual smoke:

1. Import matrix doc with section marker note (e.g., `6.5* ...`).
2. Confirm Step Notes card shows full note body.
3. Confirm Item/Section Notes shows concise `Step N | Section:...` line only.

## 6. Acceptance Gate

Do not implement until user explicitly approves this plan.
